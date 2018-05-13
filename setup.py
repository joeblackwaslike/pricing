import re
from setuptools import setup, find_packages


with open('pricing/__init__.py', 'rt') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

try:
    from m2r import parse_from_file
    long_description = parse_from_file('README.md')
except ImportError:
    with open('README.md') as fd:
        long_description = fd.read()


setup(
    name='pricing',
    version=version,
    description='Python Pricing Package',
    long_description=long_description,
    keywords=[
        'money',
        'price',
        'pricing',
        'currency',
        'cryptocurrency',
        'bitcoin',
        'exchange',
        'rates',
        'ranges',
        'formats'
    ],
    author='Joe Black',
    author_email='me@joeblack.nyc',
    maintainer='Joe Black',
    maintainer_email='me@joeblack.nyc',
    url='https://github.com/joeblackwaslike/pricing',
    download_url=(
        'https://github.com/joeblackwaslike/pricing/tarball/v%s' % version),
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'zope.interface>=4.5.0',
        'zope.configuration>=4.1.0',
        'zope.component>=4.4.1',
        'requests>=2.18.4',
        'zulu>=0.12.0',
        'attrs>=18.1.0',
        'babel>=2.5.3',
        'boltons>=18.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Utilities',
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Topic :: Software Development :: Libraries',
    ]
)
