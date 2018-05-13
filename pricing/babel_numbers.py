"""
pricing.babel_numbers
~~~~~~~~~~~~~~~~

Custom patches babel.numbers with improved `format_currency` function.

:copyright: (c) 2018 by Joseph Black.
:license: MIT, see LICENSE for more details.
"""

import decimal

import babel.numbers
from babel.core import Locale
from babel.numbers import NumberPattern as _NumberPattern
from babel.numbers import LC_NUMERIC, number_re, UnknownCurrencyFormatError


__all__ = ['format_currency']


def format_currency(number, currency, format=None,
                    locale=LC_NUMERIC, currency_digits=True,
                    format_type='standard', decimal_quantization=True):

    """Return formatted currency value.

    >>> format_currency(1099.98, 'USD', locale='en_US')
    u'$1,099.98'
    >>> format_currency(1099.98, 'USD', locale='es_CO')
    u'US$\\xa01.099,98'
    >>> format_currency(1099.98, 'EUR', locale='de_DE')
    u'1.099,98\\xa0\\u20ac'

    The format can also be specified explicitly.  The currency is
    placed with the '¤' sign.  As the sign gets repeated the format
    expands (¤ being the symbol, ¤¤ is the currency abbreviation and
    ¤¤¤ is the full name of the currency):

    >>> format_currency(1099.98, 'EUR', u'\xa4\xa4 #,##0.00', locale='en_US')
    u'EUR 1,099.98'
    >>> format_currency(1099.98, 'EUR', u'#,##0.00 \xa4\xa4\xa4',
    ...                 locale='en_US')
    u'1,099.98 euros'

    Currencies usually have a specific number of decimal digits. This function
    favours that information over the given format:

    >>> format_currency(1099.98, 'JPY', locale='en_US')
    u'\\xa51,100'
    >>> format_currency(1099.98, 'COP', u'#,##0.00', locale='es_ES')
    u'1.100'

    However, the number of decimal digits can be overriden from the currency
    information, by setting the last parameter to ``False``:

    >>> format_currency(1099.98, 'JPY', locale='en_US', currency_digits=False)
    u'\\xa51,099.98'
    >>> format_currency(1099.98, 'COP', u'#,##0.00', locale='es_ES',
    ...                 currency_digits=False)
    u'1.099,98'

    If a format is not specified the type of currency format to use
    from the locale can be specified:

    >>> format_currency(1099.98, 'EUR', locale='en_US', format_type='standard')
    u'\\u20ac1,099.98'

    When the given currency format type is not available, an exception is
    raised:

    >>> format_currency('1099.98', 'EUR', locale='root', format_type='unknown')
    Traceback (most recent call last):
        ...
    UnknownCurrencyFormatError: "'unknown' is not a known currency format type"

    By default the locale is allowed to truncate and round a high-precision
    number by forcing its format pattern onto the decimal part. You can bypass
    this behavior with the `decimal_quantization` parameter:

    >>> format_currency(1099.9876, 'USD', locale='en_US')
    u'$1,099.99'
    >>> format_currency(1099.9876, 'USD', locale='en_US',
    ...                 decimal_quantization=False)
    u'$1,099.9876'

    :param number: the number to format
    :param currency: the currency code
    :param format: the format string to use
    :param locale: the `Locale` object or locale identifier
    :param currency_digits: use the currency's natural number of decimal digits
    :param format_type: the currency format type to use
    :param decimal_quantization: Truncate and round high-precision numbers to
                                 the format pattern. Defaults to `True`.
    """

    locale = Locale.parse(locale)
    if format:
        pattern = parse_pattern(format)
    else:
        try:
            p = locale.currency_formats[format_type]
            pattern = NumberPattern(
                p.pattern, p.prefix, p.suffix, p.grouping, p.int_prec,
                p.frac_prec, p.exp_prec, p.exp_plus)

        except KeyError:
            raise UnknownCurrencyFormatError(
                "%r is not a known currency format type" % format_type)
    return pattern.apply(
        number, locale, currency=currency, currency_digits=currency_digits,
        decimal_quantization=decimal_quantization)


def parse_pattern(pattern):
    """Parse number format patterns"""
    if isinstance(pattern, NumberPattern):
        return pattern

    def _match_number(pattern):
        rv = number_re.search(pattern)
        if rv is None:
            raise ValueError('Invalid number pattern %r' % pattern)
        return rv.groups()

    pos_pattern = pattern

    # Do we have a negative subpattern?
    if ';' in pattern:
        pos_pattern, neg_pattern = pattern.split(';', 1)
        pos_prefix, number, pos_suffix = _match_number(pos_pattern)
        neg_prefix, _, neg_suffix = _match_number(neg_pattern)
    else:
        pos_prefix, number, pos_suffix = _match_number(pos_pattern)
        neg_prefix = '-' + pos_prefix
        neg_suffix = pos_suffix
    if 'E' in number:
        number, exp = number.split('E', 1)
    else:
        exp = None
    if '@' in number:
        if '.' in number and '0' in number:
            raise ValueError('Significant digit patterns can not contain '
                             '"@" or "0"')
    if '.' in number:
        integer, fraction = number.rsplit('.', 1)
    else:
        integer = number
        fraction = ''

    def parse_precision(p):
        """Calculate the min and max allowed digits"""
        min = max = 0
        for c in p:
            if c in '@0':
                min += 1
                max += 1
            elif c == '#':
                max += 1
            elif c == ',':
                continue
            else:
                break
        return min, max

    int_prec = parse_precision(integer)
    frac_prec = parse_precision(fraction)
    if exp:
        exp_plus = exp.startswith('+')
        exp = exp.lstrip('+')
        exp_prec = parse_precision(exp)
    else:
        exp_plus = None
        exp_prec = None
    grouping = babel.numbers.parse_grouping(integer)
    return NumberPattern(pattern, (pos_prefix, neg_prefix),
                         (pos_suffix, neg_suffix), grouping,
                         int_prec, frac_prec,
                         exp_prec, exp_plus)


class NumberPattern(_NumberPattern):
    """Overriding babel.numbers.NumberPattern.apply to newer version."""

    def apply(
            self, value, locale, currency=None, currency_digits=True,
            decimal_quantization=True):
        """Renders into a string a number following the defined pattern.
        Forced decimal quantization is active by default so we'll produce a
        number string that is strictly following CLDR pattern definitions.
        """
        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value))

        value = value.scaleb(self.scale)

        # Separate the absolute value from its sign.
        is_negative = int(value.is_signed())
        value = abs(value).normalize()

        # Prepare scientific notation metadata.
        if self.exp_prec:
            value, exp, exp_sign = self.scientific_notation_elements(
                value, locale)

        # Adjust the precision of the fractionnal part and force it to the
        # currency's if neccessary.
        frac_prec = self.frac_prec
        if currency and currency_digits:
            frac_prec = (babel.numbers.get_currency_precision(currency), ) * 2

        # Bump decimal precision to the natural precision of the number if it
        # exceeds the one we're about to use. This adaptative precision is only
        # triggered if the decimal quantization is disabled or if a scientific
        # notation pattern has a missing mandatory fractional part (as in the
        # default '#E0' pattern). This special case has been extensively
        # discussed at
        # https://github.com/python-babel/babel/pull/494#issuecomment-307649969
        if not decimal_quantization or (self.exp_prec and frac_prec == (0, 0)):
            frac_prec = (frac_prec[0], max([frac_prec[1],
                                            get_decimal_precision(value)]))

        # Render scientific notation.
        if self.exp_prec:
            number = ''.join([
                self._quantize_value(value, locale, frac_prec),
                babel.numbers.get_exponential_symbol(locale),
                exp_sign,
                self._format_int(
                    str(exp), self.exp_prec[0], self.exp_prec[1], locale)])

        # Is it a siginificant digits pattern?
        elif '@' in self.pattern:
            text = self._format_significant(value,
                                            self.int_prec[0],
                                            self.int_prec[1])
            a, sep, b = text.partition(".")
            number = self._format_int(a, 0, 1000, locale)
            if sep:
                number += babel.numbers.get_decimal_symbol(locale) + b

        # A normal number pattern.
        else:
            number = self._quantize_value(value, locale, frac_prec)

        retval = ''.join([
            self.prefix[is_negative],
            number,
            self.suffix[is_negative]])

        if u'¤' in retval:
            retval = retval.replace(u'¤¤¤',
                                    babel.numbers.get_currency_name(
                                        currency, value, locale))
            retval = retval.replace(u'¤¤', currency.upper())
            retval = retval.replace(u'¤', babel.numbers.get_currency_symbol(
                currency, locale))

        return retval

    def _quantize_value(self, value, locale, frac_prec):
        quantum = get_decimal_quantum(frac_prec[1])
        rounded = value.quantize(quantum)
        a, sep, b = str(rounded).partition(".")
        number = (self._format_int(a, self.int_prec[0],
                                   self.int_prec[1], locale) +
                  self._format_frac(b or '0', locale, frac_prec))
        return number

    def scientific_notation_elements(self, value, locale):
        """ Returns normalized scientific notation components of a value."""
        # Normalize value to only have one lead digit.
        exp = value.adjusted()
        value = value * get_decimal_quantum(exp)
        assert value.adjusted() == 0

        # Shift exponent and value by the minimum number of leading digits
        # imposed by the rendering pattern. And always make that number
        # greater or equal to 1.
        lead_shift = max([1, min(self.int_prec)]) - 1
        exp = exp - lead_shift
        value = value * get_decimal_quantum(-lead_shift)

        # Get exponent sign symbol.
        exp_sign = ''
        if exp < 0:
            exp_sign = babel.numbers.get_minus_sign_symbol(locale)
        elif self.exp_plus:
            exp_sign = babel.numbers.get_plus_sign_symbol(locale)

        # Normalize exponent value now that we have the sign.
        exp = abs(exp)

        return value, exp, exp_sign


def get_decimal_quantum(precision):
    """Return minimal quantum of a number, as defined by precision."""
    assert isinstance(precision, (int, decimal.Decimal))
    return decimal.Decimal(10) ** (-precision)


def get_decimal_precision(number):
    """Return maximum precision of a decimal instance's fractional part.
    Precision is extracted from the fractional part only.
    """
    # Copied from: https://github.com/mahmoud/boltons/pull/59
    assert isinstance(number, decimal.Decimal)
    decimal_tuple = number.normalize().as_tuple()
    if decimal_tuple.exponent >= 0:
        return 0
    return abs(decimal_tuple.exponent)
