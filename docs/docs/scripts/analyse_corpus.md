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
