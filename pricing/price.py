"""
pricing.price
~~~~~~~~~~~

Classes representing Price.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

from decimal import Decimal
import re

from zope.interface import implementer
from zope.component import queryUtility
import attr
from attr.validators import instance_of

import babel
from . import babel_numbers
from .interfaces import IPrice, IExchange, ICurrencyFormat
from .exceptions import (
    CurrencyMismatch, ExchangeRateNotFound, InvalidOperandType)


LC_NUMERIC = babel.default_locale('LC_NUMERIC')

__all__ = ['LC_NUMERIC', 'Price', 'XPrice']


def sub_symbols(pattern, code, symbol):
    """Substitutes symbols in CLDR number pattern."""
    return pattern.replace('¤¤', code).replace('¤', symbol)


def amount_converter(obj):
    """Converts amount value from several types into Decimal."""
    if isinstance(obj, Decimal):
        return obj
    elif isinstance(obj, (str, int, float)):
        return Decimal(str(obj))
    else:
        raise ValueError('do not know how to convert: {}'.format(type(obj)))


@implementer(IPrice)
@attr.s(frozen=True, hash=False, cmp=False, repr=False)
class Price:
    """Price class with a amount and ISO4217 currency code.

    :param amount Decimal:
        Amount of units for price. Converts from (str, int, float).
    :param currency str: A ISO4217 currency code.
    :return: a Price object.
    :rtype: :inst:`Price`

    Usage::

        >>> Price('32.09', 'USD')
        USD 32.09
        ... Price('234.242335', 'BTC').format()
        BTC 234.242335
    """

    amount: Decimal = attr.ib(
        default='0.00',
        converter=amount_converter,
        validator=instance_of(Decimal))
    currency: str = attr.ib(
        default='USD',
        validator=[
            instance_of(str)
        ])

    @currency.validator
    def validate_currency(self, attribute, value):
        if not bool(re.compile(r'^[A-Z]{3}$').match(value)):
            raise ValueError('Invalid currency: {}'.format(value))

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __repr__(self):
        return "{} {}".format(self.currency, self.amount)

    def __str__(self):
        return u'{} {:,f}'.format(self.currency, self.amount)

    def __lt__(self, other):
        if not isinstance(other, Price):
            raise InvalidOperandType(other, '<')
        elif other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency, '<')
        else:
            return self.amount < other.amount

    def __le__(self, other):
        if not isinstance(other, Price):
            raise InvalidOperandType(other, '<=')
        elif other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency, '<=')
        else:
            return self.amount <= other.amount

    def __eq__(self, other):
        if isinstance(other, Price):
            return ((self.amount == other.amount) and
                    (self.currency == other.currency))
        return False

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if not isinstance(other, Price):
            raise InvalidOperandType(other, '>')
        elif other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency, '>')
        else:
            return self.amount > other.amount

    def __ge__(self, other):
        if not isinstance(other, Price):
            raise InvalidOperandType(other, '>=')
        elif other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency, '>=')
        else:
            return self.amount >= other.amount

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        """
        Considering Price a numeric type (on ``amount``):

        bool(Price(2, 'XXX')) --> True
        bool(Price(0, 'XXX')) --> False
        """
        return bool(self.amount)

    def __add__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise CurrencyMismatch(self.currency, other.currency, '+')
            other = other.amount
        amount = self.amount + other
        return self.__class__(amount, self.currency)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise CurrencyMismatch(self.currency, other.currency, '-')
            other = other.amount
        amount = self.amount - other
        return self.__class__(amount, self.currency)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, Price):
            raise TypeError("multiplication is unsupported between "
                            "two price objects")
        amount = self.amount * other
        return self.__class__(amount, self.currency)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise CurrencyMismatch(self.currency, other.currency, '/')
            elif other.amount == 0:
                raise ZeroDivisionError()
            return self.amount / other.amount
        else:
            if other == 0:
                raise ZeroDivisionError()
            amount = self.amount / other
            return self.__class__(amount, self.currency)

    def __floordiv__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise CurrencyMismatch(self.currency, other.currency, '//')
            elif other.amount == 0:
                raise ZeroDivisionError()
            return self.amount // other.amount
        else:
            if other == 0:
                raise ZeroDivisionError()
            amount = self.amount // other
            return self.__class__(amount, self.currency)

    def __mod__(self, other):
        if isinstance(other, Price):
            raise TypeError("modulo is unsupported between two '{}' "
                            "objects".format(self.__class__.__name__))
        if other == 0:
            raise ZeroDivisionError()
        amount = self.amount % other
        return self.__class__(amount, self.currency)

    def __divmod__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise CurrencyMismatch(self.currency, other.currency, 'divmod')
            elif other.amount == 0:
                raise ZeroDivisionError()
            return divmod(self.amount, other.amount)
        else:
            if other == 0:
                raise ZeroDivisionError()
            whole, remainder = divmod(self.amount, other)
            return (self.__class__(whole, self.currency),
                    self.__class__(remainder, self.currency))

    def __pow__(self, other):
        if isinstance(other, Price):
            raise TypeError("power operator is unsupported between two '{}' "
                            "objects".format(self.__class__.__name__))
        amount = self.amount ** other
        return self.__class__(amount, self.currency)

    def __neg__(self):
        return self.__class__(-self.amount, self.currency)

    def __pos__(self):
        return self.__class__(+self.amount, self.currency)

    def __abs__(self):
        return self.__class__(abs(self.amount), self.currency)

    def __int__(self):
        return int(self.amount)

    def __float__(self):
        return float(self.amount)

    def __round__(self, ndigits=0):
        return self.__class__(round(self.amount, ndigits), self.currency)

    def __composite_values__(self):
        return self.amount, self.currency

    def to(self, currency):
        """Return equivalent price object in another currency"""
        if currency == self.currency:
            return self
        exchange = queryUtility(IExchange)
        rate = exchange.quotation(self.currency, currency)
        if rate is None:
            raise ExchangeRateNotFound(
                exchange.backend_name, self.currency, currency)
        amount = self.amount * rate
        return self.__class__(amount, currency)

    def format(self, locale=LC_NUMERIC, pattern=None, format_type='standard',
               **kwargs):
        """Return a locale-aware, currency-formatted string.

        This method emulates babel.numbers.format_currency().

        A specific locale identifier (language[_territory]) can be passed,
        otherwise the system's default locale will be used. A custom
        formatting pattern of the form "¤#,##0.00;(¤#,##0.00)"
        (positive[;negative]) can also be passed, otherwise it will be
        determined from the locale and the CLDR (Unicode Common Locale Data
        Repository) included with Babel.

        >>> m = Price('1234.567', 'EUR')
        >>> m.format() # assuming the system's locale is 'en_US'
        €1,234.57
        >>> m.format('de_DE') # German formatting
        1.234,57 €
        >>> m.format('de', '#,##0 ¤') # German formatting (short), no cents
        1.235 €
        >>> m.format(pattern='#,##0.00 ¤¤¤') # Default locale, full name
        1,235.57 euro

        Learn more about this formatting syntaxis at:
        http://www.unicode.org/reports/tr35/tr35-numbers.html
        """

        currency_format = queryUtility(ICurrencyFormat, name=self.currency)
        if currency_format:
            format = sub_symbols(pattern or currency_format.format,
                                 currency_format.code, currency_format.symbol)
            # format = (pattern or currency_format.format).replace(
            #     '¤¤', currency_format.code).replace(
            #         '¤', currency_format.symbol)
            kwargs.setdefault('format', format)
            kwargs.setdefault(
                'currency_digits', currency_format.currency_digits)
            kwargs.setdefault(
                'decimal_quantization', currency_format.decimal_quantization)
        return babel_numbers.format_currency(
            self.amount, self.currency, locale=locale, format_type=format_type,
            **kwargs)

    @classmethod
    def parse(cls, s):
        """Parse from a string representation (repr)"""
        try:
            s = s.replace(',', '')
            currency, amount = s.strip().split(' ')
            return cls(amount, currency)
        except ValueError as err:
            raise ValueError(
                "failed to parse string '{}': {}".format(s, err)) from None


@implementer(IPrice)
@attr.s(frozen=True, hash=False, cmp=False, repr=False)
class XPrice(Price):
    """Price subclass with implicit currency conversion"""

    def __add__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__add__(other)

    def __sub__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__sub__(other)

    def __div__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__div__(other)

    def __truediv__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__floordiv__(other)

    def __divmod__(self, other):
        if isinstance(other, Price):
            other = other.to(self.currency)
        return super(XPrice, self).__divmod__(other)
