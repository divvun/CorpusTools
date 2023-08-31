# How we administer and work with our corpora

## Architecture

Our corpora are stored on github, in two different repositories for each language.
We have `giellalt/corpus-xxx-orig` for storing originals, and `giellalt/corpus-xxx`
for storing processed files. The `xxx` is a 3-letter ISO-639-3 language code, for
example `sme` for North Saami, and `nob` for Norwegian Bokmål.

Here's a quick overview:

```
corpus-xxx-orig/          - original files (txt, pdf, html, doc, etc)
  ...<categories>/        - documents are ordered in subfolder, one folder
                            for each category (admin, facta, ficti, news, etc...)
    .../<document>        - The original document
    .../<document>.xsl    - Metadata for the document

corpus-xxx/               - processed files
  converted/              - extracted texts from source files in corpus-xxx-orig
                            each file is stored in xml format
    ...<categories>/      - subcategores, same structure as under 'corpus-xxx-orig'
       .../<document>.xml - Individual document in our internal xml format
  analysed/               - result of running analysis on converted files
    ...<categories>/
       ...<document>.xml  - Analysed document, in our internal xml format
  korp_mono/              - "Korp-ready files"
    ...<categories>/
      .../<document>.xml  - analysed doucment in xml korp ready format
  korp_tmx/               -
  tmx/                    - Files in TMX format, ready for further parallel
    <lang1>/                corpus processing
    <lang2>/
    <...langN>/           - one subfolder for each language
      ...<categories>/
        ...<document>.tmx - each document in tmx format
       
```

*TMX* is an XML file for storing translation strings.

See the wikipedia article [https://en.wikipedia.org/wiki/Translation_Memory_eXchange](https://en.wikipedia.org/wiki/Translation_Memory_eXchange)
            
## What each script does

Script | Description
---|---
`add_files_to_corpus` | Copies original source files into `corpus-xxx-orig`. Adds the `.xsl` metadata files. The corpus maintainer will add missing metadata about each document.
`convert2xml` | Reads documents in `corpus-xxx-orig` (or some subfolder or single file therein), and outputs the `.xml` file of the extracted text from that document. The file automatically determines file type, and uses an extractor to read text from that filetype.
`analyse_corpus` | Reads documents in `corpus-xxx/converted`, and runs our language tools (`hfst, etc`) on them. The resulting analysed xml document is placed in `corpus-xxx/analysed`.
`analyse_para` | Analyses sentence-aligned input files found in `corpus-xxx/tmx` and outputs to `corpus-xxx/tmx_analysed`.
`korp_mono` | Reads documents in `corpus-xxx/analysed`, and converts the cg3-analysis format into a CWB-input format, one `.vrt` file per document.
`korp_para` | Reads documents from `corpus-xxx/tmx_analysed`, and converts the analysis format into CWB-input format, one `.vrt` file per tmx document.
`compile_cwb_mono` | Concatenates `korp_mono` (the files in `corpus-xxx/korp_mono`) into one `.vrt` file per genre, and runs CWB-tools on each of those to generate a CWB-corpus (which is what `Korp` reads).
`compile_cwb_para` | Ditto as mono, but for `tmx_analysed`
`parallelize` | Sentence-alignes two parallel corpora, outputs into `corpus-xxx/tmx`.
`reparallelize` | Uses information found in the input `.tmx` file, to re-do the sentence alignment (convert and parallelize). Useful when fixing mis-aligned `.tmx` files.
`ccat` | Prints plain text from an internal `.xml` (xml files produced by the `convert2xml` or `analyse_corpus`) file.
