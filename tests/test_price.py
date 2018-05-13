# -*- coding: utf-8 -*-
"""
Price class unittests
"""
import unittest

from pricing import Price
from . import mixins


class TestPriceInstantiation(mixins.InstantiationMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = Price


class TestPriceClass(mixins.ClassMixin, unittest.TestCase):
    def setUp(self):
        self.price = Price('2.99', 'XXX')


class TestPriceRepresentations(mixins.RepresentationsMixin, unittest.TestCase):
    def setUp(self):
        self.price = Price('1234.567', 'XXX')


class TestPriceFormatting(mixins.FormattingMixin, unittest.TestCase):
    def setUp(self):
        self.price = Price('-1234.567', 'USD')


class TestPriceParser(mixins.ParserMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = Price


class TestPriceNumericOperations(mixins.NumericOperationsMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = Price


class TestPriceUnaryOperationsReturnNew(mixins.UnaryOperationsReturnNewMixin, unittest.TestCase):
    def setUp(self):
        self.price = Price('2.99', 'XXX')


class TestPriceLeftmostTypePrevails(mixins.LeftmostTypePrevailsMixin, unittest.TestCase):
    def setUp(self):
        self.PriceClass = Price
        self.price = self.PriceClass('2.99', 'XXX')
        self.PriceSubclass = type('PriceSubclass', (self.PriceClass,), {})
        self.other_price = self.PriceSubclass('2.99', 'XXX')
