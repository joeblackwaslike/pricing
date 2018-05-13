# -*- coding: utf-8 -*-
"""
XPrice class unittests
"""

from decimal import Decimal
import unittest

from zope.component import provideUtility
from pricing import XPrice
from pricing.exceptions import CurrencyMismatch
from pricing.interfaces import IExchange
from pricing.exchange import SimpleBackend, Exchange

from . import mixins


class TestXPriceInstantiation(mixins.InstantiationMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = XPrice


class TestXPriceClass(mixins.ClassMixin, unittest.TestCase):
    def setUp(self):
        self.price = XPrice('2.99', 'XXX')


class TestXPriceRepresentations(mixins.RepresentationsMixin, unittest.TestCase):
    def setUp(self):
        self.price = XPrice('1234.567', 'XXX')


class TestXPriceFormatting(mixins.FormattingMixin, unittest.TestCase):
    def setUp(self):
        self.price = XPrice('-1234.567', 'USD')


class TestXPriceParser(mixins.ParserMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = XPrice


class TestXPriceNumericOperations(mixins.NumericOperationsMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exchange = Exchange(backend=SimpleBackend('XXX'))
        provideUtility(cls.exchange, IExchange)
        cls.exchange.setrate('AAA', Decimal('2'))
        cls.exchange.setrate('BBB', Decimal('8'))

    @classmethod
    def tearDownClass(cls):
        del cls.exchange

    def setUp(self):
        self.PriceClass = XPrice
        self.x = XPrice('10', 'XXX')
        self.a = XPrice('10', 'AAA')
        self.b = XPrice('10', 'BBB')
        self.ax = XPrice('20', 'AAA')
        self.bx = XPrice('80', 'BBB')

    def test_add_price_different_currency(self):
        self.assertEqual(self.a + self.b, XPrice('12.5', 'AAA'))
        self.assertEqual(self.b + self.a, XPrice('50', 'BBB'))

    def test_sub_price_different_currency(self):
        self.assertEqual(self.a - self.b, XPrice('7.5', 'AAA'))
        self.assertEqual(self.b - self.a, XPrice('-30', 'BBB'))

    def test_truediv_price_different_currency(self):
        self.assertEqual(self.a / self.b, Decimal('4'))
        self.assertEqual(self.b / self.a, Decimal('0.25'))

    def test_floordiv_price_different_currency(self):
        self.assertEqual(self.a // self.b, Decimal('4'))
        self.assertEqual(self.b // self.a, Decimal('0'))

    def test_divmod_price_different_currency(self):
        whole, remainder = divmod(self.a, self.b)
        self.assertEqual(whole, Decimal('4'))
        self.assertEqual(remainder, Decimal('0'))
        whole, remainder = divmod(self.b, self.a)
        self.assertEqual(whole, Decimal('0'))
        self.assertEqual(remainder, Decimal('10'))


class TestXPriceUnaryOperationsReturnNew(mixins.UnaryOperationsReturnNewMixin, unittest.TestCase):
    def setUp(self):
        self.price = XPrice('2.99', 'XXX')


class TestXPriceLeftmostTypePrevails(mixins.LeftmostTypePrevailsMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = XPrice
        self.price = self.PriceClass('2.99', 'XXX')
        self.PriceSubclass = type('PriceSubclass', (self.PriceClass,), {})
        self.other_price = self.PriceSubclass('2.99', 'XXX')
