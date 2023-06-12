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
