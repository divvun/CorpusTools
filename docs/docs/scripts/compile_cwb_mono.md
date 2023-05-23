# compile_cwb_mono.py

Concatenates all vrt-files in `korp_mono/`, and run the _Corpus WorkBench_
(`CWB`) toolchain to produce the final files needed for Korp.

This is the last script in the process, and is very quick to run.


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

