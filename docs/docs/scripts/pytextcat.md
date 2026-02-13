# pytextcat

Language detection and text categorization based on n-gram models. This tool
implements the "N-Gram-Based Text Categorization" algorithm by Cavnar and
Trenkle (1994).

The tool can both classify text by language and compile language models from
training data.

## Basic usage

```text
pytextcat [options] <subcommand>
```

## Subcommands

### proc - Language classification

Classify input text and determine which language it is written in.

#### Usage

```text
pytextcat proc [options] [model_dir]
```

#### Arguments

- `model_dir` - Directory containing language model files (`.lm` and `.wm`
  files)
  - Optional; defaults to the built-in language models directory

#### Options

- `-l, --langs LANGS` - Comma-separated list of languages to classify between
  - By default, uses all languages found in `model_dir`
  - Example: `pytextcat proc -l sme,nob,sma`

- `-u DROP_RATIO` - Threshold for filtering character model results (default:
  1.1)
  - When the character model score of a language is worse than the best guess by
    this ratio or more, it is excluded from word model comparison

- `-s` - Process input line-by-line instead of treating entire input as one text

#### Examples

Classify a single text:

```sh
echo "Boadát go" | pytextcat proc
```

Classify multiple lines, one per line:

```sh
cat myfile.txt | pytextcat proc -s
```

Classify using only specific languages:

```sh
echo "Dette er norsk" | pytextcat proc -l nob,swe,dan
```

### complm - Compile character model

Compile a character n-gram model from plain text input.

Character models analyze the frequency of character substrings (1-4 character
sequences) to build a language fingerprint. These are used as the primary
classifier in language detection.

#### Usage

```text
pytextcat complm [options] < input_text > output_model
```

#### Input

Plain text on stdin. Can be any text in any language (UTF-8 recommended).

#### Output

Binary character model file (`.lm` format) written to stdout.

#### Options

- `-V, --verbose` - Print additional information to stderr during compilation

#### How it works

The compiler:

1. Reads text from stdin
1. Tokenizes the text (splits on whitespace and special characters)
1. Extracts all 1, 2, 3, and 4-character substrings from each word
1. Counts the frequency of each substring
1. Keeps the top 400 most frequent substrings
1. Writes these to the output model file

#### Examples

Compile a model from a text file:

```sh
pytextcat complm < corpus.txt > mylangs.lm
```

Compile from a gzipped file:

```sh
gunzip -c corpus.txt.gz | pytextcat complm > mylangs.lm
```

Compile with verbose output:

```sh
pytextcat complm -V < corpus.txt > mylangs.lm 2>compile.log
```

### compwm - Compile word model

Compile a word n-gram model from plain text input.

Word models analyze the frequency of individual words to refine language
classification. They are used to disambiguate when the character model alone is
uncertain.

#### Usage

```text
pytextcat compwm [options] < input_text > output_model
```

#### Input

Plain text on stdin. Can be any text in any language (UTF-8 recommended).

#### Output

Binary word model file (`.wm` format) written to stdout.

#### Options

- `-V, --verbose` - Print additional information to stderr during compilation

#### How it works

The compiler:

1. Reads text from stdin
1. Tokenizes the text (splits on whitespace and special characters)
1. Counts the frequency of each word
1. Keeps the top 30,000 most frequent words
1. Normalizes rankings to be compatible with incomplete models
1. Writes these to the output model file

#### Notes

- For a language with limited training data, the word model may contain fewer
  than 30,000 words
- Word models are optional; `proc` will work with just character models
- Word model frequency ordering is **inverse of character models** - this is
  intentional for ranking compatibility

#### Examples

Compile a model from a text file:

```sh
pytextcat compwm < corpus.txt > mylangs.wm
```

Filter and compile from a large corpus:

```sh
cat large_corpus.txt | head -1000000 | pytextcat compwm > mylangs.wm
```

Compile with verbose output:
```sh
pytextcat compwm -V < corpus.txt > mylangs.wm 2>compile.log
```

### compdir - Compile models from directory

Compile both character and word models from a directory of text files.

This is a convenience subcommand that trains on all `.txt` and `.txt.gz` files
in a directory and produces both `.lm` and `.wm` model files in an output
directory.

#### Usage

```text
pytextcat compdir [options] <corpus_directory> <output_directory>
```

#### Arguments

- `corpus_directory` - Directory containing training text files (`.txt` or
  `.txt.gz`)
- `output_directory` - Directory where to write the compiled models

Both directories must exist.

#### Options

- `-V, --verbose` - Print additional information to stderr during compilation

#### How it works

The compiler:

1. Scans `corpus_directory` for files matching `*.txt` or `*.txt.gz`
2. For each matching file, extracts the language name from the filename (without
   extension)
3. Trains a character model on the file's content
4. Trains a word model on the file's content
5. Writes `language.lm` and `language.wm` to `output_directory`

#### File naming convention

Files should be named like:

- `sme.txt` - Produces `sme.lm` and `sme.wm` (Northern Sámi)
- `nob.txt` - Produces `nob.lm` and `nob.wm` (Norwegian Bokmål)
- `fra.txt.gz` - Gzipped file produces `fra.lm` and `fra.wm` (French)

#### Examples

Compile models from a corpus directory with verbose output:

```sh
pytextcat compdir -V /path/to/corpus /path/to/models
```

## Model file formats

### Character model (.lm) file

Tab-separated text format, one n-gram per line:

```text
character_ngram    frequency
_a                 12540
_b                 9823
ab                 8734
...
```

Organized with highest frequency first.

### Word model (.wm) file

Tab-separated text format, one word per line:

```text
frequency    word
5430         the
4821         is
3921         and
...
```

Organized with highest frequency first.



## Algorithm notes

The classifier implements the algorithm from:

> Cavnar, W. B. and J. M. Trenkle, "N-Gram-Based Text Categorization" In
> Proceedings of Third Annual Symposium on Document Analysis and Information
> Retrieval, Las Vegas, NV, UNLV Publications/Reprographics, pp. 161-175, 11-13
> April 1994.

The original Perl implementation and paper are available at:
<https://www.let.rug.nl/vannoord/TextCat/>

### Character models (lm)

- Analyzes 1-4 character substrings within word boundaries
- Tracks only the top 400 n-grams by frequency
- Provides initial language ranking

### Word models (wm)

- Analyzes individual word frequencies
- Tracks up to 30,000 most frequent words
- Used for refinement when character model is ambiguous
- Distance metric uses inverted ranks for compatibility with incomplete models
