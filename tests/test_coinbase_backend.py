from copy import deepcopy
from decimal import Decimal
import unittest

import zulu
from zope.component import queryUtility, provideUtility

from pricing import Price, XPrice
from pricing.interfaces import IExchange
from pricing.exchange import CoinBaseBackend, Exchange
from pricing.exceptions import ExchangeBackendNotInstalled, ExchangeRateNotFound


class TestCoinBaseBackend(unittest.TestCase):
    def test_coinbase_backend_downloads_rates(self):

        backend = CoinBaseBackend('USD')

        now = zulu.now()

        backend.refresh()

        self.assertLess(now, backend.last_updated)

        self.assertGreater(len(backend._rates), 100)
        rate = backend.rate('EUR')
        self.assertIsInstance(rate, Decimal)
        self.assertLess(rate, 1)

        rate = backend.quotation('EUR', 'CAD')
        self.assertIsInstance(rate, Decimal)
        self.assertGreater(rate, 1)
