#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

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
    entry_points={
        'console_scripts': [
            'add_files_to_corpus = corpustools.adder:main',
            'analyse_corpus = corpustools.analyser:main',
            'ccat = corpustools.ccat:main',
            'compare_tmx_goldstandard = corpustools.compare_tmx_goldstandard:main',
            'convert2xml = corpustools.converter:main',
            'debug_corpus = corpustools.debug_corpus:main',
            'generate_anchor_list = corpustools.generate_anchor_list:main',
            'html_cleaner = corpustools.html_cleaner:main',
            'move_corpus_file = corpustools.move_files:main',
            'normalise_corpus_names = corpustools.normalise_filenames:main',
            'packagetmx = corpustools.packagetmx:main',
            'paracheck = corpustools.check_para_consistency:main',
            'parallelize = corpustools.parallelize:main',
            'pick_sd_se = corpustools.pick_samediggi_se_docs:main',
            'pytextcat = corpustools.text_cat:main',
            'saami_crawler = corpustools.saami_crawler:main',
            'toktmx2tmx = corpustools.toktmx2tmx:main',
            'dupefinder = corpustools.dupe_finder:main',
        ]
    },
    install_requires=[
        'gitdb',
        'gitpython',
        'html5lib',
        'lxml',
        'odfpy',
        'pydocx',
        'pyth',
        'requests',
        'six',
        'testfixtures',
        'unidecode',
    ],
    test_suite='nose.collector',
    include_package_data=True,
)
