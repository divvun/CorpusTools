# reparallelize

```text
usage: reparallelize [-h] [--version] [--files] [--convert] tmxhtml

Sentence align a given file anew. Files are converted before being
parallelised. This is mainly thought of as a debugging program when trying to
solve issues in parallelised files.

positional arguments:
  tmxhtml     The tmx.html file to realign.

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --files     Only show the interesting filenames that are needed for
              improving sentence alignment.
  --convert   Only convert the original files that are the source of the
              .tmx.html file. This is useful when improving the content of the
              converted files.
```
