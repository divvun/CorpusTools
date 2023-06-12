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
