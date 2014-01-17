============
Corpus Tools
============

Corpus Tools are tools to manipulate a corpus in different ways.

Installation
============

Install the tools for all users on a machine by writing

``sudo python setup.py install``

The scripts ccat and analyse_corpus will then be found in /usr/local/bin

Install the tools for the current user by writing

``sudo python setup.py install --user``

The scripts ccat and analyse_corpus will then be found in ~/.local/bin

ccat
====

Convert corpus format xml til clean text

analyse_corpus
==============

Analyse the corpus.

It depends on these external programs:

* ``preprocess``

* ``lookup`` (from xfst)

* ``vislcg3``

