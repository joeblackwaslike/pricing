"""
pricing
~~~~~

Pricing classes and tools with CLDR-backed locale-aware formatting and
currency exchange.  Easy to extend/customize since it's built on ZCA.

Define your custom currencies and exchange's in your project's ZCML
and you're golden.

Usage::

    >>> from pricing import Price
    ... Price('2.22', 'USD')
    EUR 2.22

    >>> Price('2.34223434', 'BTC')
    BTC 2.34223434

    >>> p = Price(2, 'USD')
    ... p.amount
    Decimal('2')
    ... p.currency
    'USD'

    >>> p = Price('2.22', 'EUR')
    ... p / 2
    EUR 1.11
    >>> p + Price('7.77', 'EUR')
    EUR 9.99
"""

__version__ = '1.0.1'
__title__ = 'pricing'
__all__ = [
    'exceptions',
    'interfaces',
    'exchange',
    'price',
    'fields',
    'range',
    'Price',
    'XPrice',
    'SimpleBackend',
    'CoinBaseBackend',
    'Exchange',
    'PriceRange'
    ]


from zope.configuration import xmlconfig

from . import exceptions, interfaces, exchange, price, fields, range
from .price import Price, XPrice
from .exchange import SimpleBackend, CoinBaseBackend, Exchange
from .range import PriceRange


xmlconfig.file('configure.zcml', __import__('sys').modules[__name__])
