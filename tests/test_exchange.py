# -*- coding: utf-8 -*-
"""
Price exchange unittests
"""

from copy import deepcopy
from decimal import Decimal
import unittest

from zope.component import queryUtility, provideUtility

from pricing import Price, XPrice
from pricing.interfaces import IExchange
from pricing.exchange import SimpleBackend, Exchange
from pricing.exceptions import ExchangeBackendNotInstalled, ExchangeRateNotFound


class TestExchangeRatesSetup(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange()

    def test_register(self):
        self.assertFalse(self.exchange)
        self.assertIsNone(self.exchange.backend_name)
        self.exchange._backend = SimpleBackend('USD')
        self.assertEqual(self.exchange.backend_name, 'SimpleBackend')

    def test_register_class(self):
        self.assertFalse(self.exchange)
        self.assertIsNone(self.exchange.backend_name)
        self.exchange._backend = SimpleBackend('USD')
        self.assertEqual(self.exchange.backend_name, 'SimpleBackend')

    def test_register_instance(self):
        self.assertFalse(self.exchange)
        self.assertIsNone(self.exchange.backend_name)
        self.exchange._backend = SimpleBackend('USD')
        self.assertEqual(self.exchange.backend_name, 'SimpleBackend')

    def test_unregister(self):
        self.exchange._backend = SimpleBackend('USD')
        self.assertEqual(self.exchange.backend_name, 'SimpleBackend')
        self.exchange._backend = None
        self.assertFalse(self.exchange)
        self.assertIsNone(self.exchange.backend_name)

    def test_no_backend_name(self):
        self.assertIsNone(self.exchange.backend_name)

    def test_no_backend_base(self):
        with self.assertRaises(ExchangeBackendNotInstalled):
            self.exchange.base

    def test_no_backend_get_rate(self):
        with self.assertRaises(ExchangeBackendNotInstalled):
            self.exchange.rate('XXX')

    def test_no_backend_get_quotation(self):
        with self.assertRaises(ExchangeBackendNotInstalled):
            self.exchange.quotation('XXX', 'YYY')

    def test_multiple_xrates(self):
        self.exchange = Exchange(backend=SimpleBackend('XXX'))
        self.assertTrue(self.exchange)
        self.exchange.setrate('AAA', Decimal('2'))
        another = Exchange(backend=SimpleBackend('XXX'))
        self.assertTrue(another)
        another.setrate('AAA', Decimal('100'))

        self.assertEqual(self.exchange.rate('AAA'), Decimal('2'))
        self.assertEqual(another.rate('AAA'), Decimal('100'))


class TestSimpleBackend(unittest.TestCase):
    def setUp(self):
        self.exchange = Exchange(backend=SimpleBackend('XXX'))
        self.exchange.setrate('AAA', Decimal('2'))
        self.exchange.setrate('BBB', Decimal('8'))
        provideUtility(self.exchange, IExchange)

    def test_base_property(self):
        self.assertEqual(self.exchange.base, 'XXX')

    def test_rate(self):
        self.assertEqual(self.exchange.rate('XXX'), Decimal('1'))
        self.assertEqual(self.exchange.rate('AAA'), Decimal('2'))
        self.assertEqual(self.exchange.rate('BBB'), Decimal('8'))

    def test_quotation(self):
        self.assertEqual(self.exchange.quotation('XXX', 'XXX'), Decimal('1'))
        self.assertEqual(self.exchange.quotation('XXX', 'AAA'), Decimal('2'))
        self.assertEqual(self.exchange.quotation('XXX', 'BBB'), Decimal('8'))
        self.assertEqual(self.exchange.quotation('AAA', 'XXX'), Decimal('0.5'))
        self.assertEqual(self.exchange.quotation('AAA', 'AAA'), Decimal('1'))
        self.assertEqual(self.exchange.quotation('AAA', 'BBB'), Decimal('4'))
        self.assertEqual(self.exchange.quotation('BBB', 'XXX'), Decimal('0.125'))
        self.assertEqual(self.exchange.quotation('BBB', 'AAA'), Decimal('0.25'))
        self.assertEqual(self.exchange.quotation('BBB', 'BBB'), Decimal('1'))

    def test_unavailable_rate_returns_none(self):
        self.assertIsNone(self.exchange.rate('ZZZ'))

    def test_unavailable_quotation_returns_none(self):
        self.assertIsNone(self.exchange.quotation('YYY', 'ZZZ'))

    def test_price_conversion(self):
        self.assertEqual(Price('10', 'AAA').to('BBB'), Price('40', 'BBB'))
        self.assertEqual(Price('10', 'BBB').to('AAA'), Price('2.5', 'AAA'))

    def test_base_not_set_warning(self):
        self.exchange._backend.base = None
        with self.assertRaises(Warning):
            self.exchange.setrate('AAA', Decimal('2'))


class ConversionMixin(object):
    def test_unavailable_backend_conversion_error(self):
        exchange = Exchange()
        provideUtility(exchange, IExchange)
        with self.assertRaises(ExchangeBackendNotInstalled):
            self.PriceClass('2', 'AAA').to('BBB')

    def test_unavailable_rate_conversion_error(self):
        exchange = Exchange(backend=SimpleBackend('AAA'))
        provideUtility(exchange, IExchange)
        with self.assertRaises(ExchangeRateNotFound):
            self.PriceClass('2', 'AAA').to('BBB')


class TestPriceConversion(ConversionMixin, unittest.TestCase):
    PriceClass = Price

class TestXPriceConversion(ConversionMixin, unittest.TestCase):
    PriceClass = XPrice
