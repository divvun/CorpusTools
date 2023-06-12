# korp_mono

Turns analysed files into *.vrt* format, for usage with Korp.

```sh 
usage: korp_mono [-h] [--version] [--ncpus NCPUS] [--skip-existing] [--serial] analysed_entities [analysed_entities ...]

Turn analysed files into vrt format xml files for Korp use.

positional arguments:
  analysed_entities  analysed files or directories where analysed files live

options:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  --ncpus NCPUS      The number of cpus to use. If unspecified, defaults to using as many cpus as it can. Choose between 1-12,
                     some (3), half (6), most (9) or all (12).
  --skip-existing    Skip files that already exist in the korp_mono/ folder
  --serial           When this argument is used files will be converted one by one.Using --serial takes priority over --ncpus
```
