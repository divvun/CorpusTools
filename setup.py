# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

import corpustools.argparse_version


setup(
    name='CorpusTools',
    version=corpustools.argparse_version.version,
    author='Børre Gaup',
    author_email='borre.gaup@uit.no',
    packages=find_packages(),
    url='http://divvun.no',
    license='GPL v3.0',
    long_description=open('README.jspwiki').read(),
    entry_points = {
        'console_scripts': ['ccat = corpustools.ccat:main',
                            'analyse_corpus = corpustools.analyser:main',
                            'convert2xml = corpustools.converter:main',
                            'parallelize = corpustools.parallelize:main',
                            'pick_sd_se = corpustools.pick_samediggi_se_docs:main',
                            'add_files_to_corpus = corpustools.namechanger:adder_main',
                            'change_corpus_names = corpustools.namechanger:main']
    },
    install_requires=[
        "pyth",
        "pytidylib",
        "beautifulsoup4",
        "unidecode",
        "lxml",
        "gitdb",
        "pydocx",
        "gitpython",
    ],
    test_suite = 'nose.collector',
    include_package_data=True,
)
