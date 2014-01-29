============
Corpus Tools
============

Corpus Tools are tools to manipulate a corpus in different ways.

Installation
============

Install the tools for all users on a machine by writing

``sudo python setup.py install --install-scripts=/usr/local/bin``

The scripts ccat, convert2xml, analyse_corpus and parallelize will then be found in /usr/local/bin

Install the tools for the current user by writing

``python setup.py install --user --install-scripts=$HOME/bin``

The scripts ccat, convert2xml, analyse_corpus and parallelize will then be found in ~/bin

Uninstalling
============

``sudo pip(-2.7) uninstall`` will uninstall the scripts from /usr/local/bin and the python system path.

``pip(-2.7) uninstall --user`` will uninstall the scripts from $HOME/bin and the users python path.

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

convert2xml
===========

Convert original files in a corpus to giellatekno xml format.

It depends on these external programs:

* ``pdftotext``

* ``antiword``

* ``bible2xml.pl``

parallelize
===========

Parallelize two parallel corpus files, write the result to a .tmx file.
