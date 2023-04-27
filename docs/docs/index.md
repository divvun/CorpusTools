# CorpusTools documentation

## Overview

*CorpusTools* is a set of tools to manipulate a giellalt corpus in different ways.

A few examples:

  - `convert2xml` - Converts original files to the Giellatekno-internal xml format.
  - `analyse_corpus` - Orchistrates the _hfst_ (etc) tools to analyse a corpus.
  - `ccat` - Output _Corpus WorkBench_-readable text files from an analysed or non-analysed corpus.

## Installation from apertium nightly

CorpusTools is available as a package in Apertium Nightly. Depending on your
system, the package is named slightly differently. Search for `corpustools`.

## Installation using pipx

> pipx lets you install python packages that has runnable scripts easily,
> onto your system.

 1. Install [pipx](https://pypa.github.io/pipx/installation/)
 2. Run `pipx install --force git+https://github.com/giellalt/CorpusTools.git`

### Requirements

  - python3
  - wvHtml (only needed for convert2xml)
  - pdftohtml (only needed for convert2xml)
  - latex2html (only needed for convert2xml)
  - Java (only needed for parallelize)
  - pandoc (maybe only needed for convert2xml?)

Installation commands
=== "Mac"

    ```
    sudo port install wv latex2html poppler pandoc
    ```

=== "Debian/Ubuntu"
    ```
    sudo apt-get install vw poppler-utils pandoc
    ```

=== "Arch Linux"
    ```
    sudo pacman -S wv
    ```

## And continued here

This is a paragraph.
