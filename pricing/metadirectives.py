"""
pricing.metadirectives
~~~~~~~~~~~~~~~~~~~~

Custom ZCML directive schemas.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

from zope.interface import Interface
from zope import schema
from zope.configuration import fields


class ICurrencyDirective(Interface):
    """Schema for Custom Currency XML directive."""

    default = schema.TextLine(
        title="Default currency",
        default='USD',
        required=False)


class ICurrencyFormatDirective(Interface):
    """Schema for Custom currencyFormat XML subdirective."""

    code = schema.TextLine(
        title="Currency code",
        required=True)
    symbol = schema.TextLine(
        title="Currency symbol",
        required=True)
    format = schema.TextLine(
        title="Currency format string",
        required=True)
    currency_digits = schema.Bool(
        title="Pad currency digits",
        default=True)
    decimal_quantization = schema.Bool(
        title="Quantize decimal",
        default=True)
    name = schema.TextLine(
        title="Currency name",
        required=True)


class IExchangeDirective(Interface):
    """Schema for Custom exchange XML subdirective."""

    component = fields.GlobalObject(
        title="Path to handler component class",
        required=True)
    backend = fields.GlobalObject(
        title="Backend name",
        required=True)
    base = schema.TextLine(
        title="Base currency for conversions",
        default='USD')
    name = schema.TextLine(
        title="Exchange name",
        default='',
        required=False)
