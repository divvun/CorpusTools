# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='CorpusTools',
    version='0.1.1',
    author='Børre Gaup',
    author_email='borre.gaup@uit.no',
    packages=find_packages(),
    url='http://divvun.no',
    license='GPL v3.0',
    long_description=open('README.txt').read(),
    entry_points = {
        'console_scripts': ['ccat = corpustools.ccat:main',
                            'analyse_corpus = corpustools.analyser:main']
    },
    install_requires=[
        "pyth",
        "pytidylib",
        "beautifulsoup4",
    ],
    test_suite = 'nose.collector',
)
