"""
Take the "korp-ready" files in a "corpus-xxx/korp_mono" directory of a corpus,
and create the binary CWB files (the files that are in data/ and registry/).
"""
import argparse
import builtins
import subprocess
import typing
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from functools import wraps
from itertools import chain
from pathlib import Path
from textwrap import dedent
from time import perf_counter_ns
from typing import Callable

Module = typing.Literal["converted", "analysed", "korp_mono"]
LANGS = set(
    "fao fit fkv koi kpv mdf mhr mrj myv olo " "sma sme smj smn sms udm vep vro".split()
)


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        t0 = perf_counter_ns()
        res = f(*args, **kwargs)
        t = round((perf_counter_ns() - t0) / 1_000_000)
        print(f"done ({t}ms)")
        return res

    return wrapper


def remove_directory_contents(directory):
    # This isn't recursive, but for this purpose it doesn't have to be, so
    # I just kept it as simple as I could
    for entry in directory.iterdir():
        if entry.is_dir():
            for subentry in entry.iterdir():
                subentry.unlink()
            entry.rmdir()
        else:
            entry.unlink()


@dataclass
class Corpus:
    # The original path that was given to us. This is kept because if only
    # a specific directory is given, we only want to recurse starting from
    # that directory. If only a single file is given, we only want to
    # process that single file
    path: Path

    lang: str

    # root corpus directory (some people call it "corpus", other "corpora",
    # others maybe "giella-corpora", who knows)
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
                    lang_end_index = folder.index("-", 7)
                    lang = folder[7 : lang_end_index + 1]
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


def _default_success(completed_process: subprocess.CompletedProcess):
    return completed_process.returncode == 0


def run_subcommand(
    cmd: list[str],
    considered_success: Callable[
        [subprocess.CompletedProcess], bool
    ] = _default_success,
    verbose: bool = False,
    check: bool = False,
):
    def noop(*_args, **_kwargs):
        pass

    print = builtins.print if verbose else noop

    print("running subcommand:\n  ", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, check=check)
    is_success = considered_success(proc)
    print("done." if proc.returncode == 0 else "failed.", end=" ")
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


@timed
def concat_corpus(corpus, date, parallel=None):
    """Concatenate all the vrt files in a corpus, and store it in one file.

    This function replaces what the compile_corpus.xsl script does.
    """
    print("Concatenating corpora...")
    date_s = str(date).replace("-", "")
    compiled_directory = Path(f"vrt_{corpus.lang}_{date_s}")
    if compiled_directory.exists():
        remove_directory_contents(compiled_directory)
    compiled_directory.mkdir(exist_ok=True)

    errors = []

    for corpus_category in corpus.categories():
        category = corpus_category.category
        corpus_id = f"{corpus.lang}_{category}_{date_s}"
        print(f"  processing corpus {corpus_id}...")
        # corpus_sentence_count = 0
        root_element = ET.Element("corpus")
        root_element.attrib["id"] = corpus_id
        n_tot_sentences, n_tot_tokens = 0, 0
        text_num = 1
        file_list = list(corpus_category.iter_files(suffix="xml"))
        nfiles = len(file_list)

        for i, file in enumerate(file_list, start=1):
            print(f"    processing file [{i}/{nfiles}] {file}...", end=" ", flush=True)
            try:
                text_el, n_sentences, n_tokens = process_input_xml(
                    file, category, text_num
                )
            except ET.ParseError:
                errors.append(f"file {file} could not be parsed (invalid xml?)")
                print("failed (could not parse xml)")
            else:
                if text_el:
                    text_num += 1
                    root_element.append(text_el)
                    n_tot_tokens += n_tokens
                    n_tot_sentences += n_sentences
                    print("done")
                else:
                    errors.append(f"file {file} had no text")
                    print("failed (file contains no text)")

        ET.indent(root_element, "")
        with open(Path(compiled_directory / f"{corpus_id}.vrt"), "w") as f:
            f.write(ET.tostring(root_element, encoding="unicode"))

    for error in errors:
        print(error)


@timed
def cwb_huffcode(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    compressing token files (cwb_huffcode)...", end="", flush=True)
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


@timed
def cwb_compress_rdx(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    compressing indexes...", end="", flush=True)
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


@timed
def rm_unneeded_data_files(data_dir, corpus_name):
    print(
        f"    deleting non-compressed files from data dir of corpus {corpus_name}...",
        end="",
        flush=True,
    )
    d = data_dir / corpus_name
    for file in chain(d.glob("*.rev"), d.glob("*.rdx"), d.glob("*.corpus")):
        file.unlink()


def ensure_data_and_registry_dirs(args):
    target = args.target
    data = args.data_dir
    registry = args.registry_dir

    if target:
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
        if not target.is_dir():
            exit(f"target directory is not a directory ({target})")
        data = target / "data"
        registry = target / "registry"
        data = data.resolve()
        registry = registry.resolve()
        data.mkdir(exist_ok=True)
        registry.mkdir(exist_ok=True)
        return data, registry
    else:
        if not data.is_dir():
            print(f"given data directory doesn't exist ({data})")
            exit()
        if not registry.is_dir():
            print(f"given registry directory doesn't exist ({registry})")
            exit()
        data = data.resolve()
        registry = registry.resolve()
        return data, registry


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

    if not dates:
        first_date = None
        last_date = None
    else:
        dates.sort()
        first_date = dates[0]
        last_date = dates[-1]

    return n_sentences, first_date, last_date


def update_registry(registry_dir, corpus_name, descriptive_name, lang):
    print(f"    Updating registry {corpus_name}...", end="", flush=True)
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
    print("done")


def create_korp_settings(korp_corpus_config_dir, vrt_directory, corpus_name):
    """Create the Korp corpus config-.yaml file that Korp needs, i.e.
    KORP_CORPUS_CONFIG_DIR/corpora/LANG_CATEGORY_DATE.yaml

    Fill it with default values
    """
    raise NotImplementedError
    # create the Korp settings files,
    # vrt_fao_DATE
    default_title = " ".join(vrt_directory.split("_")[:-1])
    data = dedent(
        f"""
    description: blank
    id: {corpus_name}
    mode:
    - name: default
    title: {default_title}
    context:
      - label:
          eng: 1 sentence
          nob: 1 mening
        value: 1 sentence
    within:
      - label:
          eng: sentence
          swe: mening
        value: sentence
    """
    ).strip()
    file = (korp_corpus_config_dir / corpus_name).with_suffix(".yaml")
    with open(file, "w") as f:
        f.write(data)


@timed
def cwb_encode(
    vrt_file,
    corpus_name,
    cwb_binaries_directory,
    data_dir,
    registry_dir,
):
    print("    Converting to CWB binary format (cwb-encode)...", end="", flush=True)
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


@timed
def cwb_makeall(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    create lexicon and index (cwb-makeall)...", end="", flush=True)
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
    vrt_directory: Path,
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

    for vrt_file in vrt_directory.iterdir():
        print(f"{vrt_file.name}...")
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

        cwb_encode(
            vrt_file, corpus_name, cwb_binaries_directory, data_dir, registry_dir
        )
        cwb_makeall(cwb_binaries_directory, registry_dir, upper_corpus_name)
        cwb_huffcode(cwb_binaries_directory, registry_dir, upper_corpus_name)
        cwb_compress_rdx(cwb_binaries_directory, registry_dir, upper_corpus_name)
        rm_unneeded_data_files(data_dir, corpus_name)
        DESCRIPTIVE_NAME = "DESCRIPTIVE " + corpus_name
        update_registry(registry_dir, corpus_name, DESCRIPTIVE_NAME, lang)
        # create_korp_settings()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=".", required=False)

    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help=(
            "Date of compilation, in iso format (YYYYMMDD). This should "
            "be the date the corpus was analysed. Defaults to todays date if "
            "not given"
        ),
    )
    parser.add_argument(
        "--cwb-binaries-dir",
        help="directory where the cwb binaries (such as cwb-encode, etc) "
        "are located. Only necessary if the `cwb-xxx` commands are not "
        "available on the system path",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="target directory, where data/ and registry/ subfolders exist. "
        "If the data/ and registry/ directires are in different folders, "
        "use the --data-dir and --registry-dir arguments to specify them "
        "individually",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="path to the CWB data/ directory. If data/ and registry/ is "
        "in the same directory, it's simpler to use --target",
    )
    parser.add_argument(
        "--registry-dir",
        type=Path,
        help="path to the CWB registry/ directory. If data/ and registry/ is "
        "in the same directory, it's simpler to use --target",
    )

    args = parser.parse_args()

    try:
        args.corpus = Corpus.from_path(args.corpus)
    except Exception as e:
        parser.error(f"argument `corpus`: {e}\n")

    ensure_korp_mono(args.corpus, parser)

    _msg = "use either: --target, OR BOTH --data-dir and --registry-dir"
    if args.target:
        if args.data_dir or args.registry_dir:
            parser.error(_msg)
    else:
        if not (args.data_dir and args.registry_dir):
            parser.error(_msg)

    if args.cwb_binaries_dir:
        args.cwb_binaries_dir = Path(args.cwb_binaries_dir)
    else:
        cmd = ["sh", "-c", "command -v cwb-encode"]
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            parser.print_usage()
            print(
                "critical: cannot find the cwb binaries on the system, "
                "specify the directory where the binaries are located using "
                "--cwb-binaries-dir"
            )
            parser.exit(1)

        args.cwb_binaries_dir = Path(proc.stdout.strip()).parent

    if (
        not (args.cwb_binaries_dir / "cwb-encode").is_file()
        or not (args.cwb_binaries_dir / "cwb-makeall").is_file()
        or not (args.cwb_binaries_dir / "cwb-huffcode").is_file()
        or not (args.cwb_binaries_dir / "cwb-compress-rdx").is_file()
    ):
        parser.print_usage()
        print(
            "critical: cannot find the cwb binaries in the given folder"
            f" ({args.cwb_binaries_dir.resolve()})"
        )
        parser.exit(1)

    return args


def ensure_korp_mono(corpus, parser):
    if corpus.module is not None:
        if corpus.module != "korp_mono":
            parser.error(
                "child folder of the corpus folder must be 'korp_mono', "
                f"not '{corpus.module}'.\n"
                f"corpus path given: {corpus.path}"
            )
    else:
        if not corpus.has_module("korp_mono"):
            parser.error(
                "This corpus has no subfolder 'korp_mono'\n"
                "Hint: This script uses the contents of the 'korp_mono' "
                "folder as its input. Use the 'korp_mono' tool to "
                "generate it. See the documentation for more "
                "information."
            )
        corpus.module = "korp_mono"


def main():
    args = parse_args()
    args.data_dir, args.registry_dir = ensure_data_and_registry_dirs(args)

    # the data/ directory must be empty, otherwise CWB gets very confused
    print("Making sure the data/ directory is empty...", end="", flush=True)
    remove_directory_contents(args.data_dir)
    print("done")

    concat_corpus(args.corpus, args.date)

    for entry in Path(".").glob("vrt_*"):
        if not entry.is_dir():
            continue

        encode_corpus(
            vrt_directory=entry,
            date=args.date,
            lang=entry.name[4:7],
            data_dir=args.data_dir,
            registry_dir=args.registry_dir,
            cwb_binaries_directory=args.cwb_binaries_dir,
        )


if __name__ == "__main__":
    raise SystemExit(main())
