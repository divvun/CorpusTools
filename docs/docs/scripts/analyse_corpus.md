# analyse_corpus

Analyse converted corpus files.

analyse_corpus depends on these external programs:

- vislcg3
- hfst

## Usage

To be able to use this program you must either use the
[nightly giella packages](https://giellalt.uit.no/infra/compiling_HFST3.html#The+simple+installation+%28you+download+ready-made+programs%29)
or build the needed resources for the supported languages (exchange "sma" with
"sme, smj" ad lib):

`cd $GTLANGS/langs-sma`

Configure the language, use at least these to options `--prefix=$HOME/.local
--enable-tokenisers`

```sh
./configure --prefix=$HOME/.local --enable-tokenisers # add your own flags to taste
make install
```

Then you must convert the corpus files as explained in the
[convert2xml](https://giellalt.github.io/CorpusTools/scripts/convert2xml/) section.

When this is done you can analyse all files in the corpus repos:

```sh
analyse_corpus corpus-<lang>/converted # exchange <lang> with your lang e.g. sme, sma, mdf
```

The analysed file will be found in `corpus-<lang>/analysed`

To analyse only one file, issue this command:

```sh
analyse_corpus --serial sme corpus-<lang>/converted/file.html.xml
```

The complete help text from the program:

```sh
usage: analyse_corpus [-h] [--version] [--ncpus NCPUS] [--skip-existing]
                      [--serial]
                      [-k {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}]
                      converted_entities [converted_entities ...]

Analyse files in parallel.

positional arguments:
  converted_entities    converted files or director(y|ies) where the converted
                        files exist

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --ncpus NCPUS         The number of cpus to use. If unspecified, defaults to
                        using as many cpus as it can. Choose between 1-12,
                        some (3), half (6), most (9) or all (12).
  --skip-existing       Skip analysis of files thar are already analysed (that
                        already exist in the analysed/ folder
  --serial              When this argument is used files will be analysed one
                        by one.Using --serial takes priority over --ncpus
  -k {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}, --modename {xfst,hfst,hfst_thirties,hfst_eighties,hfst_no_korp,trace-smegram-dev,trace-smegram}
                        You can set the analyser pipeline explicitely if you
                        want.
```
