"""
pricing.range
~~~~~~~~~~~

Represents a range in pricing.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

from zope.interface import implementer
import attr

from . import fields
from .interfaces import IPriceRange
from .price import Price


__all__ = ['PriceRange']


@implementer(IPriceRange)
@attr.s(cmp=False, frozen=True)
class PriceRange:
    """A price range."""

    start: Price = fields.price()
    stop: Price = fields.price()

    def __attrs_post_init__(self):
        if self.start.currency != self.stop.currency:
            raise ValueError(
                f'{self.start!r} and {self.stop!r} are not same currency')
        if self.start > self.stop:
            raise ValueError(
                f'Cannot create a range from {self.start!r} to {self.stop!r}')

    def __add__(self, other):
        if isinstance(other, Price):
            if other.currency != self.currency:
                raise ValueError(
                    f'Cannot add {self.currency!r} to {other.currency!r}')
            start = self.start + other
            stop = self.stop + other
            return PriceRange(start, stop)
        elif isinstance(other, PriceRange):
            if other.start.currency != self.currency:
                raise ValueError(
                    f'Cannot add {self.currency!r} and {other.currency!r}')
            start = self.start + other.start
            stop = self.stop + other.stop
            return PriceRange(start, stop)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Price):
            if other.currency != self.start.currency:
                raise ValueError(
                    f'Cannot sub {self.currency!r} to {other.currency!r}')
            start = self.start - other
            stop = self.stop - other
            return PriceRange(start, stop)
        elif isinstance(other, PriceRange):
            if other.start.currency != self.start.currency:
                raise ValueError(
                    f'Cannot sub {other.start.currency!r} to'
                    ' {self.start.currency!r}')
            start = self.start - other.start
            stop = self.stop - other.stop
            return PriceRange(start, stop)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, PriceRange):
            return (
                self.start == other.start and
                self.stop == other.stop)
        return False

    def __contains__(self, item):
        if not isinstance(item, Price):
            raise TypeError(
                f'`in price_range` requires Price as lhs not {type(item)}')
        return self.start <= item <= self.stop

    @property
    def currency(self):
        """Return the currency of the range."""
        return self.start.currency

    def evolve(self, start=None, stop=None):
        """Return a range with start or stop replaced with given values."""
        if start is None:
            start = self.start
        if stop is None:
            stop = self.stop
        return PriceRange(start=start, stop=stop)
