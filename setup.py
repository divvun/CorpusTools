# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='CorpusTools',
    version='0.6.0',
    author='Børre Gaup',
    author_email='borre.gaup@uit.no',
    packages=find_packages(),
    url='http://divvun.no',
    license='GPL v3.0',
    long_description=open('README.txt').read(),
    entry_points = {
        'console_scripts': ['ccat = corpustools.ccat:main',
                            'analyse_corpus = corpustools.analyser:main',
                            'convert2xml = corpustools.converter:main',
                            'parallelize = corpustools.parallelize:main',
                            'pick_sd_se = corpustools.pick_samediggi_se_docs:main']
    },
    install_requires=[
        "pyth",
        "pytidylib",
        "beautifulsoup4",
    ],
    test_suite = 'nose.collector',
    include_package_data=True,
)
