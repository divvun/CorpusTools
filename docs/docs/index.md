# CorpusTools documentation

## Overview

_CorpusTools_ is a set of tools to administrate Giellatekno's corpora.

A few examples:

- [add_files_to_corpus](scripts/add_files_to_corpus) - Add raw source material files to a corpus
- [convert2xml](scripts/convert2xml) - Converts original files to the Giellatekno-internal xml format.
- [analyse_corpus](scripts/analyse_corpus) - Orchistrates the _hfst_ (etc) tools to run analysis on a corpus.
- [ccat](scripts/ccat) - Output text sections from an analysed or non-analysed corpus.
- [korp_mono](scripts/korp_mono) - Convert analysed files to korp-input

## Installation from apertium nightly

CorpusTools is available as a package in Apertium Nightly. Depending on your
system, the package may be named slightly differently. For example, in _debian_,
the package is called `divvun-corpustools`. Search for `corpustools`, and you
will find it.

## Installation using pipx

> pipx lets you install python packages that has runnable scripts easily,
> onto your system.

1. Install [pipx](https://pypa.github.io/pipx/installation/)
1. Run `pipx install --force git+https://github.com/divvun/CorpusTools.git`

### Editable install (alternate pipx installation method)

An _editable_ install lets you make changes in the source script files, and
still use the same global command on the command line to run the (modified) scripts.
Recommended if you intend to do development on the scripts.

1. Clone the CorpusTools repository: (`git clone https://github.com/divvun/CorpusTools.git CorpusTools`)
1. Install with the editable flag (`-e`): `pipx install -e --force /path/to/CorpusTools`

### Requirements

- pdftohtml (only needed for convert2xml)
- latex2html (only needed for convert2xml)
- pandoc (only needed for convert2xml?)

Installation commands
=== "Mac"

    ```
    sudo port install latex2html poppler pandoc
    ```

=== "Debian/Ubuntu"
`sudo apt-get install poppler-utils pandoc`

=== "Arch Linux"
`sudo pacman -S pandoc`
