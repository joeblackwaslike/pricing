# -*- coding: utf-8 -*-
"""
Price doctests as unittest Suite
"""

import doctest
import unittest


FILES = (
    '../../README.rst',
)

def load_tests(loader, tests, pattern):
    return doctest.DocFileSuite(*FILES)
