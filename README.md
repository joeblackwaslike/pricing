# Pricing
[![Build Status](https://travis-ci.org/joeblackwaslike/pricing.svg?branch=master)](https://travis-ci.org/joeblackwaslike/pricing) [![Github Repo](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/joeblackwaslike/pricing) [![Pypi Version](https://img.shields.io/pypi/v/pricing.svg)](https://pypi.python.org/pypi/pricing) [![Pypi License](https://img.shields.io/pypi/l/pricing.svg)](https://pypi.python.org/pypi/pricing) [![Pypi Wheel](https://img.shields.io/pypi/wheel/pricing.svg)](https://pypi.python.org/pypi/pricing) [![Pypi Versions](https://img.shields.io/pypi/pyversions/pricing.svg)](https://pypi.python.org/pypi/pricing)


## Maintainer
Joe Black | <me@joeblack.nyc> | [github](https://github.com/joeblackwaslike)


## Introduction
Pricing classes and tools with CLDR-backed locale-aware formatting and currency exchange.  Easy to extend/customize since it's built on ZCA.


Define your custom currencies and exchange's in your project's ZCML and you're golden.


## Installation
```shell
pip3 install pricing
```

## Usage

### Basic
```python
>>> from pricing import Price
... Price('2.22', 'USD')
EUR 2.22

>>> Price('2.34223434', 'BTC')
BTC 2.34223434

>>> m = Price(2, 'USD')
... m.amount
Decimal('2')
... m.currency
'USD'

>>> m = Price('2.22', 'EUR')
... m / 2
EUR 1.11
>>> m + Price('7.77', 'EUR')
EUR 9.99
```

### Formatting
```python
>>> m = Price('1234.567', 'EUR')
... str(m)
'EUR 1,234.57'

>>> m.format()
'€1,234.57'
```

### Payment URI's
Create BIP21 and EIP681 compatible payment URI's.
```python
>>> from pricing.uris import BIP21PaymentURI
... BIP21PaymentURI(
... 'bitcoin',
... address='19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj',
... amount='4.32345').to_uri()
'bitcoin:19kxPokCjD6tUU3sHaLZgEQBkRsCTBt3jj?amount=4.32345'
```

```python
>>> from pricing.uris import EIP681PaymentURI
... EIP681PaymentURI(
... 'ethereum',
... address='077a7506b69e37e4f6852577190f04a35df9a36c',
... value='4.32345').to_uri()
'ethereum:0x077a7506b69e37e4f6852577190f04a35df9a36c?value=4.32345'
```


### Currency Exchange
Currency exchange works by "installing" a **backend** class that implements the `IExchangeBackend` interface.


### XPrice
You can use ``money.XPrice`` (a subclass of Price), for automatic currency conversion while adding, subtracting, and dividing money objects (+, +=, -, -=, /, //). This is useful when aggregating lots of money objects with heterogeneous currencies. The currency of the leftmost object has priority.

```python
from pricing import XPrice

# Register backend and rates as above...
a = XPrice(1, 'AAA')
b = XPrice(1, 'BBB')

assert sum([a, b]) == XPrice('1.25', 'AAA')
```

### Extending and customization
You can use ZCML to configure custom currencyFormats and exchanges, create a new file called `currency.zcml`, and follow the example below to configure.

```xml
<configure
    xmlns:zope="http://namespaces.zope.org/zope"
    xmlns="http://namespaces.zope.org/currency">

    <zope:include package="pricing" file="currency-meta.zcml" />

    <currency default="USD">
        <currencyFormat
            name="bitcoin"
            code="BTC"
            symbol="₿"
            format="¤#,##0.########"
            currency_digits="false"
            decimal_quantization="true" />
        <currencyFormat
            name="litecoin"
            code="LTC"
            symbol="Ł"
            format="¤#,##0.########"
            currency_digits="false"
            decimal_quantization="true" />
        <currencyFormat
            name="ether"
            code="ETH"
            symbol="Ξ"
            format="¤#,##0.##################"
            currency_digits="false"
            decimal_quantization="true" />

        <exchange
            component="pricing.exchange.Exchange"
            backend="pricing.exchange.CoinBaseBackend"
            base="USD" />
    </currency>

</configure>
```

Then include `currency.zcml` in your `configure.zcml` file:
```xml
<include file="currency.zcml" />
```

### Fields
Included are custom fields for `zope.schema` and `attrs` based classes.  Checkout `money.fields`.


## Exceptions
``PriceException(Exception)``
    Base class for all exceptions.

``CurrencyMismatch(PriceException, ValueError)``
    Thrown when mixing different currencies, e.g. ``Price(2, 'EUR') + Price(2, 'USD')``. Price objects must be converted first to the same currency, or XPrice could be used for automatic conversion.

``InvalidOperandType(PriceException, TypeError)``
    Thrown when attempting invalid operations, e.g. multiplication between money objects.

``ExchangeError(PriceException)``
    Base class for exchange exceptions.

``ExchangeBackendNotInstalled(ExchangeError)``
    Thrown if a conversion is attempted, but there is no backend available.

``ExchangeRateNotFound(ExchangeError)``
    The installed backend failed to provide a suitable exchange rate between the origin and target currencies.

### Hierarchy
* ``PriceException``
    * ``CurrencyMismatch``
    * ``InvalidOperandType``
    * ``ExchangeError``
        * ``ExchangeBackendNotInstalled``
        * ``ExchangeRateNotFound``


## Changes
* [CHANGELOG](CHANGELOG.md)
