# Corpus Tools

Tools to manipulate a giellalt corpus in different ways.

## Install and update from Apertium nightly

These tools are a part of
[Apertium nightly packages](https://wiki.apertium.org/wiki/Installation/Developers).

For Mac users, running the `install-nightly.sh` suffices, Linux users will have
to run `<package-manager> install <name of package>`, as well (search for corpustools in
the package system).

To update the tools on Mac, run `install-nightly.sh`. On Linux, update packages
using the package manager.

## Install and update using pipx

* [Install pipx](https://pypa.github.io/pipx/installation/)
* Run `pipx install --force git+https://github.com/giellalt/CorpusTools.git`

## Requirements

* python3
* wvHtml (only needed for convert2xml)
* pdftohtml (only needed for convert2xml)
* latex2html (only needed for convert2xml)
* Java (only needed for parallelize)

On Mac, do:

```sh
sudo port install wv latex2html poppler
```

On Debian/Ubuntu, do:

```sh
sudo apt install wv latex2html poppler-utils
```

On Arch Linux, do:

```sh
sudo pacman -S wv
```

## Use the content of the corpus

* [convert2xml: Convert original files to giellatekno xml](#convert2xml)
* [ccat: Print the contents of a converted corpus file as plain text](#ccat)
* [analyse_corpus: Do syntactic analysis of converted files](#analyse_corpus)
* [parallelize: Sentence align file pairs](#parallelize)
* [reparallelize: Reconvert and realign a given .tmx.html file](#reparallelize)
* [tmx2html: Convert tmx files to html files](#tmx2html)

## Add files to the corpus

* [add_files_to_corpus: Add file(s) to a corpus directory](#add_files_to_corpus)
* [saami_crawler: Crawl saami sites, add files to corpus](#saami_crawler)

## Manage the corpus repositories

* [move_corpus_file: Move or rename a file inside the corpus](#move_corpus_file)
* [remove_corpus_file: Remove a file from the corpus](#remove_corpus_file)
* [normalise_corpus_names: Program to normalise file names](#normalise_corpus_names)
* [paracheck: Check if the parallel files found in the metadata files exist](#paracheck)
* [duperemover: Remove duplicate files from the given directory](#duperemover)
* [dupefinder: Find files with more than 90% similarity in the given directory](#dupefinder)
* [clean_prestable:Remove files in prestable that have no original files](#clean_prestable)
* [pick_parallel_docs: Pick out parallel files from converted to prestable/converted](#pick_parallel_docs)
* [update_metadata: Update metadata files in given directories](#update_metadata)

## Miscellaneous

* [pytextcat: textcat implemented in Python](#pytextcat)
* [generate_anchor_list: Generate paired anchor list for languages lang1 and lang2](#generate_anchor_list)
* [html_cleaner: Program to print out a nicely indented html document](#html_cleaner)
* [epubchooser: Program to set metadata of an epub file](#epubchooser)
* [make_training_corpus: Program to make training corpus from giella xml analysed files](#make_training_corpus)

## ccat

Convert corpus format xml to clean text.

ccat has three usage modes, print to stdout the content of:

* converted files (produced by [convert2xml](#convert2xml))
* converted files containing errormarkup (produced by [convert2xml](#convert2xml))
* analysed files (produced by [analyse_corpus](#analyse_corpus))

## Printing content of converted files to stdout

To print out all sme content of all the converted files found in
$GTFREE/converted/sme/admin and its subdirectories, issue the command:

```sh
ccat -a -l sme $GTFREE/converted/sme/admin
```

It is also possible to print a file at a time:

```sh
ccat -a -l sme $GTFREE/converted/sme/admin/sd/other_files/vl_05_1.doc.xml
```

To print out the content of e.g. all converted pdf files found in a directory
and its subdirectories, issue this command:

```sh
find converted/sme/science/ -name "*.pdf.xml" | xargs ccat -a -l sme
```

## Printing content of analysed files to stdout

The analysed files produced by [analyse_corpus](#analyse_corpus) contain among
other one dependency element and one disambiguation element, that contain the
dependency and disambiguation analysis of the original files content.

```sh
ccat -dis sda/sda_2006_1_aikio1.pdf.xml
```

Prints the content of the disambiguation element.

```sh
ccat -dep sda/sda_2006_1_aikio1.pdf.xml
```

Prints the content of the dependency element.

The usage pattern for printing these elements is otherwise the same as printing
the content of converted files.

Printing dependency elements

```sh
ccat -dep $GTFREE/analysed/sme/admin
ccat -dep $GTFREE/analysed/sme/admin/sd/other_files/vl_05_1.doc.xml
find analysed/sme/science/ -name "*.pdf.xml" | xargs ccat -dep
```

Printing disambiguation elements

```sh
ccat -dis $GTFREE/analysed/sme/admin
ccat -dis $GTFREE/analysed/sme/admin/sd/other_files/vl_05_1.doc.xml
find analysed/sme/science/ -name "*.pdf.xml" | xargs ccat -dis
```

## Printing errormarkup content

This usage mode is used in the speller tests. Examples of this usage pattern is
found in the make files in $GTBIG/prooftools.

### The complete help text from the program

```sh
usage: ccat [-h] [--version] [-l LANG] [-T] [-L] [-t] [-a] [-c] [-C] [-ort]
            [-ortreal] [-morphsyn] [-syn] [-lex] [-format] [-foreign]
            [-noforeign] [-typos] [-f] [-S] [-dis] [-dep]
            [-hyph HYPH_REPLACEMENT]
            targets [targets ...]

Print the contents of a corpus in XML format The default is to print paragraphs
with no type (=text type).

positional arguments:
  targets               Name of the files or directories to process. If a
                        directory is given, all files in this directory and
                        its subdirectories will be listed.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -l LANG               Print only elements in language LANG. Default is all
                        languages.
  -T                    Print paragraphs with title type
  -L                    Print paragraphs with list type
  -t                    Print paragraphs with table type
  -a                    Print all text elements
  -c                    Print corrected text instead of the original typos &
                        errors
  -C                    Only print unclassified (§/<error..>) corrections
  -ort                  Only print ortoghraphic, non-word ($/<errorort..>)
                        corrections
  -ortreal              Only print ortoghraphic, real-word
                        (¢/<errorortreal..>) corrections
  -morphsyn             Only print morphosyntactic (£/<errormorphsyn..>)
                        corrections
  -syn                  Only print syntactic (¥/<errorsyn..>) corrections
  -lex                  Only print lexical (€/<errorlex..>) corrections
  -format               Only print format (‰/<errorformat..>) corrections
  -foreign              Only print foreign (∞/<errorlang..>) corrections
  -noforeign            Do not print anything from foreign (∞/<errorlang..>)
                        corrections
  -typos                Print only the errors/typos in the text, with
                        corrections tab-separated
  -f                    Add the source filename as a comment after each error
                        word.
  -S                    Print the whole text one word per line; typos have tab
                        separated corrections
  -dis                  Print the disambiguation element
  -dep                  Print the dependency element
  -hyph HYPH_REPLACEMENT
                        Replace hyph tags with the given argument
```

# convert2xml

Convert original files in a corpus to giellatekno/divvun xml format.

convert2xml depends on these external programs:

* pdftotext
* wvHtml

## Usage

Convert all files in the directory $GTFREE/orig/sme and its subdirectories.

```sh
convert2xml $GTFREE/orig/sme
```

The converted files are placed in $GTFREE/converted/sme with the same directory
structure as that in $GTFREE/orig/sme.

Convert only one file:

```sh
convert2xml $GTFREE/orig/sme/admin/sd/file1.html
```

The converted file is found in $GTFREE/orig/sme/admin/sd/file1.htm.xml

Convert all sme files in directories ending with corpus

```sh
convert2xml *corpus/orig/sme
```

If convert2xml is not able to convert a file these kinds of message will appear:

```sh
~/Dokumenter/corpus/freecorpus/orig/eng/admin/depts/regjeringen.no/calendar-for-the-ministry-of-children-an.html_id=308
```

A log file will be found in

```sh
~/Dokumenter/corpus/freecorpus/orig/eng/admin/depts/regjeringen.no/calendar-for-the-ministry-of-children-an.html_id=308.log
```

explaining what went wrong.

The complete help text from the program:

```sh
usage: convert2xml [-h] [--version] [--serial] [--lazy-conversion]
                   [--write-intermediate] [--goldstandard]
                   sources [sources ...]

Convert original files to giellatekno xml.

positional arguments:
  sources               The original file(s) or directory/ies where the
                        original files exist

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --serial              use this for debugging the conversion process. When
                        this argument is used files will be converted one by
                        one.
  --lazy-conversion     Reconvert only if metadata have changed.
  --write-intermediate  Write the intermediate XML representation to
                        ORIGFILE.im.xml, for debugging the XSLT. (Has no
                        effect if the converted file already exists.)
  --goldstandard        Convert goldstandard and .correct files
```

# analyse_corpus

Analyse converted corpus files.

analyse_corpus depends on these external programs:

* vislcg3
* hfst

## Usage

To be able to use this program you must either use the
[nightly giella packages](https://giellalt.uit.no/infra/compiling_HFST3.html#The+simple+installation+%28you+download+ready-made+programs%29)
or build the needed resources for the supported languages (exchange "sma" with
"sme, smj" ad lib):

{{cd $GTLANGS/langs-sma}}

Configure the language, use at least these to options `--prefix=$HOME/.local
--enable-tokenisers`

```sh
./configure --prefix=$HOME/.local --enable-tokenisers # add your own flags to taste
make install
```

Then you must convert the corpus files as explained in the
[convert2xml](#convert2xml) section.

When this is done you can analyse all files in the directory
$GTFREE/converted/sme (and sma, smj) and its subdirectories by issuing this
command:

```sh
analyse_corpus $GTFREE/converted/sme
```

The analysed file will be found in {{$GTFREE/analysed/sme}}

To analyse only one file, issue this command:

```sh
analyse_corpus --serial sme $GTFREE/converted/sme/file.html.xml
```

The complete help text from the program:

```sh
analyse_corpus --help
usage: analyse_corpus [-h] [--version] [--serial] [-k {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}]
                      converted_entities [converted_entities ...]

Analyse files in parallel.

positional arguments:
  converted_entities    converted files or director(y|ies) where the converted files exist

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --serial              When this argument is used files will be analysed one by one.
  -k {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}, --modename {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}
                        You can set the analyser pipeline explicitely if you want.
```

# add_files_to_corpus

The complete help text from the program is as follows:

```sh
usage: add_files_to_corpus [-h] [-v] [-p PARALLEL_FILE] [-l LANG]
                           [-d DIRECTORY]
                           origs [origs ...]

Add file(s) to a corpus directory. The filenames are converted to ascii only
names. Metadata files containing the original name, the main language, the
genre and possibly parallel files are also made. The files are added to the
working copy.

positional arguments:
  origs                 The original files, urls or directories where the
                        original files reside (not the corpus repo)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

parallel:
  -p PARALLEL_FILE, --parallel PARALLEL_FILE
                        Path to an existing file in the corpus that will be
                        parallel to the orig that is about to be added
  -l LANG, --lang LANG  Language of the file to be added

no_parallel:
  -d DIRECTORY, --directory DIRECTORY
                        The directory where the origs should be placed
```

Examples:
Download and add parallel files from the net to the corpus:

`cd $GTFREE`

__Adding the first file__

The command

```sh
add_files_to_corpus -d orig/sme/admin/sd/other_files http://www.samediggi.no/content/download/5407/50892/version/2/file/Sametingets+%C3%A5rsmelding+2013+-+nordsamisk.pdf
```

Gives the message:

```sh
Added orig/sme/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_nordsamisk.pdf
```

__Adding the parallel file__

```sh
add_files_to_corpus -p orig/sme/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_nordsamisk.pdf -l nob  http://www.samediggi.no/content/download/5406/50888/version/2/file/Sametingets+%C3%A5rsmelding+2013+-+norsk.pdf
```

Gives the message:

```sh
Added orig/nob/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_norsk.pdf
```

After this is done, you will have to commit the files to the working copy, like
this:

```sh
git commit
```

# parallelize

**NOTE!** This section is partly outdated. Some files are moved from *svn* to *github* (especially the `langs` ones).

Parallelize parallel corpus files, write the results to .tmx and .txm.html
files.

NB! When debugging alignment, use [reparallelize](#reparallelize), it reconverts
all files and realigns the file anew.

parallelize depends on various files from the Divvun/Giellatekno SVN, at least
the following directories need to exist in $GTHOME:

* langs (specifically, the abbr.txt files)
* gt/common
* gt/script

It also requires Java if you wish to use the default (included) alignment
program TCA2. For convenience, a pre-compiled version of TCA2's
alignment.jar-file is included in SVN and installed by CorpusTools, but if you
have ant installed, you can recompile it by simply typing "ant" in
corpustools/tca2.

Alternatively, you can align with Hunalign, if you have that installed (or don't
have Java). Hunalign is faster, and the quality is less dependent on predefined
dictionaries (though it can use those as well). Neither system gives perfect
alignments.

By default, it uses the $GTHOME/gt/common/src/anchor.txt file as an anchor
dictionary for alignment. If your language pair is not in this dictionary, you
can provide your own with the --dict argument. If you do not have a dictionary,
you can use "--dict=<(echo)" to provide an "empty" dictionary – in this case,
you should also use "--aligner=hunalign".

## Compile dependencies

XXX is the iso code for the language you work with in $GTLANGS/lang-XXX:

```sh
    cd $GTLANGS/lang-XXX
    ./configure --prefix="$HOME"/.local \
                --enable-tokenisers \
                --enable-reversed-intersect
    make
    make install
```

To prepare for parallelising e.g. nob and sme files, do the following:

```sh
for LANG in sme nob # Replace sme and nob by languages for your own needs
do
    cd $GTLANGS/lang-$LANG
    ./configure --prefix="$HOME"/.local \
                --with-hfst \
                --enable-tokenisers
    make
    make install
done
```

The complete help text from the program is as follows:

```sh
usage: parallelize [-h] [--version] [-s] [-f] [-q] [-a {hunalign,tca2}]
                   [-d DICT] -l2 LANG2
                   sources [sources ...]

Sentence align file pairs.

positional arguments:
  sources               Files or directories to search for parallelisable
                        files

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -s, --stdout          Whether output of the parallelisation should be
                        written to stdout or a files. Defaults to
                        tmx/{lang1}2{lang2}/{GENRE}/.../{BASENAME}.tmx
  -f, --force           Overwrite output file if it already exists.This is the
                        default.
  -q, --quiet           Don't mention anything out of the ordinary.
  -a {hunalign,tca2}, --aligner {hunalign,tca2}
                        Either hunalign or tca2 (the default).
  -d DICT, --dict DICT  Use a different bilingual seed dictionary. Must have
                        two columns, with input_file language first, and
                        --parallel_language second, separated by `/'. By
                        default, $GTHOME/gt/common/src/anchor.txt is used, but
                        this file only supports pairings between
                        sme/sma/smj/fin/eng/nob.
  -l2 LANG2, --lang2 LANG2
                        Indicate which language the given file shouldbe
                        parallelised with
```

You run the program on the files created by convert2xml by running a command
with the following syntax:

```sh
parallelize -l2 TARGET_LANGUAGE PATH/TO/THE/CONVERTED/SOURCE_LANGUAGE/FILE.xml
```

for instance, with nob as SOURCE_LANGUAGE and sma as TARGET_LANGUAGE

```sh
parallelize -l2 sma converted/nob/admin/ntfk/tsaekeme.html.xml
```

This will create a file named tmx/nob2sma/admin/ntfk/tsaekeme.html.tmx

If you want to parallelize all your sma files with nob in one go, you can do
e.g.

```sh
convert2xml orig/{sma,nob}
parallelize -l2 sma converted/nob
```

The files will end up in corresponding directories under tmx/nob2sma.

__CAVEAT 1__: ''If you get a message such as''

```sh
parallelize -l2 sma converted/sma/admin/ntfk/tsaekeme.html.xml
Error reading file '/Users/xxx/freecorpus/converted/sma/admin/ntfk/.xml':
failed to load external entity "/Users/xxx/freecorpus/converted/sma/admin/ntfk/.xml"
```

then you gave nob as l1 but the path to a sma-file as argument.

__CAVEAT 2__: ''If you get a similar error message as''

```sh
parallelize -l2 sma converted/nob/admin/ntfk/rup_2013_trykt_versjon.pdf.xml
ERROR: /Users/xxx/gtsvn/langs/nob/tools/preprocess/tokeniser-gramcheck-gt-desc.pmhfst does not exist
```

you have to recompile the language tool of the respective language (in the
example above it is nob) with a different configuration, as in the following
example with nob as language to recompile, have a look at the info above on how
to [compile dependencies](#compile-dependencies)

After that you can go back to the directory where you are working with the
parallelizing files and try to parallelize the files anew. You might recompile
the language tools for ALL the languages you are working with.

__CAVEAT 3__: ''If you get a message like''

```sh
Exception in thread "main" java.lang.UnsupportedClassVersionError: aksis/alignment/Alignment : Unsupported major.minor version 51.0
        at java.lang.ClassLoader.defineClass1(Native Method)
        at java.lang.ClassLoader.defineClassCond(ClassLoader.java:637)
        at java.lang.ClassLoader.defineClass(ClassLoader.java:621)
        at java.security.SecureClassLoader.defineClass(SecureClassLoader.java:141)
        at java.net.URLClassLoader.defineClass(URLClassLoader.java:283)
        at java.net.URLClassLoader.access$000(URLClassLoader.java:58)
        at java.net.URLClassLoader$1.run(URLClassLoader.java:197)
        at java.security.AccessController.doPrivileged(Native Method)
        at java.net.URLClassLoader.findClass(URLClassLoader.java:190)
        at java.lang.ClassLoader.loadClass(ClassLoader.java:306)
        at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:301)
        at java.lang.ClassLoader.loadClass(ClassLoader.java:247)
```

then you need to recompile the Java parts and reinstall CorpusTools. Make sure
you have Apache ant installed, then do:

```sh
cd $GTHOME/tools/CorpusTools/corpustools/tca2
ant
```

Then follow the instructions on [how to install CorpusTools ](#installation)

# saami_crawler

Add files to freecorpus from a given site.

Only able to crawl www.samediggi.fi now, will collect html files only for now.

Run it like this:

```sh
saami_crawler www.samediggi.fi
```

The complete help text from the program is as follows:

```sh
usage: saami_crawler [-h] [-v] sites [sites ...]

Crawl saami sites (for now, only www.samediggi.fi).

positional arguments:
  sites          The sites to crawl

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# pytextcat

Pytextcat is an implementation of the "N-Gram-Based Text Categorization"
algorithm.

Original article:

Cavnar, W. B. and J. M. Trenkle,
''N-Gram-Based Text Categorization''
In Proceedings of Third Annual Symposium on
Document Analysis and Information Retrieval, Las Vegas, NV, UNLV
Publications/Reprographics, pp. 161-175, 11-13 April 1994.

Original Perl implementation and article available from
[http://odur.let.rug.nl/~vannoord/TextCat/]

```sh
usage: pytextcat [-h] [--version] [-V] {proc,complm,compwm,compdir} ...

Create or use n-gram models for language classification.

positional arguments:
  {proc,complm,compwm,compdir}
                        (try e.g. 'proc -h' for help with that subcommand)
    proc                Language classification
    complm              Compile character model from stdin to stdout.
    compwm              Compile word model from stdin to stdout.
    compdir             Compile language from directory.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -V, --verbose         Print some info to stderr
```

# generate_anchor_list

```sh
usage: generate_anchor_list.py [-h] [-v] [--lang1 LANG1] [--lang2 LANG2]
                               [--outdir OUTDIR]
                               input_file [input_file ...]

Generate paired anchor lisit for languages lg1 and lg2. Output line format
e.g. njukčamán* / mars. Source file is given command line, the format is
tailored for the file gt/common/src/anchor.txt.

positional arguments:
  input_file       The input file(s)

optional arguments:
  -h, --help       show this help message and exit
  -v, --version    show program's version number and exit
  --lang1 LANG1    First languages in the word list
  --lang2 LANG2    Second languages in the word list
  --outdir OUTDIR  The output directory
```

# normalise_corpus_names

Normalise the filenames of the files found in the given directories.

```sh
usage: normalise_corpus_names [-h] [--version] target_dirs [target_dirs ...]

Program to normalise names in given directories. The filenames are downcased,
non ascii characters are replaced by ascii ones and some unwanted characters
are removed.

positional arguments:
  target_dirs  The directory/ies where filenames should be normalised.

optional arguments:
  -h, --help   show this help message and exit
  --version    show program's version number and exit
```

# move_corpus_file

```sh
usage: move_corpus_file [-h] [-v] oldpath newpath

Program to move or rename files inside the corpus.

positional arguments:
  oldpath        The path of the old file.
  newpath        The place to move the file to. newpath can be either a
                 filename or a directory

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# paracheck

```sh
usage: paracheck [-h] [-v] orig_dir

Check the if the files in the parallel_text entries found in the metadata files
exist

positional arguments:
  orig_dir       The directory where the original corpus files are

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# html_cleaner

```sh
usage: html_cleaner [-h] [-v] inhtml outhtml

Program to print out a nicely indented html document. This makes it easier to
see the structure of it. This eases debugging the conversion of html
documents.

positional arguments:
  inhtml         The path of the html to indent.
  outhtml        The place where the indented html doc is written

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# duperemover

```sh
usage: duperemover [-h] [-v] dir

Remove duplicate files from the given directory

positional arguments:
  dir            The directory where the converted files exist

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

## dupefinder

```sh
usage: dupefinder [-h] [-v] dir

Find files with more than 90% similarity in the given directory

positional arguments:
  dir            The directory where the converted files exist

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# move_corpus_file

```sh
usage: move_corpus_file [-h] [-v] oldpath newpath

Program to move or rename a file inside the corpus.

positional arguments:
  oldpath        The path of the old file.
  newpath        The place to move the file to. newpath can be either a
                 filename or a directory

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# remove_corpus_file

```sh
usage: remove_corpus_file [-h] [-v] oldpath

Program to remove a file from the corpus.

positional arguments:
  oldpath        The path of the old file.

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

# pick_parallel_docs

```sh
usage: pick_parallel_docs [-h] [-v] -p PARALLEL_LANGUAGE --minratio MINRATIO
                          --maxratio MAXRATIO
                          language1_dir

Pick out parallel files from converted to prestable/converted.

positional arguments:
  language1_dir         directory where the files of language1 exist

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -p PARALLEL_LANGUAGE, --parallel_language PARALLEL_LANGUAGE
                        The language where we would like to find parallel
                        documents
  --minratio MINRATIO   The minimum ratio
  --maxratio MAXRATIO   The maximum ratio
```

# clean_prestable

```sh
usage: clean_prestable [-h] [--version] corpusdirs [corpusdirs ...]

Remove files in prestable that have no original files.

positional arguments:
  corpusdirs  Corpus directories

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

# reparallelize

```sh
usage: reparallelize [-h] [--version] [--files] [--convert] tmxhtml

Sentence align a given file anew. Files are converted before being
parallelised. This is mainly thought of as a debugging program when trying to
solve issues in parallelised files.

positional arguments:
  tmxhtml     The tmx.html file to realign.

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --files     Only show the interesting filenames that are needed for
              improving sentence alignment.
  --convert   Only convert the original files that are the source of the
              .tmx.html file. This is useful when improving the content of the
              converted files.
```

# tmx2html

```sh
usage: tmx2html [-h] [--version] sources [sources ...]

Convert tmx files to html

positional arguments:
  sources     Files or directories to search for tmx files

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

# update_metadata

```sh
usage: update_metadata [-h] [--version] directories [directories ...]

Update metadata files to look like XSL-template.xsl, but with original
content. This script exists because the XSL-template is updated with new
variables and documentation. This script will propagate these changes to
existing metadata files.

positional arguments:
  directories  Directories where metadata files should be updated.

optional arguments:
  -h, --help   show this help message and exit
  --version    show program's version number and exit
```

# epubchooser

```sh
usage: epubchooser [-h] [--version] epubfile

Choose which chapters and html ranges should be omitted from an epub file.

positional arguments:
  epubfile    Path to an epub file

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

# make_training_corpus

```sh
Make training corpus from analysed giella xml files. Sentences with words
unknown for the giella fsts are not included.

positional arguments:
  langs       The languages to make a training corpus for.

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```
