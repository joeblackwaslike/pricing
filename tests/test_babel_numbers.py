from pricing.babel_numbers import format_currency
from babel.core import Locale

import unittest


class TestBabelNumbers(unittest.TestCase):
    def test_format_currency(self):
        self.assertEqual(
            format_currency('42.23423432', 'USD', format="¤#,##0.########",
                            currency_digits=True, decimal_quantization=False),
            '$42.23423432')

        self.assertEqual(
            format_currency('42.23423432', 'BTC', format="₿#,##0.########",
                            currency_digits=False, decimal_quantization=False),
            '\u20bf42.23423432')

        self.assertEqual(
            format_currency('42.23', 'BTC', format="₿#,##0.########",
                            currency_digits=False, decimal_quantization=True),
            '\u20bf42.23')

        self.assertEqual(
            format_currency('42.23423432', 'USD', currency_digits=True,
                            decimal_quantization=True),
            '$42.23')

        self.assertEqual(
            format_currency('42.23423432', 'USD', currency_digits=True,
                            decimal_quantization=True),
            '$42.23')

        locale = Locale('en_US')
        self.assertEqual(
            format_currency('42.23423432', 'USD', locale=locale,
                            currency_digits=True, decimal_quantization=True),
            '$42.23')
