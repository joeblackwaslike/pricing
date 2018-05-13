"""
pricing.fields
~~~~~~~~~~~~

Fields helpers for zope.schema and attrs.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""


from zope.interface import implementer
from zope.schema.interfaces import IFromUnicode
from zope.schema._field import NativeStringLine

import attr
from attr.validators import instance_of
from .price import Price as PriceClass


__all__ = ['Price', 'price']


def price_converter(obj):
    """Ensures that string prices are converted into Price objects."""
    if isinstance(obj, str):
        obj = PriceClass.parse(obj)
    return obj


@implementer(IFromUnicode)
class Price(NativeStringLine):
    """Price field for zope.schema.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('title', 'Price')
        kwargs.setdefault(
            'description', 'A price object')
        kwargs.setdefault('required', False)
        kwargs.setdefault('readonly', False)
        kwargs.setdefault('default', 'USD 0.00')
        super(Price, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(Price, self)._validate(value)

    def fromUnicode(self, value):
        """See IFromUnicode."""
        v = value.strip()
        if isinstance(v, bytes):
            v = v.decode()
        v = PriceClass.parse(value)
        self.validate(v)
        return v


def price(*args, **kwargs):
    """Price field for attrs.

    See `help(attr.ib)` for full signature.

    Usage:

        >>> from pricing import fields
        ... @attr.s
        ... class Test:
        ...     price: Price = fields.price(default='USD 5.00')
        ...
        ... Test()
        Test(price=USD 5.00)
    """

    kwargs.setdefault('default', 'USD 0.00')
    kwargs.setdefault('converter', price_converter)

    if 'validator' in kwargs:
        validator = kwargs.pop('validator')
        if not isinstance(validator, (tuple, list)):
            validator = [validator]
    else:
        validator = []
    validator.append(instance_of(PriceClass))
    return attr.ib(validator=validator, *args, **kwargs)
