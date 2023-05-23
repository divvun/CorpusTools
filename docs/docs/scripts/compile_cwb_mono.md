# compile_cwb_mono.py

Concatenates all vrt-files in `corpus-xxx/korp_mono/` (which is made by the
`korp_mono` script), and run the _Corpus WorkBench_ (`CWB`) toolchain to
produce the final files needed for Korp (the files in the `data/` and
`registry/` CWB folders).

This is the last script in the process, and is very quick to run.

After running the script, `.yaml` files need to be added to the Korp
backend configuration directory `CORPUS_CONFIG/corpora`.
One .yaml file for each file in the created `registry/` folder.
It contains information to Korp for how to present the corpus in the
web interface. Things like "description" and such go in there. Refer to the
Korp documentation for more information about that.
This only applies to v9 of Korp, as previously configuration was done
differently.

Some of these things could be done programmatically, but ultimately there
are settings in there that we cannot determine from this script (at least
not trivally), so automating it further is probably not worth it. As long
as the documentation is good, it's really ok.


## Basic usage

```
usage: compile_cwb_mono.py [-h] [--date DATE] [--cwb-binaries-dir CWB_BINARIES_DIR]
                           [--target TARGET] [--data-dir DATA_DIR] [--registry-dir REGISTRY_DIR]
                           directory
$ compile_cwb_mono --target TARGET KORP_MONO_DIRECTORY
```

Use `--date` to set the date as it appears to *CWB*. It's optional, and today's
date will be used if not given.

Either (1) `--target` or (2) _both_ `--data-dir` _and_ `--registry-dir` must
be given, even though the usage text of the program (the text that you get
when you run `compile_cwb_mono --help`) suggests otherwise.

`--data-dir` specifies where the *CWB* `data/` directory resides, while
`--registry-dir` specifies the *CWB* `registry/` directory. If both the `data/`
and `registry/` directory resides next to each other in the same parent directory,
it's easier to use `--target`, which specifies the parent directory.


## Options

If the script cannot find the *CWB* _binaries_ (`cwb-encode`, `cwb-makeall`,
etc...), you can use `--cwb-binaries-dir` to tell the script where they are
located.

