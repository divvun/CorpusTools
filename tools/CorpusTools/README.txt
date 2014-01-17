============
Corpus Tools
============

Corpus Tools is used for manipulating a corpus

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
==========

Convert original files in the corpus to corpus format xml.

It converts the following formats to the corpus xml format:

* Microsoft Word .doc files

* .pdf files

* .rtf files

* .html files

* .xml from the sámi newspaper Ávvir

* .svg files

* .bible.xml files

It depends on these external programs:

* ``antiword`` (convert MS Word format files)

* ``pdftotext`` (convert PDF files)

* ``biblexml2xml.pl`` (convert bible xml format files)

* ``lookup`` (from xfst)

