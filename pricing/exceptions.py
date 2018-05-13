"""
pricing.exceptions
~~~~~~~~~~~~~~~~

Custom exception classes

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""


__all__ = [
    'PriceException',
    'CurrencyMismatch',
    'InvalidOperandType',
    'ExchangeError',
    'ExchangeBackendNotInstalled',
    'ExchangeRateNotFound'
    ]


class PriceException(Exception):
    """Generic price exception"""


class CurrencyMismatch(PriceException, ValueError):
    """Invalid operation between price objects of different currencies"""

    def __init__(self, a, b, operation):
        msg = ("unsupported operation between price in '{}' and '{}': '{}'. "
               "Use XPrice for automatic currency conversion.").format(
                   a, b, operation)
        super(CurrencyMismatch, self).__init__(msg)


class InvalidOperandType(PriceException, TypeError):
    """Invalid operation for price object types."""

    def __init__(self, operand, operation):
        msg = ("unsupported operation between Price and '{}': '{}'. This "
               "operation can only be performed with another Price object. "
               "You can access the amount of a price object 'foo'"
               " with 'foo.amount' (decimal.Decimal).").format(
                   type(operand), operation)
        super(InvalidOperandType, self).__init__(msg)


class ExchangeError(PriceException):
    """Generic exception related to exchange rates"""


class ExchangeBackendNotInstalled(ExchangeError):
    """No backend installed yet"""

    def __init__(self):
        msg = "use e.g. price.xrates.install('price.exchange.SimpleBackend')"
        super(ExchangeBackendNotInstalled, self).__init__(msg)


class ExchangeRateNotFound(ExchangeError):
    """A rate/quotation was not returned by the backend"""

    def __init__(self, backend, a, b):
        msg = ("rate not found in backend '{}': {}/{}".format(backend, a, b))
        super(ExchangeRateNotFound, self).__init__(msg)
