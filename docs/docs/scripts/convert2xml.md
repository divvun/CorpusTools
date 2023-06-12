# convert2xml

The `convert2xml` script runs `corpustools.convertermanager:main`.

## Overview

Convert original files in a corpus to giellatekno/divvun xml format.

## Dependencies

convert2xml depends on these external programs:

  - pdftotext
  - wvhtml

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
