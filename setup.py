# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='CorpusTools',
    version='0.1',
    author='Børre Gaup',
    author_email='borre.gaup@uit.no'],
    packages=['corpustools', 'corpustools.test'],
    license='GPL v3.0',
    long_description=open('README.txt').read(),
    install_requires=[
        "pyth",
        "pytidylibs",
        "beautifulsoup4",
)
