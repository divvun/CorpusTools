# Graph Report - CorpusTools  (2026-11-24)

## Corpus Check
- 170 files · ~240,438 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 767 nodes · 958 edges · 192 communities (37 shown, 155 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e2677c22`
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
- NrkNoPage
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
- util.py
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
- sentencedivider.py
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
- PDF2XMLConverter
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
- TestCcatErrormarkup
- .test_process_file_typos
- Exception
- PDFPageMetadata
- pdfconverter.py
- Path
- SamediggiNoPage
- main
- executable_in_path
- pytextcat
- Documentation Dependencies
- PDFPage
- PDFFontspecs
- to_html_elt
- styles
- .handle_syntaxerror
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
2. `NrkNoPage` - 20 edges
3. `Converter` - 19 edges
4. `PrintOptions` - 19 edges
5. `SamediggiNoPage` - 16 edges
6. `process_file()` - 15 edges
7. `NrkNoCrawler` - 14 edges
8. `PDF2XMLConverter` - 14 edges
9. `DupeFinder` - 12 edges
10. `visit_children()` - 11 edges

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

## Communities (192 total, 155 thin omitted)

### Community 4 - "Converter"
Cohesion: 0.07
Nodes (20): Classifier, Converter, newer_group(), Return a boolean indicating if the file is convertable., Return a boolean indicating if the file is convertable., Return a boolean indicating if the file is a gold standard doc., Return the path to the corpus dtd file., Validate the complete document. (+12 more)

### Community 12 - "NrkNoPage"
Cohesion: 0.06
Nodes (23): Crawler, NrkNoCrawler, Collect links from a page., Set the parallels for this set of parallel pages., Get parallel pages for the original page. Args: orig_page: The original page to…, Collect pages from nrk.no., Get article ids from NRK Sápmi. Returns: A set of article ids., Find articles ids of fetched documents. Args: path (str): path to the directory… (+15 more)

### Community 32 - "util.py"
Cohesion: 0.11
Nodes (19): BaseException, basename_noext(), get_lang_resource(), human_readable_filesize(), human_readable_timespan(), ignored(), lineno(), note() (+11 more)

### Community 50 - "avvirdigital.py"
Cohesion: 0.08
Nodes (52): Any, AvvirAuthor, AvvirContainer, AvvirTaggedText, parametrize, AvvirAuthor, AvvirContainer, AvvirDocument (+44 more)

### Community 67 - "analyse_corpus"
Cohesion: 0.20
Nodes (12): add_files_to_corpus, analyse_corpus, ccat, compile_cwb_mono, convert2xml, Scripts Overview, korp_mono, make_training_corpus (+4 more)

### Community 68 - "ccat.py"
Cohesion: 0.06
Nodes (63): Element, ElementTree, SerializedXml, flatten(), Serialize the AvvirDocument to a list of XML elements., Flatten a nested structure of XML elements and sequences., Serialize the AvvirContainer to a list of lists of XML elements., ccatter() (+55 more)

### Community 74 - "sentencedivider.py"
Cohesion: 0.18
Nodes (15): Namespace, corpus_file_to_sentences(), get_tokeniser(), main(), make_sentences(), make_valid_sentences(), parse_options(), Turn tokenised output into cleaned up sentences. Args: tokenised_output: The… (+7 more)

### Community 76 - "DupeFinder"
Cohesion: 0.13
Nodes (13): DupeFinder, find(), main(), parse_finder_options(), parse_remover_options(), Check if the word ratio of two files are nearly equal. Args: filename1 (str):…, Compare two files. Args: filename1 (str): name of the first file. filename2…, Compare all files to each other. Args: remove (bool): Defaults to False. If… (+5 more)

### Community 77 - "TrainingCorpusMaker"
Cohesion: 0.13
Nodes (13): main(), parse_options(), Turn a giella xml into a list of sentences. Args: filename (str): name of the…, Find analysed files. Yields: (str): filename of an analysed file., Make .txt files from .xml files. The .txt files contain only sentences with…, Turn the free and bound corpus into a pytextcat training corpus., Turn the free and bound corpus into a langid training corpus., Parse the options given to the program. (+5 more)

### Community 82 - "TestCcat"
Cohesion: 0.18
Nodes (5): Print only errorort content Check the output of a p element containing two…, Visit only <p type=tablecell> elements when table is True, Default settings, print content of p elements Check the output of plain p…, Print only content of p elements with type=title gets output., TestCcat

### Community 89 - "PDF2XMLConverter"
Cohesion: 0.18
Nodes (10): PDF2XMLConverter, Element, Class to convert the xml output of pdftohtml to Giella xml. Attributes:…, Strip unwanted chars from the document. Args: content: the xml document that…, Replace unwanted strings with correct replacements. Args: content (str):…, Convert from pdf to a corpus xml file. Returns: (lxml.etree.Element): A corpus…, Convert output of pdftohtml to a corpus xml file. Returns:…, Parse the page element. Args: page: a pdf xml page element. (+2 more)

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
Cohesion: 0.18
Nodes (14): main(), move_orig_to_correct(), orig_to_text(), parse_options(), Parse the commandline options. Returns: (argparse.Namespace): the parsed…, Move the original file to a .correct.txt file. Args: orig_file: The original…, Extract the text from a file. Args: orig_file: The original goldstandard file.…, Convert goldstandard files to .correct.txt files. (+6 more)

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

### Community 147 - "TestCcatErrormarkup"
Cohesion: 0.05
Nodes (19): Test hyph tags when hyph_replacement is set to "xml, Test hyph tags when hyph_replacement is set to "-, Test the treatment of two hyph tags in a row, The text before a hyph is the tail of the previous sibling, Test how ccat handles errormarkup, Plain error element, default text flow, Nested error element, default text flow, Plain error element, one word per line output (+11 more)

### Community 149 - "Exception"
Cohesion: 0.17
Nodes (13): Exception, PDFEmptyPageError, Raise this exception if a pdf page is empty., ArgumentError, ConversionError, ExecutableMissingError, Look for programs and files that are needed to do the analysis. If they don't…, This exception is raised when setup is faulty. (+5 more)

### Community 150 - "PDFPageMetadata"
Cohesion: 0.19
Nodes (8): PDFPageMetadata, Read pdf metadata from the metadata file into this class. Compute metadata…, Compute the margins of a page in pixels. Returns: (dict): a dict containing the…, Compute a margin in pixels. Args: margin: the name of the margin Returns:…, Get the width of the margin in percent., Compute inner margins of the document. Returns: (dict): A dict where the key is…, Compute a margin in pixels. Args: margin (str): the name of the margin Returns:…, Get the width of the margin in percent.

### Community 151 - "pdfconverter.py"
Cohesion: 0.24
Nodes (9): handle_br(), is_probably_hyphenated(), merge(), merge_children_of_p(), merge_i(), Find out if previous is part of a hyphenated word. Args: previous: the previous…, Handle br tags in p elements. Args: previous (str): the previous string in…, Merge two paragraph elements into one. (+1 more)

### Community 152 - "Path"
Cohesion: 0.18
Nodes (20): CorpusPath, Path, analyse(), analyse_in_parallel(), analyse_serially(), dependency_analysis(), find_analyser_zpipe(), get_modename() (+12 more)

### Community 153 - "SamediggiNoPage"
Cohesion: 0.06
Nodes (19): Element, Path, This will be the content of the saved file., Extract metadata from the web page., Get the name of the corpus path., Check if the pages seem to have the expected structure., Save a samediggi.no page to the corpus., Get links to the parallels of this document. (+11 more)

### Community 154 - "main"
Cohesion: 0.33
Nodes (6): main(), parse_args(), Parse the commandline options. Returns: (argparse.Namespace): the parsed…, Convert an html file, and print the result to outfile., print_element(), Format an html document. This function formats html documents for readability,…

### Community 155 - "executable_in_path"
Cohesion: 0.33
Nodes (6): executable_in_path(), is_executable(), path_possibilities(), Check if the program in fullpath is executable. Args: fullpath: the path to the…, Check if program is found in $PATH. Args: program (str): name of program of…, Check if program is in path. Args: program: name of the program Returns: True…

### Community 158 - "PDFPage"
Cohesion: 0.22
Nodes (6): PDFPage, Reads a page element. Attributes: textelements (list of PDFTextElements):…, Initialise the PDFPage class. Args: page_element (etree.Element): an etree…, Found out if this page should be skipped. Args: skip_pages: list of the pages…, Check if t is inside the given margins. t is a text element, Pick the wanted text elements from a page. This is the main function of this…

### Community 159 - "PDFFontspecs"
Cohesion: 0.25
Nodes (5): PDFFontspecs, Add font specs found in a pdf page to this class. Attributes: pdffontspecs: map…, Initialise the PDFFontspecs class., Add a pdf2xml fontspec to this class. Args: xmlfontspec: a PDF2XML fontspec…, Return a corrected id of a fontspec. Some xmlfontspecs have different id's for…

### Community 160 - "to_html_elt"
Cohesion: 0.40
Nodes (4): Path, Initialise the PDF2XMLConverte class. Args: filename (str): the path to the pdf…, Convert a pdf document to the Giella xml format. Args: path (str): path to the…, to_html_elt()

### Community 161 - "styles"
Cohesion: 0.50
Nodes (3): Initialise the PDFPageMetadata class. Args: page_id: the page id page_style:…, Turn inline css styles into a dict., styles()

## Knowledge Gaps
- **39 isolated node(s):** `corpustools`, `generate_tables.sh script`, `Original Corpus`, `Korp-ready Files`, `VRT Corpus Files` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **155 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Converter` connect `Converter` to `orig_to_text`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `corpustools`, `generate_tables.sh script`, `Original Corpus` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Converter` be split into smaller, more focused modules?**
  _Cohesion score 0.06906906906906907 - nodes in this community are weakly interconnected._
- **Should `NrkNoPage` be split into smaller, more focused modules?**
  _Cohesion score 0.058279370952821465 - nodes in this community are weakly interconnected._
- **Should `util.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11052631578947368 - nodes in this community are weakly interconnected._
- **Should `avvirdigital.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07597402597402597 - nodes in this community are weakly interconnected._
- **Should `ccat.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06433566433566433 - nodes in this community are weakly interconnected._