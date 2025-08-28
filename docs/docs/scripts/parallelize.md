# parallelize

Parallelize parallel corpus files, write the results to .tmx and .txm.html
files.

NB! When debugging alignment, use [reparallelize](https://divvun.github.io/CorpusTools/scripts/reparallelize/), it reconverts
all files and realigns the file anew.

## Compile dependencies

XXX is the iso code for the language you work with in $GTLANGS/lang-XXX:

```sh
    cd $GTLANGS/lang-XXX
    ./configure --prefix="$HOME"/.local \
                --enable-tokenisers \
                --enable-analyser-tool
    make
    make install
```

The complete help text from the program is as follows:

```text
usage: parallelize [-h] [--version] [-d DICT] -l2 LANG2 sources [sources ...]

Sentence align file pairs.

positional arguments:
  sources               Files or directories to search for parallelisable
                        files

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d DICT, --dict DICT  Use a different bilingual seed dictionary. Must have
                        two columns, with input_file language first, and
                        --parallel_language second, separated by `/'. By
                        default, $GTHOME/gt/common/src/anchor.txt is used, but
                        this file only supports pairings between
                        sme/sma/smj/fin/eng/nob.
  -l2 LANG2, --lang2 LANG2
                        Indicate which language the given file should be
                        parallelised with
```

You run the program on the files created by convert2xml by running a command
with the following syntax:

```sh
parallelize -l2 TARGET_LANGUAGE PATH/TO/THE/CONVERTED/SOURCE_LANGUAGE/FILE.xml
```

for instance, with nob as SOURCE_LANGUAGE and sma as TARGET_LANGUAGE

```sh
parallelize -l2 sma corpub-nob/converted/admin/ntfk/tsaekeme.html.xml
```

This will create a file named `corpus-nob/tmx/sma/admin/ntfk/tsaekeme.html.tmx`

If you want to parallelize all your sma files with nob in one go, you can do
e.g.

```sh
convert2xml corpus-sma-orig
convert2xml corpus-nob-orig
parallelize -l2 sma corpus-nob/converted
```

The files will end up in corresponding directories under `corpus-nob/tmx/sma`.
