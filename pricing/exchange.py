"""
pricing.exchange
~~~~~~~~~~~~~~

Price exchange related classes.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

from decimal import Decimal
from datetime import timedelta
import importlib
from typing import ClassVar

from zope.interface import implementer
import attr
from attr.validators import instance_of
import requests
import zulu

from .interfaces import IExchangeBackend, IExchange
from .exceptions import ExchangeBackendNotInstalled


__all__ = ['BackendBase', 'SimpleBackend', 'CoinBaseBackend', 'Exchange']


def ensure_fresh_rates(func):
    """Decorator for Backend that ensures rates are fresh within last 5 mins"""
    def wrapper(self, *args, **kwargs):
        if self.last_updated + timedelta(minutes=5) < zulu.now():
            self.refresh()
        return func(self, *args, **kwargs)
    return wrapper


class BackendBase:
    """Base class API for exchange backends"""

    def quotation(self, origin, target):
        """Return quotation between two currencies (origin, target)"""
        a = self.rate(origin)
        b = self.rate(target)
        if a and b:
            return Decimal(b) / Decimal(a)
        return None


@implementer(IExchangeBackend)
@attr.s
class SimpleBackend(BackendBase):
    """Simple Backend implementation.

    :param base str: An ISO4217 currency code.
    :return: A `SimpleBackend` object.
    :rtype: :inst:`SimpleBackend`

    Usage::

        >>> SimpleBackend(base='USD')
        SimpleBackend(base='USD')

    """

    base: str = attr.ib(default='USD', validator=instance_of(str))
    _rates: dict = attr.ib(init=False, repr=False, factory=dict,
                           validator=instance_of(dict))

    def setrate(self, currency, rate):
        """Sets the rate for currency to provided rate."""
        if not self.base:
            raise Warning("set the base first: backend.base = currency")
        self._rates[currency] = rate

    def rate(self, currency):
        """Returns the rate of exchange from base -> currency."""
        if currency == self.base:
            rate = 1
        else:
            rate = self._rates.get(currency, None)
        if rate:
            return Decimal(rate)

    def quotation(self, origin, target):
        """Returns the rate of exchange from origin -> target currency."""
        return super(SimpleBackend, self).quotation(origin, target)


@implementer(IExchangeBackend)
@attr.s
class CoinBaseBackend(BackendBase):
    """Backend implementation that uses the Coinbase API for rates.

    :param base str: An ISO4217 currency code.
    :return: An `CoinBaseBackend` object.
    :rtype: :inst:`CoinBaseBackend`

    Usage::

        >>> CoinBaseBackend(base='USD')
        CoinBaseBackend(base='USD', last_updated=<Zulu [...]>)

    """

    base: str = attr.ib(default='USD', validator=instance_of(str))

    _rates: dict = attr.ib(repr=False, init=False, factory=dict)
    _headers: ClassVar[dict] = {
        'Accept': 'application/json', 'Content-Type': 'application/json'}
    _base_url: ClassVar[str] = 'https://api.coinbase.com/v2'
    last_updated: zulu.Zulu = attr.ib(init=False)

    @last_updated.default
    def last_updated_default(self):
        now = zulu.now()
        return now - timedelta(minutes=5)

    def _rates_refresh(self, values=None):
        if values:
            base_url = values['_base_url']
            base = values['base']
            headers = values['_headers']
        else:
            base_url = self._base_url
            base = self.base
            headers = self._headers

        url = base_url + '/exchange-rates?currency={}'.format(base)
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()['data']['rates']

    def refresh(self):
        """Refresh rates and update last_updated timestamp."""
        self._rates = self._rates_refresh()
        self.last_updated = zulu.now()

    @ensure_fresh_rates
    def rate(self, currency):
        """Returns the rate of exchange from base -> currency."""
        if currency == self.base:
            rate = 1
        else:
            rate = self._rates.get(currency, None)
        if rate:
            return Decimal(rate)

    @ensure_fresh_rates
    def quotation(self, origin, target):
        """Returns the rate of exchange from origin -> target currency."""
        return super(CoinBaseBackend, self).quotation(origin, target)


@implementer(IExchange)
@attr.s
class Exchange:
    """Currency rate exchange class.

    :param _backend IExchangeBackend:
        An instance of an ExchangeBackend providing IExchangeBackend interface.
    :return: An `Exchange` object.
    :rtype: :inst:`Exchange`

    Usage::

        >>> backend = CoinBaseBackend(base='USD')
        ... exchange = Exchange(backend=backend)
        ... exchange
        Exchange(_backend=CoinBaseBackend(
        ... base='USD', last_updated=<Zulu [...]>))

        >>> exchange.rate('EUR')
        Decimal('...')
        ... exchange.quotation('EUR', 'GBP')
        Decimal('...')
    """

    _backend: IExchangeBackend = attr.ib(default=None)

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return bool(self._backend)

    def install(self, backend='pricing.exchange.SimpleBackend'):
        """Install an exchange rates backend using a python path string"""

        if isinstance(backend, str):
            path, name = backend.rsplit('.', 1)
            module = importlib.import_module(path)
            backend = getattr(module, name)()
        elif isinstance(backend, type):
            backend = backend()
        if not isinstance(backend, BackendBase):
            raise TypeError("backend '{}' is not a subclass of "
                            "pricing.exchange.BackendBase".format(backend))
        self._backend = backend

    def uninstall(self):
        """Uninstall any exchange rates backend"""
        self._backend = None

    @property
    def backend_name(self):
        """Return the class name of the currently installed backend or None."""
        if not self._backend:
            return None
        return self._backend.__class__.__name__

    @property
    def base(self):
        """Return the base currency."""
        if not self._backend:
            raise ExchangeBackendNotInstalled()
        return self._backend.base

    def rate(self, currency):
        """Returns the rate of exchange from base -> currency."""
        if not self._backend:
            raise ExchangeBackendNotInstalled()
        return self._backend.rate(currency)

    def quotation(self, origin, target):
        """Returns the rate of exchange from origin -> target currency."""
        if not self._backend:
            raise ExchangeBackendNotInstalled()
        return self._backend.quotation(origin, target)

    def __getattr__(self, key):
        return getattr(self._backend, key)

    def __setattr__(self, key, value):
        if key == '_backend':
            self.__dict__[key] = value
        elif self._backend is None:
            raise ExchangeBackendNotInstalled()
        else:
            setattr(self._backend, key, value)
