from decimal import Decimal

from zope.interface import implementer
import attr
from attr.validators import instance_of
from boltons.urlutils import URL

from .interfaces import IBIP21PaymentURI, IEIP681PaymentURI


@implementer(IBIP21PaymentURI)
@attr.s(repr=False, frozen=True)
class BIP21PaymentURI:
    """BIP21 Payment URI's.

    :param currency str: The currency represented by the URI, ex: bitcoin.
    :param address str: The recipient address.
    :param amount Decimal: The value/amount requested.

    Usage::

        >>> BIP21PaymentURI(
        ... 'bitcoin',
        ... address='19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj',
        ... amount='4.32345').to_uri()
        'bitcoin:19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj?amount=4.32345'
    """

    currency: str = attr.ib(
        validator=[
            instance_of(str),
            lambda i,a,v: v in ('bitcoin', 'litecoin')
        ])
    address: str = attr.ib()
    amount: Decimal = attr.ib(
        converter=Decimal,
        validator=instance_of(Decimal))

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.to_uri())

    def __str__(self):
        return str(self.to_uri())

    def to_uri(self):
        """Return a formatted BIP21 Payment URI."""
        return '{}:{}?amount={}'.format(
            self.currency, self.address, str(self.amount))

    @classmethod
    def parse_uri(cls, uri):
        """Parses a BIP21 Payment URI into this class"""
        parsed = URL(uri)
        currency = parsed.scheme
        address = parsed.path
        amount = parsed.qp['amount']
        return cls(currency, address, amount)


@implementer(IEIP681PaymentURI)
@attr.s(repr=False, frozen=True)
class EIP681PaymentURI:
    """EIP681 Payment URI's.

    :param currency str: The currency represented by the URI, ex: ethereum.
    :param address str: The recipient ethereum account address.
    :param value Decimal: The value/amount requested.

    Usage::

        >>> EIP681PaymentURI(
        ... 'ethereum',
        ... address='077a7506b69e37e4f6852577190f04a35df9a36c',
        ... value='4.32345').to_uri()
        'ethereum:0x077a7506b69e37e4f6852577190f04a35df9a36c?value=4.32345'
    """

    currency: str = attr.ib(
        validator=[
            instance_of(str),
            lambda i,a,v: v in ('ethereum',)
        ])
    address: str = attr.ib(
        converter=lambda a: a if a.startswith('0x') else '0x' + a,
        validator=lambda i,a,v: v.startswith('0x')
        )
    value: Decimal = attr.ib(
        converter=Decimal,
        validator=instance_of(Decimal))

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.to_uri())

    def __str__(self):
        return str(self.to_uri())

    def to_uri(self):
        """Return a formatted EIP681 Payment URI."""
        return '{}:{}?value={}'.format(
            self.currency, self.address, str(self.value))

    @classmethod
    def parse_uri(cls, uri):
        """Parses a EIP681 Payment URI into this class"""
        parsed = URL(uri)
        currency = parsed.scheme
        address = parsed.path
        value = parsed.qp['value']
        return cls(currency, address, value)
