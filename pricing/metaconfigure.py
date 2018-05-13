"""
pricing.metaconfigure
~~~~~~~~~~~~~~~~~~~

Custom ZCML directive processing.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

from zope.component import provideUtility
from pricing.formats import CurrencyFormat
from pricing.interfaces import ICurrencyFormat, IExchange


def _register_currency(name, code, *args):
    currency = CurrencyFormat(name, code, *args)
    provideUtility(currency, ICurrencyFormat, name=code)


def _register_exchange(name, component, backend, base):
    backend = backend(base)
    exchange = component(backend)
    provideUtility(exchange, IExchange, name=name)


class CurrencyHandler:
    """Custom XML Complex-directive Handler for Currency."""

    def __init__(self, _context, default='USD'):
        self.default = default

    def __call__(self):
        pass

    @staticmethod
    def currencyFormat(_context, code, symbol, format,
                       currency_digits=True, decimal_quantization=True,
                       name=''):
        """Handle currencyFormat subdirectives."""
        _context.action(
            discriminator=('currency', name, code),
            callable=_register_currency,
            args=(name, code, symbol, format, currency_digits,
                  decimal_quantization)
            )

    @staticmethod
    def exchange(_context, component, backend, base, name=''):
        """Handle exchange subdirectives."""
        _context.action(
            discriminator=('currency', 'exchange', component),
            callable=_register_exchange,
            args=(name, component, backend, base)
        )
