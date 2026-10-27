# Graph Report - CorpusTools  (2026-10-27)

## Corpus Check
- 176 files · ~246,094 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 251 nodes · 166 edges · 141 communities (16 shown, 125 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9fd3a9d5`
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
- Path
- expand
- Element
- CorpusPath
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
2. `convert_tagged_text()` - 8 edges
3. `convert_container()` - 8 edges
4. `remove_control_chars()` - 7 edges
5. `extract_captions()` - 7 edges
6. `extract_slideshows()` - 7 edges
7. `extract_authors()` - 6 edges
8. `extract_main_content()` - 6 edges
9. `extract_quotes()` - 6 edges
10. `extract_containers()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `dupefinder` --semantically_similar_to--> `duperemover`  [INFERRED] [semantically similar]
  docs/docs/scripts/dupefinder.md → docs/docs/scripts/duperemover.md
- `move_corpus_file` --semantically_similar_to--> `remove_corpus_file`  [INFERRED] [semantically similar]
  docs/docs/scripts/move_corpus_file.md → docs/docs/scripts/remove_corpus_file.md
- `add_files_to_corpus` --conceptually_related_to--> `normalise_corpus_names`  [INFERRED]
  docs/docs/scripts/add_files_to_corpus.md → docs/docs/scripts/normalise_corpus_names.md
- `ccat` --references--> `analyse_corpus`  [EXTRACTED]
  docs/docs/scripts/ccat.md → docs/docs/scripts/analyse_corpus.md
- `korp_mono` --conceptually_related_to--> `analyse_corpus`  [EXTRACTED]
  docs/docs/scripts/korp_mono.md → docs/docs/scripts/analyse_corpus.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Corpus Processing Flow** — docs_docs_howitworks_original_corpus, docs_docs_howitworks_convert2xml, docs_docs_howitworks_processed_corpus, docs_docs_howitworks_analyse_corpus, docs_docs_howitworks_korp_mono [EXTRACTED 1.00]
- **Timespan Update Workflow** — korp_scripts_timedata_readme_timestamp_extraction, korp_scripts_timedata_readme_saxon_transformation, korp_scripts_timedata_readme_timespan_sql_generation, korp_scripts_timedata_readme_mysql_timespan_import [EXTRACTED 1.00]
- **CWB Build Flow** — korp_scripts_update_mono_readme_compile_cwb_files, korp_scripts_update_mono_readme_korp_ready_files, korp_scripts_update_mono_readme_cwb_binary_files, korp_scripts_update_mono_readme_korp_corpus_configuration [EXTRACTED 1.00]
- **Word Picture Setup** — korp_scripts_word_picture_readme_korp_database, korp_scripts_word_picture_readme_word_picture_tables, korp_scripts_word_picture_readme_relations_sql, korp_scripts_word_picture_readme_insert_py [EXTRACTED 1.00]
- **Parallel Corpus Alignment Workflow** — docs_docs_scripts_convert2xml_documentation, docs_docs_scripts_parallelize_documentation, docs_docs_scripts_reparallelize_documentation, docs_docs_scripts_tmx2html_documentation [INFERRED 0.85]
- **Corpus to Korp Processing Pipeline** — docs_docs_scripts_convert2xml_documentation, docs_docs_scripts_analyse_corpus_documentation, docs_docs_scripts_korp_mono_documentation, docs_docs_scripts_compile_cwb_mono_documentation [INFERRED 0.95]

## Communities (141 total, 125 thin omitted)

### Community 12 - "flatten"
Cohesion: 0.13
Nodes (14): Element, Path, SerializedXml, AvvirContainer, AvvirDocument, convert2intermediate(), flatten(), A class representing an Ávvir document. (+6 more)

### Community 50 - "avvirdigital.py"
Cohesion: 0.13
Nodes (32): Any, AvvirAuthor, AvvirTaggedText, convert_author(), convert_container(), convert_image(), convert_slideshow(), convert_tagged_text() (+24 more)

### Community 67 - "analyse_corpus"
Cohesion: 0.15
Nodes (15): add_files_to_corpus, analyse_corpus, ccat, compile_cwb_mono, convert2xml, Scripts Overview, korp_mono, make_training_corpus (+7 more)

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
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `AvvirTaggedText` connect `avvirdigital.py` to `flatten`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `convert2intermediate()` connect `flatten` to `avvirdigital.py`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **What connects `generate_tables.sh script`, `corpustools`, `Original Corpus` to the rest of the system?**
  _38 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `flatten` be split into smaller, more focused modules?**
  _Cohesion score 0.1323529411764706 - nodes in this community are weakly interconnected._
- **Should `avvirdigital.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1319073083778966 - nodes in this community are weakly interconnected._