# BEFORE YOU READ FURTHER

The `compile_cwb_files.py` is the new script. All the other files are old,
but kept for reference.

# What is this

The script takes as input the "korp-ready" files in "corpus-xxx/korp",
(which is made by the `korp_mono` script), and creates the binary CWB files
that goes in the data/ and registry/ directories.

After running the script, .yaml files need to be added to the Korp
backend configuration directory CORPUS_CONFIG/corpora.
One .yaml file for each file in the created registry/ folder.
It contains information to Korp for how to present the corpus in the
web interface. Things like "description" and such go in there. Refer to the
Korp documentation for more information about that.
This only applies to v9 of Korp, as previously configuration was done
differently.

Some of these things could be done programmatically, but ultimately there
are settings in there that we cannot determine from this script (at least
not trivally), so automating it further is probably not worth it. As long
as the documentation is good, it's really ok.


## Description of the old files

(These are scribbled notes as how I understood the old files to work)

### compile_corpus.xsl

"Concatenates" the .xml files that are in `corpus-LANG/korp` into one
.vrt-file for each corpus. In each language, each category gets it's own
"corpus". So as output from this will be files such as `LANG_CATEGORY_DATE`
(e.g. `sme_science_20230510`).

How to run it given in the file. It requires some parameters to be set.
See the comment inside in the `run_compile_corpus_xsl()` function in
`compile_cwb_files.py`.

inputs:  (disse må gis til scriptet som kjører .xsl fila)
- cDomain: category, e.g. "science", "facta", "news", etc. The folders that
  are directly under "analysed", "converted", (etc) in corpus-xxx.
- cLang: 3-letter language code. e.g. sma, sme, ...
  same as is in the path to the corpus.
- inDir: input folder, in essence corpus/corpus-LANG/korp/DOMAIN
- date: the date the files are created (should be same as the date of analysis)
  in YYYYMMDD format

### loc_run_gt_corpus_encoding.sh

Uses the files in the temporarily created `vrt_lang_date` folder by the
`compile_corpus.xsl` script (above), and makes the CWB data/ and registry/
files.

Requires some data set in a metadata file (loc_metadata_sme.json), and
setting some variables in the script before it's run.

args:
- in_dir (the corpus folder)
metaFile: JSON file with the metadata for that corpus
  format:
   object with field "metadata" ->
     object with field "text" ->
       array of objects:
         id, name, title, description, lang, updated

  -- So it lists more corpora at the same time (hmm)
date: (same date as above)
lang_code: (same lang as above)

This script then calls the `loc_encode_gt_corpus_20181106.sh` to do most
of it's job.

