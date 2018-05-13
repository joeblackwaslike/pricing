from pricing.interfaces import ICurrencyFormat
from pricing.formats import CurrencyFormat

import unittest


class TestCurrencyFormat(unittest.TestCase):
    def test_interface(self):
        cf = CurrencyFormat('something', 'BTC', '$')
        self.assertTrue(ICurrencyFormat.providedBy(cf))

    def test_correct_currency_format(self):
        cf = CurrencyFormat('bitcoin', 'BTC', '₿', format="¤#,##0.########",
                            currency_digits=False, decimal_quantization=True)

        self.assertEqual(cf.name, 'bitcoin')
        self.assertEqual(cf.code, 'BTC')
        self.assertEqual(cf.symbol, '₿')
        self.assertEqual(cf.format, "¤#,##0.########")
        self.assertEqual(cf.currency_digits, False)
        self.assertEqual(cf.decimal_quantization, True)

    def test_incorrect_currency_formats(self):
        bad_codes = ['BT', 'usd', 'UsD', '4ff', 432, '$23', 'btcd']
        for code in bad_codes:
            with self.assertRaises((ValueError, TypeError)):
                cf = CurrencyFormat('test', code, '$')
