# -*- coding: utf-8 -*-
"""
Price unittests as mixins for Price and subclasses
"""

import abc
from decimal import Decimal, InvalidOperation
import collections
import unittest
import pickle
import babel

from pricing import Price, XPrice
from pricing.exceptions import InvalidOperandType, CurrencyMismatch


class InstantiationMixin(object):
    def test_new_instance_int_amount(self):
        self.assertEqual(self.PriceClass(0, 'XXX').amount, Decimal('0.00'))
        self.assertEqual(self.PriceClass(2, 'XXX').amount, Decimal('2.00'))

    def test_new_instance_decimal_amount(self):
        self.assertEqual(self.PriceClass(Decimal('0.00'), 'XXX').amount, Decimal('0.00'))
        self.assertEqual(self.PriceClass(Decimal('2.99'), 'XXX').amount, Decimal('2.99'))

    def test_new_instance_float_amount(self):
        self.assertEqual(self.PriceClass(0.0, 'XXX').amount, Decimal('0.00'))
        self.assertAlmostEqual(self.PriceClass(2.99, 'XXX').amount, Decimal('2.99'))

    def test_new_instance_str_amount(self):
        self.assertEqual(self.PriceClass('0', 'XXX').amount, Decimal('0.00'))
        self.assertEqual(self.PriceClass('2.99', 'XXX').amount, Decimal('2.99'))

    def test_invalid_currency_false(self):
        with self.assertRaises((ValueError, TypeError)):
            self.PriceClass('2.99', False)

    def test_invalid_currency_empty(self):
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', '')

    def test_invalid_currency_code(self):
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', 'XX')
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', '123')
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', 'xxx')
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', '$')
        with self.assertRaises(ValueError):
            self.PriceClass('2.99', 'US$')

    def test_invalid_amount(self):
        with self.assertRaises(InvalidOperation):
            self.PriceClass('twenty', 'XXX')


class ClassMixin(object):
    def test_is_price(self):
        self.assertIsInstance(self.price, Price)

    def test_immutable_by_convention(self):
        with self.assertRaises(AttributeError):
            self.price.amount += 1
        with self.assertRaises(AttributeError):
            self.price.currency = 'YYY'

    def test_hashable(self):
        self.assertIsInstance(self.price, collections.Hashable)

    def test_hash_eq(self):
        price_set = set([self.price, self.price])
        self.assertEqual(len(price_set), 1)

    def test_hash_int(self):
        self.assertEqual(type(hash(self.price)), int)

    def test_pickable(self):
        self.assertEqual(pickle.loads(pickle.dumps(self.price)), self.price)

    def test_sqlalchemy_composite_values(self):
        self.assertEqual((self.price.amount, self.price.currency), self.price.__composite_values__())


class RepresentationsMixin(object):
    def test_repr(self):
        self.assertEqual(repr(self.price), 'XXX 1234.567')

    def test_str(self):
        self.assertEqual(str(self.price), 'XXX 1,234.567')


# RADAR: Python2 (unicode strings u'')
class FormattingMixin(object):
    def test_custom_format_padding(self):
        self.assertEqual(self.price.format('en_US', format=u'¤000000.00'), u'-$001234.57')

    def test_custom_format_custom_negative(self):
        self.assertEqual(self.price.format('en_US', format=u'¤#,##0.00;<¤#,##0.00>'), u'<$1,234.57>')

    def test_custom_format_grouping(self):
        self.assertEqual(self.price.format('en_US', format=u'¤#,##0.00'), u'-$1,234.57')
        self.assertEqual(self.price.format('de_DE', format=u'#,##0.00 ¤'), u'-1.234,57 $')
        self.assertEqual(self.price.format('en_US', format=u'¤0.00'), u'-$1234.57')
        self.assertEqual(self.price.format('de_DE', format=u'0.00 ¤'), u'-1234,57 $')

    def test_custom_format_decimals(self):
        self.assertEqual(self.price.format('en_US', format=u'¤0.000', currency_digits=False), u'-$1234.567')
        self.assertEqual(self.price.format('en_US', format=u'¤0', currency_digits=False), u'-$1235')

    def test_auto_format_locales(self):
        self.assertEqual(self.price.format('en_US'), u'-$1,234.57')
        self.assertEqual(self.price.format('de_DE'), u'-1.234,57\xa0$')
        self.assertEqual(self.price.format('es_CO'), u'-US$\xa01.234,57')

    def test_auto_format_locales_alias(self):
        self.assertEqual(self.price.format('en'), self.price.format('en_US'))
        self.assertEqual(self.price.format('de'), self.price.format('de_DE'))

    def test_auto_format_locale_numeric(self):
        locale = babel.default_locale('LC_NUMERIC')
        babel_formatted = babel.numbers.format_currency(self.price.amount, self.price.currency, locale=locale)
        self.assertEqual(self.price.format(), babel_formatted)

    def test_auto_format(self):
        babel_formatted = babel.numbers.format_currency(self.price.amount, self.price.currency)
        self.assertEqual(self.price.format(), babel_formatted)


class ParserMixin(object):
    def test_loads_repr(self):
        self.assertEqual(self.PriceClass.parse('XXX 2.99'), self.PriceClass('2.99', 'XXX'))

    def test_loads_missing_currency(self):
        with self.assertRaises(ValueError):
            self.PriceClass.parse('2.99')

    def test_loads_reversed_order(self):
        with self.assertRaises(InvalidOperation):
            self.PriceClass.parse('2.99 XXX')

    def test_loads_empty(self):
        with self.assertRaises(ValueError):
            self.PriceClass.parse('')


class NumericOperationsMixin(object):
    def test_lt(self):
        self.assertTrue(self.PriceClass('2.219', 'XXX') < self.PriceClass('2.99', 'XXX'))
        self.assertTrue(self.PriceClass('-2.99', 'XXX') < self.PriceClass('2.99', 'XXX'))
        self.assertFalse(self.PriceClass('0', 'XXX') < self.PriceClass('0', 'XXX'))

    def test_lt_works_only_with_price(self):
        with self.assertRaises(InvalidOperandType):
            self.PriceClass(0, 'XXX') < Decimal('0')

    def test_lt_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') < self.PriceClass(2, 'BBB')

    def test_le(self):
        self.assertTrue(self.PriceClass('2.219', 'XXX') <= self.PriceClass('2.99', 'XXX'))
        self.assertTrue(self.PriceClass('-2.99', 'XXX') <= self.PriceClass('2.99', 'XXX'))
        self.assertTrue(self.PriceClass('0', 'XXX') <= self.PriceClass('0', 'XXX'))
        self.assertTrue(self.PriceClass('2.990', 'XXX') <= self.PriceClass('2.99', 'XXX'))

    def test_le_works_only_with_price(self):
        with self.assertRaises(InvalidOperandType):
            self.PriceClass(0, 'XXX') <= Decimal('0')

    def test_le_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') <= self.PriceClass(2, 'BBB')

    def test_eq(self):
        self.assertEqual(self.PriceClass('2', 'XXX'), self.PriceClass('2', 'XXX'))
        self.assertEqual(hash(self.PriceClass('2', 'XXX')), hash(self.PriceClass('2', 'XXX')))

        self.assertEqual(self.PriceClass('2.99000', 'XXX'), self.PriceClass('2.99', 'XXX'))
        self.assertEqual(hash(self.PriceClass('2.99000', 'XXX')), hash(self.PriceClass('2.99', 'XXX')))

    def test_ne(self):
        self.assertNotEqual(self.PriceClass('0', 'XXX'), self.PriceClass('2', 'XXX'))
        self.assertNotEqual(hash(self.PriceClass('0', 'XXX')), hash(self.PriceClass('2', 'XXX')))

        self.assertNotEqual(self.PriceClass('2.99001', 'XXX'), self.PriceClass('2.99', 'XXX'))
        self.assertNotEqual(hash(self.PriceClass('2.99001', 'XXX')), hash(self.PriceClass('2.99', 'XXX')))

        self.assertNotEqual(self.PriceClass('2', 'XXX'), self.PriceClass('2', 'YYY'))
        self.assertNotEqual(hash(self.PriceClass('2', 'XXX')), hash(self.PriceClass('2', 'YYY')))

    def test_ne_if_not_price(self):
        self.assertNotEqual(self.PriceClass(0, 'XXX'), Decimal('0'))

    def test_gt(self):
        self.assertTrue(self.PriceClass('2.99', 'XXX') > self.PriceClass('2.219', 'XXX'))
        self.assertTrue(self.PriceClass('2.99', 'XXX') > self.PriceClass('-2.99', 'XXX'))
        self.assertFalse(self.PriceClass('0', 'XXX') > self.PriceClass('0', 'XXX'))

    def test_gt_works_only_with_price(self):
        with self.assertRaises(InvalidOperandType):
            self.PriceClass(0, 'XXX') > Decimal('0')

    def test_gt_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') > self.PriceClass(2, 'BBB')

    def test_ge(self):
        self.assertTrue(self.PriceClass('2.99', 'XXX') >= self.PriceClass('2.219', 'XXX'))
        self.assertTrue(self.PriceClass('2.99', 'XXX') >= self.PriceClass('-2.99', 'XXX'))
        self.assertTrue(self.PriceClass('2.99', 'XXX') >= self.PriceClass('2.99', 'XXX'))

    def test_ge_works_only_with_price(self):
        with self.assertRaises(InvalidOperandType):
            self.PriceClass(0, 'XXX') >= Decimal('0')

    def test_ge_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') >= self.PriceClass(2, 'BBB')

    def test_bool_true(self):
        self.assertTrue(self.PriceClass('2.99', 'XXX'))
        self.assertTrue(self.PriceClass('-1', 'XXX'))

    def test_bool_false(self):
        self.assertFalse(self.PriceClass('0', 'XXX'))

    def test_add_int(self):
        result = self.PriceClass('2', 'XXX') + 2
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_add_decimal(self):
        result = self.PriceClass('2', 'XXX') + Decimal('2')
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_add_price(self):
        result = self.PriceClass('2', 'XXX') + self.PriceClass('2', 'XXX')
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_add_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') + self.PriceClass(2, 'BBB')

    def test_add_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(0, 'XXX') + None

    def test_radd_int(self):
        result = 2 + self.PriceClass('2', 'XXX')
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_sub_int(self):
        result = self.PriceClass('2', 'XXX') - 2
        self.assertEqual(result, self.PriceClass('0', 'XXX'))

    def test_sub_decimal(self):
        result = self.PriceClass('2', 'XXX') - Decimal(2)
        self.assertEqual(result, self.PriceClass('0', 'XXX'))

    def test_sub_price(self):
        result = self.PriceClass('2', 'XXX') - self.PriceClass('2', 'XXX')
        self.assertEqual(result, self.PriceClass('0', 'XXX'))

    def test_sub_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') - self.PriceClass(2, 'BBB')

    def test_sub_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(0, 'XXX') - None

    def test_rsub_int(self):
        result = 0 - self.PriceClass('2', 'XXX')
        self.assertEqual(result, self.PriceClass('-2', 'XXX'))

    def test_mul_int(self):
        result = self.PriceClass('2', 'XXX') * 2
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_mul_decimal(self):
        result = self.PriceClass('2', 'XXX') * Decimal(2)
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_mul_price(self):
        with self.assertRaises(TypeError):
            self.PriceClass('2', 'XXX') * self.PriceClass('2', 'XXX')

    def test_mul_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(0, 'XXX') * None

    def test_rmul_int(self):
        result = 2 * self.PriceClass('2', 'XXX')
        self.assertEqual(result, self.PriceClass('4', 'XXX'))

    def test_truediv_int(self):
        result = self.PriceClass('2.99', 'XXX') / 2
        self.assertEqual(result, self.PriceClass('1.495', 'XXX'))

    def test_truediv_decimal(self):
        result = self.PriceClass('2.99', 'XXX') / Decimal(2)
        self.assertEqual(result, self.PriceClass('1.495', 'XXX'))

    def test_truediv_price(self):
        result = self.PriceClass('2', 'XXX') / self.PriceClass('2', 'XXX')
        self.assertEqual(result, Decimal('1'))

    def test_truediv_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass(2, 'AAA') / self.PriceClass(2, 'BBB')

    def test_truediv_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(2, 'XXX') / None

    def test_truediv_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.PriceClass(2, 'XXX') / 0

    def test_floordiv_number(self):
        result = self.PriceClass('2.99', 'XXX') // 2
        self.assertEqual(result, self.PriceClass('1', 'XXX'))

    def test_floordiv_price(self):
        result = self.PriceClass('2.99', 'XXX') // self.PriceClass('2', 'XXX')
        self.assertEqual(result, Decimal('1'))

    def test_floordiv_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            self.PriceClass('2.99', 'AAA') // self.PriceClass('2', 'BBB')

    def test_floordiv_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(2, 'XXX') // None

    def test_floordiv_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.PriceClass(2, 'XXX') // 0

    def test_mod_number(self):
        result = self.PriceClass('2.99', 'XXX') % 2
        self.assertEqual(result, self.PriceClass('0.99', 'XXX'))

    def test_mod_price(self):
        with self.assertRaises(TypeError):
            self.PriceClass('2.99', 'XXX') % self.PriceClass('2', 'XXX')

    def test_mod_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(2, 'XXX') % None

    def test_mod_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.PriceClass(2, 'XXX') % 0

    def test_divmod_number(self):
        whole, remainder = divmod(self.PriceClass('2.99', 'XXX'), 2)
        self.assertEqual(whole, self.PriceClass('1', 'XXX'))
        self.assertEqual(remainder, self.PriceClass('0.99', 'XXX'))

    def test_divmod_price(self):
        whole, remainder = divmod(self.PriceClass('2.99', 'XXX'), self.PriceClass('2', 'XXX'))
        self.assertEqual(whole, Decimal('1'))
        self.assertEqual(remainder, Decimal('0.99'))

    def test_divmod_price_different_currency(self):
        with self.assertRaises(CurrencyMismatch):
            divmod(self.PriceClass('2.99', 'AAA'), self.PriceClass('2', 'BBB'))

    def test_divmod_none(self):
        with self.assertRaises(TypeError):
            divmod(self.PriceClass(2, 'XXX'), None)

    def test_divmod_zero(self):
        with self.assertRaises(ZeroDivisionError):
            divmod(self.PriceClass(2, 'XXX'), 0)

    def test_pow_number(self):
        result = self.PriceClass('3', 'XXX') ** 2
        self.assertEqual(result, self.PriceClass('9', 'XXX'))

    def test_pow_price(self):
        with self.assertRaises(TypeError):
            self.PriceClass('3', 'XXX') ** self.PriceClass('2', 'XXX')

    def test_pow_none(self):
        with self.assertRaises(TypeError):
            self.PriceClass(0, 'XXX') ** None

    def test_neg(self):
        result = -self.PriceClass('2.99', 'XXX')
        self.assertEqual(result, self.PriceClass('-2.99', 'XXX'))

    def test_pos(self):
        result = +self.PriceClass('2.99', 'XXX')
        self.assertEqual(result, self.PriceClass('2.99', 'XXX'))

    def test_abs(self):
        result = abs(self.PriceClass('-2.99', 'XXX'))
        self.assertEqual(result, self.PriceClass('2.99', 'XXX'))

    def test_int(self):
        self.assertEqual(int(self.PriceClass('-2.99', 'XXX')), -2)
        self.assertEqual(int(self.PriceClass('2.99', 'XXX')), 2)

    def test_float(self):
        self.assertEqual(float(self.PriceClass('-2.99', 'XXX')), -2.99)
        self.assertEqual(float(self.PriceClass('2.99', 'XXX')), 2.99)

    def test_round_python3(self):
        self.assertEqual(round(self.PriceClass('-1.49', 'XXX')), self.PriceClass('-1', 'XXX'))
        self.assertEqual(round(self.PriceClass('1.50', 'XXX')), self.PriceClass('2', 'XXX'))
        self.assertEqual(round(self.PriceClass('1.234', 'XXX'), 2), self.PriceClass('1.23', 'XXX'))


class UnaryOperationsReturnNewMixin(object):
    def test_pos(self):
        self.assertIsNot(+self.price, self.price)

    def test_abs(self):
        self.assertIsNot(abs(self.price), self.price)

    def test_round(self):
        self.assertIsNot(round(self.price), self.price)


class LeftmostTypePrevailsMixin(object):
    def test_add(self):
        result = self.price + self.other_price
        self.assertEqual(result.__class__, self.PriceClass)

    def test_add_other(self):
        result = self.other_price + self.price
        self.assertEqual(result.__class__, self.PriceSubclass)

    def test_sub(self):
        result = self.price - self.other_price
        self.assertEqual(result.__class__, self.PriceClass)

    def test_sub_other(self):
        result = self.other_price - self.price
        self.assertEqual(result.__class__, self.PriceSubclass)
