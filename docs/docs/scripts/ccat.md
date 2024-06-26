# ccat

Convert corpus format xml to clean text.

ccat has three usage modes, print to stdout the content of:

- converted files (produced by [convert2xml](https://giellalt.github.io/CorpusTools/scripts/convert2xml/))
- converted files containing errormarkup (produced by [convert2xml](https://giellalt.github.io/CorpusTools/scripts/convert2xml/))
- analysed files (produced by [analyse_corpus](https://giellalt.github.io/CorpusTools/scripts/analyse_corpus/))

## Printing content of converted files to stdout

To print out all sme content of all the converted files found in
corpus-sme/converted/admin and its subdirectories, issue the command:

```sh
ccat -a -l sme corpus-sme/converted/admin
```

It is also possible to print a file at a time:

```sh
ccat -a -l sme corpus-sme/converted/admin/sd/other_files/vl_05_1.doc.xml
```

To print out the content of e.g. all converted pdf files found in a directory
and its subdirectories, issue this command:

```sh
find corpus-sme/converted/science/ -name "*.pdf.xml" | xargs ccat -a -l sme
```

## Printing content of analysed files to stdout

The analysed files produced by [analyse_corpus](https://giellalt.github.io/CorpusTools/scripts/analyse_corpus/) contain among
a dependency element, that contain the dependency analysis of the original files content.

Prints the content of the disambiguation element.

```sh
ccat -dep sda/sda_2006_1_aikio1.pdf.xml
```

Prints the content of the dependency element.

The usage pattern for printing these elements is otherwise the same as printing
the content of converted files.

Printing dependency elements

```sh
ccat -dep corpus-sme/analysed/admin
ccat -dep corpus-sme/analysed/admin/sd/other_files/vl_05_1.doc.xml
find analysed/science -name "*.pdf.xml" | xargs ccat -dep
```

Printing disambiguation elements

```sh
ccat -dis corpus-sme/analysed/admin
ccat -dis corpus-sme/analysed/admin/sd/other_files/vl_05_1.doc.xml
find analysed/science -name "*.pdf.xml" | xargs ccat -dis
```

## Printing errormarkup content

This usage mode is used in the speller tests. Examples of this usage pattern is
found in the make files in $GTBIG/prooftools.

### The complete help text from the program

```sh
usage: ccat [-h] [--version] [-l LANG] [-T] [-L] [-t] [-a] [-c] [-C] [-ort]
            [-ortreal] [-morphsyn] [-syn] [-lex] [-format] [-foreign]
            [-noforeign] [-withforeign] [-typos] [-f] [-S] [-dis] [-dep]
            [-hyph HYPH_REPLACEMENT]
            targets [targets ...]

Print the contents of a corpus in XML format The default is to print
paragraphs with no type (=text type).

positional arguments:
  targets               Name of the files or directories to process. If a
                        directory is given, all files in this directory and
                        its subdirectories will be listed.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -l LANG               Print only elements in language LANG. Default is all
                        langs.
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
  -withforeign          When printing corrections: include foreign text
                        instead of nothing
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
