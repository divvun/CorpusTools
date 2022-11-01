from setuptools import find_packages, setup

import corpustools.argparse_version

setup(
    name="CorpusTools",
    version=corpustools.argparse_version.version,
    author=(
        "Børre Gaup <borre.gaup@uit.no>, "
        "Kevin Unhammer, "
        "Ciprian Gerstenberger, "
        "Chiara Argese <chiara.argese@uit.no>"
    ),
    packages=find_packages(),
    url="http://github.com/giellalt/CorpusTools",
    license="GPL v3.0",
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": [
            "add_files_to_corpus = corpustools.adder:main",
            "analyse_corpus = corpustools.analyser:main",
            "ccat = corpustools.ccat:main",
            "compare_tmx_goldstandard = corpustools.compare_tmx_goldstandard:main",
            "convert2xml = corpustools.convertermanager:main",
            "debug_corpus = corpustools.debug_corpus:main",
            "generate_anchor_list = corpustools.generate_anchor_list:main",
            "html_cleaner = corpustools.html_cleaner:main",
            "move_corpus_file = corpustools.move_files:main",
            "remove_corpus_file = corpustools.move_files:remove_main",
            "normalise_corpus_names = corpustools.normalise_filenames:main",
            "packagetmx = corpustools.packagetmx:main",
            "paracheck = corpustools.check_para_consistency:main",
            "parallelize = corpustools.parallelize:main",
            "pick_sd_se = corpustools.pick_samediggi_se_docs:main",
            "pytextcat = corpustools.text_cat:main",
            "saami_crawler = corpustools.saami_crawler:main",
            "duperemover = corpustools.dupe_finder:main",
            "dupefinder = corpustools.dupe_finder:find",
            "pick_parallel_docs = corpustools.pick_parallel_docs:main",
            "count_analysed = corpustools.counter:main",
            "clean_prestable = corpustools.clean_prestable:main",
            "reparallelize = corpustools.realign:main",
            "update_metadata = corpustools.update_metadata:main",
            "epubchooser = corpustools.epubchooser:main",
            "make_training_corpus = corpustools.trainingcorpusmaker:main",
            "tmx2html = corpustools.tmx:main",
            "dropbox_adder = corpustools.dropbox_adder:main",
            "korp_mono = corpustools.korp_mono:main",
            "korp_para = corpustools.korp_para:main",
            "bibel_no_aligner = corpustools.bibel_no_aligner:main",
            "bibel_no_crawler = corpustools.bibel_no_crawler:main",
            "ces_to_bibel_no = corpustools.ces2homegrown:main",
        ]
    },
    install_requires=[
        "epub",
        "feedparser",
        "gitdb",
        "gitpython",
        "html5lib",
        "lxml",
        "parameterized",
        "prompt_toolkit",
        "regex",
        "requests",
        "requests-mock",
        "testfixtures",
        "unidecode",
    ],
    test_suite="nose.collector",
    include_package_data=True,
)
