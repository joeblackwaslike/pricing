import unittest

from pricing.interfaces import IBIP21PaymentURI, IEIP681PaymentURI
from pricing.uris import BIP21PaymentURI, EIP681PaymentURI


class TestCurrencyFormat(unittest.TestCase):
    def test_interfaces(self):
        uri = BIP21PaymentURI(
            'bitcoin', address='19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj',
            amount='2.425222')
        self.assertTrue(IBIP21PaymentURI.providedBy(uri))

        uri = EIP681PaymentURI(
            'ethereum', address='077a7506b69e37e4f6852577190f04a35df9a36c',
            value='2.425222')
        self.assertTrue(IEIP681PaymentURI.providedBy(uri))

    def test_bip21_payment_uri(self):
        uri = BIP21PaymentURI(
            'bitcoin', address='19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj',
            amount='2.425222')
        self.assertEqual(
            str(uri),
            'bitcoin:19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj?amount=2.425222')

    def test_eip681_payment_uri(self):
        uri = EIP681PaymentURI(
            'ethereum', address='077a7506b69e37e4f6852577190f04a35df9a36c',
            value='2.425222')
        uri2 = EIP681PaymentURI(
            'ethereum', address='0x077a7506b69e37e4f6852577190f04a35df9a36c',
            value='2.425222')
        self.assertEqual(
            str(uri),
            'ethereum:0x077a7506b69e37e4f6852577190f04a35df9a36c?value=2.425222'
            )
        self.assertEqual(str(uri), str(uri2))
