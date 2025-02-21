"""
Take the "korp-ready" files in a "corpus-xxx/korp_mono" directory of a corpus,
and create the binary CWB files (the files that are in data/ and registry/).
"""
import argparse
import builtins
import shutil
import subprocess
import sys
import typing
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from functools import wraps
from itertools import chain
from pathlib import Path
from shlex import split as split_cmd
from time import perf_counter_ns
from typing import Callable

from corpustools.korp_config_template import CORPUS_CONFIG_TITLE_AND_DESCRIPTIONS
from corpustools.korp_config_template import DEFAULT_MODE_CONTENTS
from corpustools.korp_config_template import KORP_SETTINGS_TEMPLATE


Module = typing.Literal["converted", "analysed", "korp_mono"]
LANGS = set(
    "fao fit fkv koi kpv mdf mhr mrj myv olo sma sme smj smn sms udm vep vro".split()
)


def noop(*_args, **_kwargs):
    pass


def abort(*msg, sep=" "):
    prog = Path(sys.argv[0]).name
    sys.exit(f"{prog}: critical: {sep.join(msg)}")


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        t0 = perf_counter_ns()
        res = f(*args, **kwargs)
        t = round((perf_counter_ns() - t0) / 1_000_000)
        print(f"done ({t}ms)")
        return res

    return wrapper


def corpusname(lang: str, origs=False, openorclosed="open"):
    """The name of a corpus directory for a given lang,
    whether or not it is origs, or open or closed."""
    if openorclosed != "open" and openorclosed != "closed":
        raise ValueError("openorclosed must be 'open' or 'closed'")

    match (origs, openorclosed):
        case (True, "closed"):
            return f"corpus-{lang}-orig-x-closed"
        case (False, "closed"):
            return f"corpus-{lang}-x-closed"
        case (True, "open"):
            return f"corpus-{lang}-orig"
        case (False, "open"):
            return f"corpus-{lang}"


def clean_directory(directory: Path, verbose: int):
    assert isinstance(directory, Path)
    if verbose:
        print(f"cleaning directory {directory}...", end="")
    try:
        shutil.rmtree(directory)
    except FileNotFoundError:
        pass
    directory.mkdir(parents=True, exist_ok=True)
    if verbose:
        print("done")


@dataclass
class Category:
    """A category in a stage of a corpora.
    The category may exist in only the open, or the closed
    corpora, or both.
    corpus-xxx[-x-closed]/STAGE/CATEGORY
    """
    lang: str
    # "converted", "analysed", "korp_mono", etc...
    stage: str
    # "admin", "blogs", "facta", "ficit", "laws", etc...
    category: str

    # the original path to where all corpus-xxx directories
    # are kept
    root: Path

    # does this category exist in the open corpora? what about
    # in the closed?
    # invariant: both cannot be False at the same time
    #   (that would mean there is no such category)
    in_open: bool
    in_closed: bool

    def __post_init__(self):
        if not self.in_open and not self.in_closed:
            raise ValueError("either in_open must be true, or in_closed must be true, or both. they cannot both be False")

    def directory(self, openorclosed):
        """The Path to the category directory in the open corpora."""
        cn = corpusname(self.lang, False, openorclosed)
        return self.root / cn / self.stage / self.category

    def files(self, suffix=""):
        glob = f"**/*{suffix}"
        if self.in_open:
            yield from self.directory("open").glob(glob)
        if self.in_closed:
            yield from self.directory("closed").glob(glob)


@dataclass
class Corp:
    lang: str
    root: Path

    @classmethod
    def from_root_and_lang(cls, root: Path, lang: str):
        root = root.resolve()
        open_corp = root / corpusname(lang, False, "open")
        closed_corp = root / corpusname(lang, False, "closed")
        has_open = open_corp.is_dir()
        has_closed = closed_corp.is_dir()
        if has_open or has_closed:
            return cls(lang, root)

    def categories(self, stage: str):
        """Get all categories for a stage, that is, the set
        of all subdirectories in both the open and closed
        corpora of this language. That would be all of these
        subdirectories:
           corpus-{self.lang}/{stage}/SUBDIR
           corpus-{self.lang}-x-closed/{stage}/SUBDIR
        """

        # this gives you the category, but you don't know if
        # that category exists in the open corpora, the closed,
        # or both, so the caller will have to check

        d = defaultdict(list)  # name -> [open_path, closed_path]
        for oc in ("open", "closed"):
            this_corp_name = corpusname(self.lang, False, oc)
            thiscorp = self.root / this_corp_name

            stage_dir = thiscorp / stage
            if not stage_dir.is_dir():
                # stage doesn't exist here
                continue

            for category in stage_dir.iterdir():
                if not category.is_dir():
                    # not expecting to find a file here..
                    continue
                name = category.name
                d[name].append(oc)

        for name, ocs in d.items():
            in_open = in_closed = False
            for oc in ocs:
                if oc == "open":
                    in_open = True
                elif oc == "closed":
                    in_closed = True

            yield Category(
                self.lang,
                stage,
                name,
                self.root,
                in_open,
                in_closed,
            )


@dataclass
class Corpus:
    # The original path that was given to us. This is kept because if only
    # a specific directory is given, we only want to recurse starting from
    # that directory. If only a single file is given, we only want to
    # process that single file
    path: Path

    lang: str

    # directory where corpus-LANG[-orig][-x-closed] directories is stored
    root_dir: Path

    # the path to the orig folder
    orig_dir: Path

    # the path to the other folder (the ones with converted, analysed, etc)
    processed_dir: Path

    # is the corpora a closed one (i.e. "not open", one that uses source
    # material bound by copyright or such things)
    closed: bool

    # Which module we have selected, module being "converted", "analysed", etc
    module: Module | None

    # which category we have selected, if any
    category: str | None = None

    # a specific subpath inside of the category that is selected.
    # if given, only recurses from this directory
    subpath: str | None = None

    def has_module(self, module: Module):
        """Returns True if this corpus has module `module`, else False"""
        return (self.processed_dir / module).is_dir()

    @staticmethod
    def from_path(path):
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve(strict=True)

        info = Corpus._find_corpus_folder(path)
        return Corpus(*info)

    @staticmethod
    def _find_corpus_folder(path):
        """Find the corpus directory in the given path.

        Args:
            path (pathlib.Path): the path to search

        Raises:
            ValueError: if no corpus directory was found

        Returns:
            (tuple): The result
        """
        parts = path.parts
        for idx, folder in enumerate(parts):
            if len(folder) >= 7 and folder.startswith("corpus-"):
                try:
                    # str.index() ValueError's on substring not found
                    lang = folder[7:folder.index("-", 7)]
                except ValueError:
                    lang = folder[7:]

                closed = folder.endswith("-x-closed")
                root_dir = Path(*parts[0:idx])
                if not closed:
                    orig_dir = root_dir / f"corpus-{lang}-orig"
                    processed_dir = root_dir / f"corpus-{lang}"
                else:
                    orig_dir = root_dir / f"corpus-{lang}-orig-x-closed"
                    processed_dir = root_dir / f"corpus-{lang}-x-closed"

                module = None if idx + 1 >= len(parts) else parts[idx + 1]
                category = None if idx + 2 >= len(parts) else parts[idx + 2]
                subpath = None if idx + 3 >= len(parts) else Path(*parts[idx + 3 :])

                return (
                    path,
                    lang,
                    root_dir,
                    orig_dir,
                    processed_dir,
                    closed,
                    module,
                    category,
                    subpath,
                )

        raise ValueError(
            f"no corpus directory found in path {Path(*parts)}\n"
            "Hint: The first folder in the path that is named in the form "
            "'corpus-LANG[...]' (LANG being the language code), is "
            "considered the corpus directory. In the path given, no such "
            "folder was found"
        )

    def categories(self):
        """Yields category dictionaries"""
        if self.category:
            # only a specific category selected, so only yield one result
            yield self
        else:
            # iterate over all categories in CORPUS_ROOT/corpus-xxx/korp/<category>
            for p in (self.processed_dir / "korp_mono").iterdir():
                yield Corpus(
                    path=self.path,
                    lang=self.lang,
                    root_dir=self.root_dir,
                    orig_dir=self.orig_dir,
                    processed_dir=self.processed_dir,
                    closed=self.closed,
                    module="korp_mono",
                    category=p.parts[-1],
                    subpath=None,
                )

    def iter_files(self, suffix=""):
        directory = self.processed_dir
        if self.module:
            directory /= self.module
        if self.category:
            directory /= self.category
        if self.subpath is not None:
            directory /= self.subpath
        yield from directory.glob(f"**/*{suffix}")


# class CorpusDirectory(argparse.Action):
#     """The type of the *directory* argument. Checks that folder exists,
#     and determines how the *class:Corpus* should be built."""
#
#     def __init__(self, option_strings, dest, nargs=None, const=None,
#                  default=None, type=None, choices=None, required=False,
#                  help=None, metavar=None):
#         help = (
#             "the path of the corpus directory to compile CWB files for, "
#             "or a subdirectory thereof"
#         )
#         print("CorpusDirectory argparse Action __init__")
#         super().__init__(option_strings, dest, default=".", type=Path, help=help)
#
#     def __call__(self, parser, namespace, values, option_string=None):
#         print("CorpusDirectory argparse Action __call__")
#         path = values
#         try:
#             corpus = Corpus.from_path(path)
#         except Exception as e:
#             parser.error(f"{sys.argv[0]}: error: argument `{self.dest}`: {e}\n")
#         setattr(namespace, self.dest, corpus)


def run_subcommand(
    cmd: list[str] | str,
    # callable that is given the CompletedProcess object, and
    # from that determines if the call was a success, or not.
    # Defaults to considering it a success if return code was 0.
    considered_success: Callable[
        [subprocess.CompletedProcess], bool
    ] = lambda proc: proc.returncode == 0,
    verbose: bool = False,
    check: bool = False,
):
    print = builtins.print if verbose else noop
    if isinstance(cmd, str):
        cmd = split_cmd(cmd)

    print("running subcommand:\n  ", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, check=check)
    is_success = considered_success(proc)
    print("ok." if is_success else "failed.", end=" ")
    print(f"return code: {proc.returncode}")
    stdout = proc.stdout.splitlines(keepends=False)
    stderr = proc.stderr.splitlines(keepends=False)
    print("stdout: (stdout was empty)" if not stdout else "stdout:")
    for line in stdout:
        print(">>>", line)
    print("stderr: (stderr was empty)" if not stderr else "stderr:")
    for line in stderr:
        print(">>>", line)

    return is_success


def process_input_xml2(root, category, text_num):
    texts = root.findall("[sentence]")
    if not texts:
        return None, 0, 0
    if len(texts) != 1:
        # TODO does this ever happen? if so, what to do? fail? take only first?
        print(f"MORE THAN 1 TEXT! ({len(texts)})")
        pass

    # note: assuming only 1 <text> element in each file (only processing the first)
    text_el = texts[0]
    text_el.attrib["id"] = f"{category}_t{text_num}"
    n_tot_tokens = 0
    for sentence_num, sentence_el in enumerate(root.findall("sentence"), start=1):
        sentence_el.attrib["id"] = f"{category}_t{text_num}_s{sentence_num}"
        inner_text = "".join(sentence_el.itertext())
        token_count = inner_text.count("\n")
        sentence_el.attrib["token_count"] = str(token_count - 1)
        n_tot_tokens += token_count
    text_el.attrib["sentence_count"] = str(sentence_num)
    text_el.attrib["token_count"] = str(n_tot_tokens)
    return text_el, sentence_num, n_tot_tokens


def concat_corpus(corpus, lang, compiled_dir, date_s):
    clean_directory(compiled_dir, verbose=1)

    print("Gathering korp_mono files in both open and closed corpus...")
    categories = {}
    for category in corpus.categories("korp_mono"):
        corpus_id = f"{lang}_{category.category}_{date_s}"
        files = list(category.files(suffix=".xml"))
        categories[corpus_id] = (category, files)

    n_total_files = sum(len(files) for (_, files) in categories.values())
    n_processed_files = 0

    print(f"Found {n_total_files} files")

    for corpus_id, (category, files) in categories.items():
        rem = n_total_files - n_processed_files - len(files)
        print(f"{corpus_id}: concatenating {len(files)} files... ({rem} files remains)")
        root_element = ET.Element("corpus")
        root_element.attrib["id"] = corpus_id
        n_tot_sentences, n_tot_tokens = 0, 0
        text_num = 1
        for i, file in enumerate(files):
            n_processed_files += 1

            try:
                root = ET.parse(file)
            except ET.ParseError as e:
                print(f"file {file} could not be parsed (invalid xml?). ET says: {e}")
                continue

            text_el, nsentences, ntokens = process_input_xml2(
                    root, category.category, text_num)
            if not text_el:
                print(f"file {file} contained no <text> element")
                continue
            root_element.append(text_el)
            n_tot_sentences += nsentences
            n_tot_tokens += ntokens

        ET.indent(root_element, "")
        with open(Path(compiled_dir / f"{corpus_id}.vrt"), "w") as f:
            f.write(ET.tostring(root_element, encoding="unicode"))


def process_input_xml(file, category, text_num):
    xml = ET.parse(file)
    texts = xml.findall("[sentence]")
    if not texts:
        return None, 0, 0
    if len(texts) > 1:
        # TODO does this ever happen? if so, what to do? fail? take only first?
        pass

    # note: assuming only 1 <text> element in each file (only processing the first)
    text_el = texts[0]
    text_el.attrib["id"] = f"{category}_t{text_num}"
    n_tot_tokens = 0
    for sentence_num, sentence_el in enumerate(xml.findall("sentence"), start=1):
        sentence_el.attrib["id"] = f"{category}_t{text_num}_s{sentence_num}"
        inner_text = "".join(sentence_el.itertext())
        token_count = inner_text.count("\n")
        sentence_el.attrib["token_count"] = str(token_count - 1)
        n_tot_tokens += token_count
    text_el.attrib["sentence_count"] = str(sentence_num)
    text_el.attrib["token_count"] = str(n_tot_tokens)
    return text_el, sentence_num, n_tot_tokens


def cwb_huffcode(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("compressing token files (cwb-huffcode)...")
    cmd = [
        f"{cwb_binaries_directory}/cwb-huffcode",
        "-r",
        f"{registry_dir}",
        "-A",
        upper_corpus_name,
    ]
    ok = run_subcommand(cmd)
    if not ok:
        raise Exception("error: cwb_huffcode() returned non-0")


def cwb_compress_rdx(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("compressing indexes (cwb-compress-rdx)...")
    cmd = [
        f"{cwb_binaries_directory}/cwb-compress-rdx",
        "-r",
        f"{registry_dir}",
        "-A",
        upper_corpus_name,
    ]
    ok = run_subcommand(cmd)
    if not ok:
        raise Exception("error: cwb_compress_rx() returned non-0")


def rm_unneeded_data_files(data_dir, corpus_name):
    print(
        "deleting non-compressed files (*.rev, *.rdx, *.corpus) from data "
        f"dir of corpus {corpus_name}...",
    )
    d = data_dir / corpus_name
    for file in chain(d.glob("*.rev"), d.glob("*.rdx"), d.glob("*.corpus")):
        file.unlink()


def read_vrt_xml(vrt_file):
    """Read a (xml based) .vrt file, and return the number of sentences it
    contains, as well as the first and last date of the texts"""
    xml_root = ET.parse(vrt_file)
    dates = []
    for text_el in xml_root.findall("text"):
        datefrom = text_el.attrib["datefrom"]
        if datefrom:
            try:
                dates.append(date.fromisoformat(datefrom))
            except ValueError:
                pass
    n_sentences = len(xml_root.findall("sentence"))

    dates.sort()
    first_date = dates[0] if dates else None
    last_date = dates[-1] if dates else None

    return n_sentences, first_date, last_date


def update_registry(registry_dir, corpus_name, descriptive_name, lang):
    print(f"Updating registry {corpus_name}...")
    file = registry_dir / corpus_name
    if file.is_file():
        text = file.read_text()
        updated_text = []

        for line in text.split("\n"):
            if line == 'NAME ""':
                updated_text.append(f'NAME "{descriptive_name}"')
            elif line == 'language = "??"':
                updated_text.append(f'language = "{lang}"')
            else:
                updated_text.append(line)
        updated_text = "\n".join(updated_text)

        file.write_text(updated_text)


def scaffold_korp_config(korp_config_dir, lang):
    # Delete anything that may have been there from a previous run
    shutil.rmtree(korp_config_dir)

    # copy in the template structure
    template_dir = Path(__file__).parent / "korp_config_template"
    shutil.copytree(template_dir, korp_config_dir)

    # Fill in modes/default.yaml
    try:
        default_mode_contents = DEFAULT_MODE_CONTENTS[lang]
    except KeyError:
        default_mode_contents = DEFAULT_MODE_CONTENTS["__DEFAULT__"]
    with open(korp_config_dir / "modes" / "default.yaml", "w") as f:
        f.write(default_mode_contents)


def create_korp_settings(korp_config_dir, vrt_file):
    """Create the Korp backend corpus config-.yaml file that Korp needs, i.e.
    KORP_CORPUS_CONFIG_DIR/corpora/LANG_CATEGORY_DATE.yaml

    Fill it with default values
    """
    category = vrt_file.name.split("_")[1]  # lang_category_date
    title_and_description = CORPUS_CONFIG_TITLE_AND_DESCRIPTIONS.get(
        category,
        CORPUS_CONFIG_TITLE_AND_DESCRIPTIONS["__DEFAULT__"],
    )
    corpus_id = vrt_file.stem
    file_contents = KORP_SETTINGS_TEMPLATE.format(
        corpus_id=corpus_id,
        title_and_description=title_and_description,
    )
    file = (korp_config_dir / "corpora" / vrt_file.name).with_suffix(".yaml")
    print(f"Write korp-backend yaml config to {file}")
    with open(file, "w") as f:
        f.write(file_contents)


def cwb_encode(
    cwb_binaries_directory,
    vrt_file,
    corpus_name,
    data_dir,
    registry_dir,
):
    print("Converting to CWB binary format (cwb-encode)...")
    cmd = [
        f"{cwb_binaries_directory}/cwb-encode",
        # skip empty lines in input data
        "-s",
        # xml format
        "-x",
        # no default p attribute (we specify the first one with -P word below)
        "-p",
        "-",
        # data directory
        "-d",
        f"{data_dir}/{corpus_name}",
        # registry directory
        "-R",
        f"{registry_dir}/{corpus_name}",
        # character set
        "-c",
        "utf8",
        # which .vrt file to encode
        "-f",
        f"{vrt_file}",
        # positional attributes
        "-P",
        "word",
        "-P",
        "lemma",
        "-P",
        "pos",
        "-P",
        "msd",
        "-P",
        "ref",
        "-P",
        "deprel",
        "-P",
        "dephead",
        # structural attributes
        "-S",
        "sentence:0+id+token_count",
        "-S",
        "text:0+id+title+lang+orig_lang+gt_domain+first_name+last_name"
        "+nationality+date+datefrom+dateto+timefrom+timeto"
        "+sentence_count+token_count",
        "-S",
        "corpus:0+id",
    ]
    if not run_subcommand(cmd):
        raise RuntimeError("cwb_encode() failed")


def cwb_makeall(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("create lexicon and index (cwb-makeall)...")
    cmd = [
        f"{cwb_binaries_directory}/cwb-makeall",
        "-D",
        "-r",
        f"{registry_dir}",
        f"{upper_corpus_name}",
    ]
    try:
        run_subcommand(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("failed")
        print(e.stdout)
        print(e.stderr)
        raise e


def encode_corpus(
    vrt_file: Path,
    date: date,
    lang: str,
    data_dir: Path,
    registry_dir: Path,
    cwb_binaries_directory: Path,
):
    """Run the CWB tools on the given folder that contains .vrt files, to
    create the data/ and registry/ folder contents for a corpus.

    Args:
        vrt_directory (Path): the output directory from the previous steps,
            that contains a .vrt file for a corpus.
        date (date): The date that we created this corpus
        lang (str): which language this corpus is in. 3-letter language code
        cwb_binaries_directory (Path): path to where the CWB binaries are
            located
        target_directory (Path): path to the directory where the
            final encoded corpus resides (the directory that has subfolders
            data/ and registry/)
    """

    n_sentences, first_date, last_date = read_vrt_xml(vrt_file)
    corpus_name = vrt_file.name[: vrt_file.name.index(".")]
    upper_corpus_name = corpus_name.upper()
    # in metadata: id name title description lang updated
    # TODO this is supposed to be the "NAME" field in the file registry/<corpus>/<id>

    # sh loc_encode_gt_corpus_20181106.sh "$input_data" "$date" "$ln" "$lang_code" "$corpus_name" "$fd" "$ld"

    corpus_data_dir = data_dir / corpus_name
    corpus_data_dir.mkdir(parents=True, exist_ok=True)
    with open(corpus_data_dir / ".info", "w") as f:
        f.write(
            f"Sentences: {n_sentences}\nUpdated: {date}\n"
            f"FirstDate: {first_date}\nLastDate: {last_date}\n"
        )

    cwbbindir = cwb_binaries_directory
    cwb_encode(
        cwbbindir, vrt_file, corpus_name, data_dir, registry_dir
    )
    cwb_makeall(cwbbindir, registry_dir, upper_corpus_name)
    cwb_huffcode(cwbbindir, registry_dir, upper_corpus_name)
    cwb_compress_rdx(cwbbindir, registry_dir, upper_corpus_name)
    rm_unneeded_data_files(data_dir, corpus_name)
    DESCRIPTIVE_NAME = "DESCRIPTIVE " + corpus_name
    update_registry(registry_dir, corpus_name, DESCRIPTIVE_NAME, lang)
    # create_korp_settings()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lang",
        choices=LANGS,
        help="which language to compile cwb mono files of",
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=".",
        help="path to directory containing the where corpus-[...] directories."
    )
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help=(
            "Date of compilation, the date the corpus was analysed, in ISO "
            "8601 format (YYYYMMDD). See datetime.date.fromisoformat(). "
            "Defaults to today's date."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--cwb-binaries-dir",
        type=Path,
        default=Path(shutil.which("cwb-encode")).parent,
        help="directory where the cwb binaries (such as cwb-encode, etc) "
        "are located. Only necessary if the `cwb-xxx` commands are not "
        "available on the system path",
    )

    args = parser.parse_args()

    cwb_progs = [
        shutil.which(f"cwb-{prog}", path=args.cwb_binaries_dir)
        for prog in ("encode", "makeall", "huffcode", "compress-rdx")
    ]
    if not all(cwb_progs):
        parser.print_usage()
        if args.cwb_binaries_dir is None:
            print(
                "critical: cannot find the cwb binaries on the system path, "
                "either add the path to the cwb binaries to the PATH, or "
                "specify the directory explicitly with --cwb-binaries-dir"
            )
        else:
            print(
                "critical: cannot find the cwb binaries in the given folder"
                f" ({args.cwb_binaries_dir.resolve()})"
            )
        parser.exit(1)

    args.cwb_binaries_dir = Path(cwb_progs[0]).parent

    return args


def main():
    args = parse_args()

    corpus = Corp.from_root_and_lang(args.root_dir, args.lang)
    args.root_dir = args.root_dir.resolve()
    if not corpus:
        open_name = corpusname(args.lang, False, "open")
        closed_name = corpusname(args.lang, False, "closed")
        abort(
            f"no corpora for language {args.lang}\nneither "
            f"directory {open_name} nor {closed_name} found "
            f"in {args.root_dir}"
        )
    target_dir = args.root_dir / "cwb-files" / args.lang
    clean_directory(target_dir, verbose=args.verbose)
    (target_dir / "data").mkdir(exist_ok=True)
    (target_dir / "registry").mkdir(exist_ok=True)

    date_s = str(args.date).replace("-", "")
    vrt_dir = Path(f"vrt/vrt_{args.lang}_{date_s}")
    concat_corpus(corpus, args.lang, vrt_dir, date_s)

    data_dir = args.root_dir / "cwb-files" / args.lang / "data"
    registry_dir = args.root_dir / "cwb-files" / args.lang / "registry"
    clean_directory(data_dir, verbose=1)
    clean_directory(registry_dir, verbose=1)

    korp_config_dir = args.root_dir / "korp_configs" / args.lang
    scaffold_korp_config(korp_config_dir, args.lang)

    for entry in vrt_dir.glob("*.vrt"):
        print(f"encode_corpus {entry.name}...")
        encode_corpus(
            vrt_file=entry,
            date=args.date,
            lang=args.lang,
            data_dir=data_dir,
            registry_dir=registry_dir,
            cwb_binaries_directory=args.cwb_binaries_dir,
        )
        create_korp_settings(
            korp_config_dir,
            entry,
        )


if __name__ == "__main__":
    raise SystemExit(main())
