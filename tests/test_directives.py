import unittest

from zope.configuration import xmlconfig
from zope.component import queryUtility

from pricing.interfaces import (
    IPrice, ICurrencyFormat, IExchange, IExchangeBackend)
from pricing.formats import CurrencyFormat
from pricing.exchange import Exchange, CoinBaseBackend


class DirectivesTest(unittest.TestCase):
    def setUp(self):
        super(DirectivesTest, self).setUp()
        self.context = xmlconfig.file('test.zcml', __import__('tests'))

    def test_format_directives(self):
        for code in ['BTC', 'LTC', 'ETH']:
            self.assertIsInstance(
                queryUtility(ICurrencyFormat, name=code), CurrencyFormat
            )

    def test_exchange(self):
        exchange = queryUtility(IExchange)
        self.assertIsInstance(exchange, Exchange)
        self.assertIsInstance(exchange._backend, CoinBaseBackend)
        self.assertEqual(exchange._backend.base, 'USD')
