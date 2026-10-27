# Graph Report - CorpusTools  (2026-10-27)

## Corpus Check
- 176 files · ~245,803 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 265 nodes · 197 edges · 143 communities (18 shown, 125 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8888141f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- XMLTester
- Exception
- BookChapter
- Element
- Classifier
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
- CorpusPath
- GenerateAnchorList
- HtmlElement
- ParseResult
- Pattern
- Element
- StringIO
- Exception
- UnicodeDecodeError
- test_avvirdigital.py
- Path
- expand
- Element
- CorpusPath
- convert_author
- Element
- Path
- Exception
- BaseException
- _Element
- CorpusPath
- ElementTree
- _Element
- Element
- expand
- Element
- Path
- Element
- Element
- analyse_corpus
- compile_cwb_files.py
- run_para_corpus_encoding.sh script
- insert.py
- Element
- Element
- Exception
- expand
- Classifier
- insert.py
- setter
- XMLTester
- Saxon Transformation
- loc_encode_gt_corpus_20181106.sh script
- CorpusTools Release History
- Documentation Deployment Workflow
- Corpus Tools
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
1. `AvvirTaggedText` - 10 edges
2. `convert_tagged_text()` - 10 edges
3. `convert_author()` - 8 edges
4. `convert_container()` - 8 edges
5. `convert_image()` - 8 edges
6. `convert_slideshow()` - 7 edges
7. `extract_captions()` - 7 edges
8. `extract_slideshows()` - 7 edges
9. `remove_control_chars()` - 7 edges
10. `flatten()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `test_control_chars_are_removed()` --calls--> `convert_tagged_text()`  [INFERRED]
  tests/test_avvirdigital.py → src/corpustools/avvirdigital.py
- `test_extract_faktatittel()` --calls--> `convert_tagged_text()`  [INFERRED]
  tests/test_avvirdigital.py → src/corpustools/avvirdigital.py
- `test_extract_image()` --calls--> `convert_image()`  [INFERRED]
  tests/test_avvirdigital.py → src/corpustools/avvirdigital.py
- `test_extract_slideshow()` --calls--> `convert_slideshow()`  [INFERRED]
  tests/test_avvirdigital.py → src/corpustools/avvirdigital.py
- `test_control_chars_are_removed_from_image_and_author()` --calls--> `convert_image()`  [INFERRED]
  tests/test_avvirdigital.py → src/corpustools/avvirdigital.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Corpus Processing Flow** — docs_docs_howitworks_original_corpus, docs_docs_howitworks_convert2xml, docs_docs_howitworks_processed_corpus, docs_docs_howitworks_analyse_corpus, docs_docs_howitworks_korp_mono [EXTRACTED 1.00]
- **Timespan Update Workflow** — korp_scripts_timedata_readme_timestamp_extraction, korp_scripts_timedata_readme_saxon_transformation, korp_scripts_timedata_readme_timespan_sql_generation, korp_scripts_timedata_readme_mysql_timespan_import [EXTRACTED 1.00]
- **CWB Build Flow** — korp_scripts_update_mono_readme_compile_cwb_files, korp_scripts_update_mono_readme_korp_ready_files, korp_scripts_update_mono_readme_cwb_binary_files, korp_scripts_update_mono_readme_korp_corpus_configuration [EXTRACTED 1.00]
- **Word Picture Setup** — korp_scripts_word_picture_readme_korp_database, korp_scripts_word_picture_readme_word_picture_tables, korp_scripts_word_picture_readme_relations_sql, korp_scripts_word_picture_readme_insert_py [EXTRACTED 1.00]
- **Parallel Corpus Alignment Workflow** — docs_docs_scripts_convert2xml_documentation, docs_docs_scripts_parallelize_documentation, docs_docs_scripts_reparallelize_documentation, docs_docs_scripts_tmx2html_documentation [INFERRED 0.85]
- **Corpus to Korp Processing Pipeline** — docs_docs_scripts_convert2xml_documentation, docs_docs_scripts_analyse_corpus_documentation, docs_docs_scripts_korp_mono_documentation, docs_docs_scripts_compile_cwb_mono_documentation [INFERRED 0.95]

## Communities (143 total, 125 thin omitted)

### Community 12 - "flatten"
Cohesion: 0.15
Nodes (12): Element, Path, SerializedXml, AvvirDocument, convert2intermediate(), flatten(), A class representing an Ávvir document., Serialize the AvvirDocument to a list of XML elements. (+4 more)

### Community 50 - "avvirdigital.py"
Cohesion: 0.15
Nodes (28): Any, AvvirContainer, AvvirTaggedText, convert_container(), convert_image(), convert_slideshow(), convert_tagged_text(), extract_captions() (+20 more)

### Community 67 - "analyse_corpus"
Cohesion: 0.15
Nodes (15): add_files_to_corpus, analyse_corpus, ccat, compile_cwb_mono, convert2xml, Scripts Overview, korp_mono, make_training_corpus (+7 more)

### Community 77 - "test_avvirdigital.py"
Cohesion: 0.31
Nodes (10): AvvirContainer, AvvirTaggedText, parametrize, _sample_container(), test_container_serialize_flattens_nested_containers(), test_control_chars_are_removed(), test_document_serialize_flattens_nested_containers(), test_extract_faktatittel() (+2 more)

### Community 82 - "convert_author"
Cohesion: 0.28
Nodes (9): AvvirAuthor, AvvirAuthor, convert_author(), extract_authors(), Extract the authors from an Ávvir JSON dictionary., Convert an Ávvir author to AvvirAuthor. Args: fullname: the full name of the…, A class representing an Ávvir author., test_control_chars_are_removed_from_image_and_author() (+1 more)

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

## Knowledge Gaps
- **38 isolated node(s):** `generate_tables.sh script`, `corpustools`, `Original Corpus`, `Korp-ready Files`, `VRT Corpus Files` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **125 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `flatten()` connect `flatten` to `avvirdigital.py`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `AvvirTaggedText` connect `avvirdigital.py` to `flatten`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `convert_tagged_text()` connect `avvirdigital.py` to `test_avvirdigital.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `convert_tagged_text()` (e.g. with `test_control_chars_are_removed()` and `test_extract_faktatittel()`) actually correct?**
  _`convert_tagged_text()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `convert_author()` (e.g. with `test_control_chars_are_removed_from_image_and_author()` and `test_extract_author()`) actually correct?**
  _`convert_author()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `generate_tables.sh script`, `corpustools`, `Original Corpus` to the rest of the system?**
  _38 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `avvirdigital.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14942528735632185 - nodes in this community are weakly interconnected._