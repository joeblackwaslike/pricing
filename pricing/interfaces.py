# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
# pylint: disable=unexpected-special-method-signature,arguments-differ
"""
pricing.interfaces
~~~~~~~~~~~~~~~~

Various zope compatible interfaces for the price package.
"""

from zope.interface import Interface, Attribute


__all__ = [
    'ICurrencyFormat',
    'IExchangeBackend',
    'IPrice',
    'IPriceRange',
    'IExchange'
    ]


class ICurrencyFormat(Interface):
    """Formal specification for formatting a currency type."""

    name = Attribute('Name of the currency being formatted')
    code = Attribute('ISO code for currency being formatted')
    symbol = Attribute('Symbol for currency being formatted')
    currency_digits = Attribute('')
    decimal_quantization = Attribute('Quantize decimal')


class IExchangeBackend(Interface):
    """Backend provider for the Exchange, exchange-rates system."""

    base = Attribute('Base currency for exchange rates')

    def rate(currency):
        """Return the rate of exchange from the base currency to currency."""

    def quotation(origin, target):
        """Return a quotation from origin to target currency."""


class IPrice(Interface):
    """Represents a known quantity of a specific currency."""

    amount = Attribute('Currency amount for instance')
    currency = Attribute('Currency type for instance')

    def format(locale='en_US', pattern=None, format_type='standard', **kwargs):
        """Return a locale-aware, currency-formatted string."""

    def to(currency):
        """Return equivalent price object in another currency"""


class IPriceRange(Interface):
    """Represents a range between start and stop price."""

    start = Attribute('Low end of price range')
    stop = Attribute('High end of price range')
    currency = Attribute('Currency unit of range')

    def __contains__(self, item):
        """Return whether item (Price obj) is contained within range."""

    def evolve(start=None, stop=None):
        """Return new range with start or stop replaced with given values."""


class IExchange(Interface):
    """Converts between currencies and manages the exchange backend"""

    base = Attribute('Base currency for conversion.')
    backend_name = Attribute(
        'Return class name of the currently installed backend')

    def rate(currency):
        """Return quotation between the base and another currency"""

    def quotation(origin, target):
        """Return quotation between two currencies (origin, target)"""
