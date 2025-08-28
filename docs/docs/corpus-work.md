# Working with corpora

## Structure

The corpus for a given language is hosted on github. Raw source files, along
with metadata, is stored in `github.com/giellalt/corpus-xxx-orig` (where `xxx`
is a language code), while processed output is stored in
`github.com/giellalt/corpus-xxx`.

Additionally, _bound_ (or _restricted_) corpus are stored as
`github.com/giellalt/corpus-xxx-orig-x-closed` and `github.com/giellalt/corpus-xxx-x-closed`.

## Git LFS

The source repositories contains original files (as _pdf_, _docx_, etc),
and many of them are large. We use Git **L**arge **F**ile **S**torage (LFS) to
handle them.

This means that they are not downloaded when you clone the repository, instead
you will get files containing information for LFS about where the files are
located, and their size.

!!! note
LFS is only required for handling raw source files (i.e. when working with
**corpus-xxx-orig**). If you are not dealing with any raw material - and
only dealing with the \*_corpus-xxx_ folder, you can skip this.

### Installation

Installation is documented in their readme, at [https://github.com/git-lfs/git-lfs#installing](https://github.com/git-lfs/git-lfs#installing), but see also the main site at [https://git-lfs.com/](https://git-lfs.com/).
