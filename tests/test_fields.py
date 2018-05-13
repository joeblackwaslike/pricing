import attr

from pricing.interfaces import ICurrencyFormat
from pricing.formats import CurrencyFormat
from pricing import fields, Price

import unittest


@attr.s
class Fixture:
    name: str = attr.ib(default='test-name')
    price: Price = fields.price()


class TestFields(unittest.TestCase):
    def makeOne(self, **kwargs):
        return Fixture(**kwargs)

    def test_correct_attrs_field(self):
        fix = self.makeOne()

        self.assertIsInstance(fix, Fixture)
        self.assertEqual(fix.name, 'test-name')
        self.assertEqual(fix.price, Price.parse('USD 0.00'))
        self.assertEqual(fix.price.format(), '$0.00')

    def test_incorrect_attrs_field(self):
        with self.assertRaises(ValueError):
            fix = self.makeOne(price='two')

    def test_incorrect_currency_formats(self):
        bad_codes = ['BT', 'usd', 'UsD', '4ff', 432, '$23', 'btcd']
        for code in bad_codes:
            with self.assertRaises((ValueError, TypeError)):
                cf = CurrencyFormat('test', code, '$')
