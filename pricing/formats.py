"""
pricing.formats
~~~~~~~~~~~~~

Custom currency format classes.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

import re

import attr
from attr.validators import instance_of, optional
from zope.interface import implementer

from .interfaces import ICurrencyFormat


__all__ = ['CurrencyFormat']


@implementer(ICurrencyFormat)
@attr.s(frozen=True)
class CurrencyFormat:
    """Represents a custom currency's formatting parameters.

    :param name str: Currency name, ex: bitcoin.
    :param code str: An ISO4217 currency code, ex: USD
    :param symbol str: A currency symbol, ex: $
    :param format str: A CLDR compatible currency format pattern.
    :param currency_digits bool: Zero pad to currency precision if True
    :param decimal_quantization bool: Decimal Quantization.
    :return: a CurrencyFormat object.
    :rtype: :inst:`CurrencyFormat`

    Usage::

        >>> BTC = CurrencyFormat(
                'bitcoin', 'BTC', symbol='₿', format="¤#,##0.########",
                currency_digits=False, decimal_quantization=True)
        ... BTC
        CurrencyFormat(name='bitcoin', code='BTC', symbol='\u20bf',
        ...            format='¤#,##0.########', currency_digits=False,
        ...            decimal_quantization=True)

    """

    name: str = attr.ib(
        validator=instance_of(str))
    code: str = attr.ib(
        validator=instance_of(str))
    symbol: str = attr.ib(
        validator=instance_of(str))
    format: str = attr.ib(
        default=None,
        validator=optional(instance_of(str)))
    currency_digits: bool = attr.ib(
        default=True,
        validator=instance_of(bool))
    decimal_quantization: bool = attr.ib(
        default=True,
        validator=instance_of(bool))

    @code.validator
    def validate_currency(self, attribute, value):
        if not bool(re.compile(r'^[A-Z]{3}$').match(value)):
            raise ValueError('Invalid currency code: {}'.format(value))
