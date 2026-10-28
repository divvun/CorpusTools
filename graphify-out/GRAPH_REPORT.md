# Graph Report - CorpusTools  (2026-10-28)

## Corpus Check
- 174 files · ~245,418 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 536 nodes · 601 edges · 178 communities (24 shown, 154 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f8f813ad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- XMLTester
- Exception
- BookChapter
- Element
- Converter
- Path
- Path
- Element
- expand
- Path
- Element
- Path
- flatten
- Element
- Path
- Path
- Path
- _Element
- Path
- _Element
- XMLTester
- Path
- Path
- Element
- Path
- Path
- Path
- Path
- Path
- Path
- Path
- Path
- Exception
- parametrize
- fixture
- fixture
- Element
- Exception
- CompletedProcess
- XMLTester
- _Element
- Path
- parametrize
- parameterized
- parameterized
- XMLTester
- parametrize
- parametrize
- parameterized
- parametrize
- avvirdigital.py
- Exception
- Module
- XMLTester
- XMLTester
- Book
- XMLTester
- ElementTree
- Path
- Element
- Path
- Path
- Path
- Path
- date
- Exception
- Enum
- analyse_corpus
- ccat.py
- GenerateAnchorList
- HtmlElement
- ParseResult
- Pattern
- Element
- TestCcatErrormarkup
- Exception
- DupeFinder
- TrainingCorpusMaker
- Path
- expand
- Element
- CorpusPath
- TestCcat
- Element
- Path
- .test_process_minus_l_sme
- .test_foreign
- Exception
- .test_no_foreign_typos
- BaseException
- .test_typos_errordepth3
- _Element
- .test_typos_errormorphsyn_twice
- .test_process_file1
- .test_process_file2
- .test_p
- CorpusPath
- ElementTree
- .test_p_with_span
- .test_p_with_error
- _Element
- Element
- .test_p_one_word_per_line
- expand
- .test_p_with_span_one_word_per_line
- .test_p_with_error_correction
- .test_p_with_error_filtering_errorlex
- Element
- Path
- Element
- .test_p_with_error_filtering_errormorphsyn
- Element
- analyse_corpus
- compile_cwb_files.py
- run_para_corpus_encoding.sh script
- insert.py
- Element
- Element
- Exception
- .test_p_with_error_filtering_errorort
- expand
- Classifier
- insert.py
- .test_visit_this_p_default
- .test_visit_this_p_title_set
- setter
- .test_visit_this_p_listitem_set
- XMLTester
- .test_visit_this_p_allp_set
- orig_to_text
- .test_process_file_title_set
- .test_process_file_listitem_set
- .test_get_element_language_same_as_parent
- .test_process_file_allp_set
- .test_get_lang
- .test_get_element_language_different_from_parent
- Saxon Transformation
- loc_encode_gt_corpus_20181106.sh script
- CorpusTools Release History
- .test_process_file_typos_errorlex
- .test_no_foreign
- .test_process_file_language_nob
- .test_process_file_one_word_per_line_errorort
- .test_process_file_one_word_per_line_errorlex
- Documentation Deployment Workflow
- Corpus Tools
- .test_process_two_paragraphs
- TestCcatHyph
- .test_process_file_typos
- _Element
- CorpusPath
- Corpus Repositories
- dupefinder
- move_corpus_file
- gen_ref_pages.py
- generate_tables.sh
- loc_encode_gt_corpus_20181106.sh
- Free Software Foundation
- MkDocs Documentation
- Corpus Processing Pipeline
- clean_prestable
- epubchooser
- html_cleaner
- paracheck
- saami_crawler
- update_metadata
- corpustools
- Path
- Element
- Exception
- Exception
- Classifier
- CorpusPath

## God Nodes (most connected - your core abstractions)
1. `TestCcat` - 40 edges
2. `Converter` - 19 edges
3. `PrintOptions` - 19 edges
4. `process_file()` - 15 edges
5. `DupeFinder` - 12 edges
6. `visit_children()` - 11 edges
7. `AvvirTaggedText` - 10 edges
8. `TestCcatErrormarkup` - 10 edges
9. `TrainingCorpusMaker` - 10 edges
10. `convert_tagged_text()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `convert_tagged_text()` --calls--> `test_control_chars_are_removed()`  [INFERRED]
  src/corpustools/avvirdigital.py → tests/test_avvirdigital.py
- `AvvirDocument` --calls--> `test_document_serialize_flattens_nested_containers()`  [INFERRED]
  src/corpustools/avvirdigital.py → tests/test_avvirdigital.py
- `convert_author()` --calls--> `test_control_chars_are_removed_from_image_and_author()`  [INFERRED]
  src/corpustools/avvirdigital.py → tests/test_avvirdigital.py
- `convert_author()` --calls--> `test_extract_author()`  [INFERRED]
  src/corpustools/avvirdigital.py → tests/test_avvirdigital.py
- `convert_image()` --calls--> `test_control_chars_are_removed_from_image_and_author()`  [INFERRED]
  src/corpustools/avvirdigital.py → tests/test_avvirdigital.py

## Import Cycles
- None detected.

## Communities (178 total, 154 thin omitted)

### Community 4 - "Converter"
Cohesion: 0.07
Nodes (19): Classifier, Converter, newer_group(), Return a boolean indicating if the file is convertable., Return a boolean indicating if the file is convertable., Return a boolean indicating if the file is a gold standard doc., Return the path to the corpus dtd file., Validate the complete document. (+11 more)

### Community 12 - "flatten"
Cohesion: 0.29
Nodes (5): SerializedXml, flatten(), Serialize the AvvirDocument to a list of XML elements., Flatten a nested structure of XML elements and sequences., Serialize the AvvirContainer to a list of lists of XML elements.

### Community 50 - "avvirdigital.py"
Cohesion: 0.08
Nodes (52): Any, AvvirAuthor, AvvirContainer, AvvirTaggedText, parametrize, AvvirAuthor, AvvirContainer, AvvirDocument (+44 more)

### Community 67 - "analyse_corpus"
Cohesion: 0.15
Nodes (15): add_files_to_corpus, analyse_corpus, ccat, compile_cwb_mono, convert2xml, Scripts Overview, korp_mono, make_training_corpus (+7 more)

### Community 68 - "ccat.py"
Cohesion: 0.07
Nodes (59): Element, ElementTree, Path, ccatter(), collect_inline_errors(), collect_not_inline_errors(), collect_text(), corrected_texts() (+51 more)

### Community 74 - "TestCcatErrormarkup"
Cohesion: 0.12
Nodes (9): Test how ccat handles errormarkup, Plain error element, default text flow, Nested error element, default text flow, Plain error element, one word per line output, Plain error element, one word per line output, with filename, Nested error element, one word per line output, with filename, Nested error element, one word per line output, One word per line, multiple corrections. (+1 more)

### Community 76 - "DupeFinder"
Cohesion: 0.13
Nodes (13): DupeFinder, find(), main(), parse_finder_options(), parse_remover_options(), Check if the word ratio of two files are nearly equal. Args: filename1 (str):…, Compare two files. Args: filename1 (str): name of the first file. filename2…, Compare all files to each other. Args: remove (bool): Defaults to False. If… (+5 more)

### Community 77 - "TrainingCorpusMaker"
Cohesion: 0.13
Nodes (13): main(), parse_options(), Turn a giella xml into a list of sentences. Args: filename (str): name of the…, Find analysed files. Yields: (str): filename of an analysed file., Make .txt files from .xml files. The .txt files contain only sentences with…, Turn the free and bound corpus into a pytextcat training corpus., Turn the free and bound corpus into a langid training corpus., Parse the options given to the program. (+5 more)

### Community 82 - "TestCcat"
Cohesion: 0.18
Nodes (5): Print only errorort content Check the output of a p element containing two…, Visit only <p type=tablecell> elements when table is True, Default settings, print content of p elements Check the output of plain p…, Print only content of p elements with type=title gets output., TestCcat

### Community 112 - "analyse_corpus"
Cohesion: 0.47
Nodes (6): analyse_corpus, convert2xml, korp_mono, Original Corpus, Processed Corpus, CorpusTools

### Community 113 - "compile_cwb_files.py"
Cohesion: 0.33
Nodes (6): compile_corpus.xsl, compile_cwb_files.py, CWB Binary Files, Korp Corpus Configuration, Korp-ready Files, VRT Corpus Files

### Community 114 - "run_para_corpus_encoding.sh script"
Cohesion: 0.33
Nodes (3): align_files.sh script, encode_gt_corpus.sh script, run_para_corpus_encoding.sh script

### Community 115 - "insert.py"
Cohesion: 0.33
Nodes (6): Base Form Relation Search, insert.py, Korp Database, _relations.sql, Settings Configuration, Word Picture Tables

### Community 129 - "orig_to_text"
Cohesion: 0.15
Nodes (17): CorpusPath, Namespace, Initialise the Converter class. Args: filename: the path to the file that…, main(), move_orig_to_correct(), orig_to_text(), parse_options(), Parse the commandline options. Returns: (argparse.Namespace): the parsed… (+9 more)

### Community 136 - "Saxon Transformation"
Cohesion: 0.50
Nodes (4): MySQL Timespan Import, Saxon Transformation, Timespan SQL Generation, Timestamp Extraction

### Community 138 - "CorpusTools Release History"
Cohesion: 0.67
Nodes (3): Document Conversion, Parallelization, CorpusTools Release History

### Community 144 - "Documentation Deployment Workflow"
Cohesion: 0.67
Nodes (3): Documentation Deployment Workflow, GitHub Pages, MkDocs

### Community 145 - "Corpus Tools"
Cohesion: 0.67
Nodes (3): Apertium Nightly Packages, Corpus Tools, pipx

### Community 147 - "TestCcatHyph"
Cohesion: 0.09
Nodes (10): Test hyph tags when hyph_replacement is set to "xml, Test hyph tags when hyph_replacement is set to "-, Test the treatment of two hyph tags in a row, The text before a hyph is the tail of the previous sibling, Test how ccat handles hyph, Test the default treatment of hyph tags, TestCcatCLI, TestCcatCLIErrors (+2 more)

## Knowledge Gaps
- **38 isolated node(s):** `corpustools`, `generate_tables.sh script`, `Original Corpus`, `Korp-ready Files`, `VRT Corpus Files` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **154 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestCcat` connect `TestCcat` to `.test_visit_this_p_allp_set`, `.test_process_file_title_set`, `.test_process_file_listitem_set`, `.test_get_element_language_same_as_parent`, `.test_process_file_allp_set`, `.test_get_lang`, `.test_get_element_language_different_from_parent`, `.test_process_file_typos_errorlex`, `.test_no_foreign`, `.test_process_file_language_nob`, `.test_process_file_one_word_per_line_errorort`, `.test_process_file_one_word_per_line_errorlex`, `.test_process_two_paragraphs`, `TestCcatHyph`, `.test_process_file_typos`, `.test_process_minus_l_sme`, `.test_foreign`, `.test_no_foreign_typos`, `.test_typos_errordepth3`, `.test_typos_errormorphsyn_twice`, `.test_process_file1`, `.test_process_file2`, `.test_p`, `.test_p_with_span`, `.test_p_with_error`, `.test_p_one_word_per_line`, `.test_p_with_span_one_word_per_line`, `.test_p_with_error_correction`, `.test_p_with_error_filtering_errorlex`, `.test_p_with_error_filtering_errormorphsyn`, `.test_p_with_error_filtering_errorort`, `.test_visit_this_p_default`, `.test_visit_this_p_title_set`, `.test_visit_this_p_listitem_set`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `Converter` connect `Converter` to `orig_to_text`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **What connects `corpustools`, `generate_tables.sh script`, `Original Corpus` to the rest of the system?**
  _38 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Converter` be split into smaller, more focused modules?**
  _Cohesion score 0.07394957983193277 - nodes in this community are weakly interconnected._
- **Should `avvirdigital.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07597402597402597 - nodes in this community are weakly interconnected._
- **Should `ccat.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07457627118644068 - nodes in this community are weakly interconnected._
- **Should `TestCcatErrormarkup` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._