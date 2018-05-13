import attr

import unittest

from pricing import Price, PriceRange
from pricing.interfaces import IPriceRange


class TestPriceRange(unittest.TestCase):
    def test_interface(self):
        m1 = Price('32.44', 'USD')
        m2 = Price('40.33', 'USD')
        mr = PriceRange(m1, m2)
        self.assertTrue(IPriceRange.providedBy(mr))

    def test_correct_price_range(self):
        m1 = Price('32.44', 'USD')
        m2 = Price('40.33', 'USD')
        mr = PriceRange(m1, m2)

        self.assertIsInstance(mr, PriceRange)
        self.assertEqual(mr.currency, 'USD')
        self.assertEqual(m1, mr.start)
        self.assertEqual(m2, mr.stop)

    def test_incorrect_price_range(self):
        with self.assertRaises(ValueError):
            mr = PriceRange('43', '23')

    def test_price_range_containment(self):
        m1 = Price('32.44', 'USD')
        m2 = Price('40.33', 'USD')
        mr = PriceRange(m1, m2)

        self.assertTrue(Price('36.00', 'USD') in mr)
        self.assertFalse(Price('50.00', 'USD') in mr)

    def test_evolve_price_range(self):
        m1 = Price('32.44', 'USD')
        m2 = Price('40.33', 'USD')
        mr = PriceRange(m1, m2)

        mr2 = mr.evolve(stop=Price('60.00', 'USD'))
        self.assertEqual(mr2.stop, Price('60.00', 'USD'))
