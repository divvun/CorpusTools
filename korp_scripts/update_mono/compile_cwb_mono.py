"""
Take the "korp-ready" files in a "corpus-xxx/korp_mono" directory of a corpus,
and create the binary CWB files (the files that are in data/ and registry/).
"""
import argparse
import builtins
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from functools import wraps
from itertools import chain
from pathlib import Path
from textwrap import dedent
from time import perf_counter_ns
from typing import Callable


LANGS = set(
    "fao fit fkv koi kpv mdf mhr mrj myv olo "
    "sma sme smj smn sms udm vep vro".split()
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
    path: Path
    lang: str

    # which category to scan through. part of the path, if given,
    # if only root directory given, scan through all categories in the folder
    category: str | None = None

    # if given, specify the subpath inside of a category to start recursing
    # from
    subpath: str | None = None

    def subcorpuses(self):
        """Yield all directories"""
        if self.category:
            # only a specific category selected, so only yield one result
            yield Corpus(path=self.path, lang=self.lang,
                         category=self.category, subpath=self.subpath)
        else:
            # iterate over all categories in CORPUS_ROOT/corpus-xxx/korp/<category>
            for i, part in enumerate(self.path.parts):
                if part.startswith("corpus-"):
                    root = Path(*self.path.parts[:i + 1])

            for p in (root / "korp_mono").iterdir():
                yield Corpus(path=p, lang=self.lang, category=p.parts[-1])


class CorpusDirectory(argparse.Action):
    """The type of the *directory* argument. Checks that folder exists,
    and determines how the *class:Corpus* should be built."""

    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        help = (
            "the path of the corpus directory to compile CWB files for, "
            "or a subdirectory thereof"
        )
        super().__init__(option_strings, dest, type=Path, help=help)

    def die(self, parser, msg):
        parser.error(f"{sys.argv[0]}: error: argument `{self.dest}`: {msg}\n")

    def __call__(self, parser, namespace, values, option_string=None):
        directory = values
        try:
            directory = directory.resolve(strict=True)
        except FileNotFoundError:
            self.die(parser, f"'{directory}' is not a directory")
        except RuntimeError:
            self.die(parser, "inifinite loop in links detected")

        parts = directory.parts

        for idx, folder in enumerate(parts):
            if folder.startswith("corpus-"):
                lang = folder[7:]
                if lang not in LANGS:
                    msg = (
                        f"directory '{folder}' detected as corpus directory, "
                        f"but '{lang}' is not a valid language code\n"
                        f"directory path given: {directory}"
                    )
                    self.die(parser, msg)
                subfolder_given = len(parts) > idx + 1
                if subfolder_given:
                    subfolder = parts[idx + 1]
                    if subfolder != "korp_mono":
                        msg = (
                            "child folder of the corpus folder must be 'korp_mono', "
                            f"not '{subfolder}'.\n"
                            f"directory path given: {directory}"
                        )
                        self.die(parser, msg)
                else:
                    if not (directory / "korp_mono").is_dir():
                        self.die(
                            parser,
                            "The corpus folder given has no "
                            "subfolder 'korp_mono'\n"
                            "Hint: This script uses the contents of that 'korp_mono' "
                            "folder as its input. Use the 'korp_mono' tool to "
                            "generate it. See the documentation for more "
                            "information."
                        )

                if len(parts) > idx + 2:
                    category = parts[idx + 2]
                else:
                    category = None

                if len(parts) > idx + 3:
                    subpath = parts[idx + 3:]
                else:
                    subpath = None

                corpus = Corpus(path=directory, lang=lang, category=category,
                                subpath=subpath)

                setattr(namespace, self.dest, corpus)
                return

        self.die(parser, "no corpus found in given directory path.\nThe first "
                 "folder that is named in the form 'corpus-xxx' (where xxx is "
                 "a 3-letter language code) is considered the corpus "
                 "directory, but in the directory path that was given, no "
                 "such folder was found.\n"
                 f"directory path given: {directory}")


def _default_success(completed_process: subprocess.CompletedProcess):
    return completed_process.returncode == 0


def run_subcommand(
    cmd: list[str],
    considered_success:
        Callable[[subprocess.CompletedProcess], bool] = _default_success,
    verbose: bool = False,
    check: bool = False,
):
    def noop(*_args, **_kwargs): pass
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
    try:
        xml = ET.parse(file)
    except ET.ParseError:
        return None, None, None

    texts = xml.findall("[sentence]")
    if not texts:
        return None, None, None
    if len(texts) > 1:
        print(f"notice: {file} has >1 texts! (should have exactly 1 (?))")
        # TODO what should happen in this case? Just process all <text> nodes?

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
def concat_corpus(corpus, date):
    """Replaces what compile_corpus.xsl does. Basically concat all the files
    in a corpus, and store it in one file."""
    print("Concatenating corpora...")
    date_s = str(date).replace('-', '')
    corpus_directory = Path(f"vrt_{corpus.lang}_{date_s}")
    if corpus_directory.exists():
        remove_directory_contents(corpus_directory)
    corpus_directory.mkdir(exist_ok=True)

    no_texts = []

    for corpusfile in corpus.subcorpuses():
        category = corpusfile.category
        corpus_id = f"{corpus.lang}_{category}_{date_s}"
        print(f"  processing corpus {corpus_id}...")
        # corpus_sentence_count = 0
        root_element = ET.Element("corpus")
        root_element.attrib["id"] = corpus_id
        n_tot_sentences, n_tot_tokens = 0, 0
        text_num = 1
        file_list = list(corpusfile.path.glob("**/*.xml"))
        nfiles = len(file_list)

        for i, file in enumerate(file_list, start=1):
            print(f"    reading file [{i}/{nfiles}] {file}")
            text_el, n_sentences, n_tokens = process_input_xml(file, category, text_num)
            if text_el:
                text_num += 1
                root_element.append(text_el)
                n_tot_tokens += n_tokens
                n_tot_sentences += n_sentences
            else:
                no_texts.append(file)

        ET.indent(root_element, "")
        with open(Path(corpus_directory / f"{corpus_id}.vrt"), "w") as f:
            f.write(ET.tostring(root_element, encoding="unicode"))

    for file in no_texts:
        print(f"  file {file} has no texts!")


@timed
def cwb_huffcode(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    compressing token files (cwb_huffcode)...", end="", flush=True)
    cmd = [
        f"{cwb_binaries_directory}/cwb-huffcode",
        "-r", f"{registry_dir}",
        "-A", upper_corpus_name,
    ]
    ok = run_subcommand(cmd)
    if not ok:
        raise Exception("error: cwb_huffcode() returned non-0")


@timed
def cwb_compress_rdx(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    compressing indexes...", end="", flush=True)
    cmd = [
        f"{cwb_binaries_directory}/cwb-compress-rdx",
        "-r", f"{registry_dir}",
        "-A", upper_corpus_name,
    ]
    ok = run_subcommand(cmd)
    if not ok:
        raise Exception("error: cwb_compress_rx() returned non-0")


def rm_unneeded_data_files(data_dir, corpus_name):
    print(f"    deleting non-compressed files from data dir of corpus {corpus_name}...", end="", flush=True)
    d = data_dir / corpus_name
    for file in chain(d.glob("*.rev"), d.glob("*.rdx"), d.glob("*.corpus")):
        file.unlink()
    print("done")


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
    data = dedent(f"""
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
    """).strip()
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
        "-p", "-",

        # data directory
        "-d", f"{data_dir}/{corpus_name}",

        # registry directory
        "-R", f"{registry_dir}/{corpus_name}",

        # character set
        "-c", "utf8",

        # which .vrt file to encode
        "-f", f"{vrt_file}",

        # positional attributes
        "-P", "word",
        "-P", "lemma",
        "-P", "pos",
        "-P", "msd",
        "-P", "ref",
        "-P", "deprel",
        "-P", "dephead",

        # structural attributes
        "-S", "sentence:0+id+token_count",
        "-S", "text:0+id+title+lang+orig_lang+gt_domain+first_name+last_name"
              "+nationality+date+datefrom+dateto+timefrom+timeto"
              "+sentence_count+token_count",
        "-S", "corpus:0+id",
    ]
    if not run_subcommand(cmd):
        raise RuntimeError("cwb_encode() failed")


def cwb_makeall(cwb_binaries_directory, registry_dir, upper_corpus_name):
    print("    create lexicon and index (cwb-makeall)...", end="", flush=True)
    cmd = [
        f"{cwb_binaries_directory}/cwb-makeall",
        "-D",
        "-r", f"{registry_dir}",
        f"{upper_corpus_name}",
    ]
    try:
        run_subcommand(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("failed")
        print(e.stdout)
        print(e.stderr)
        raise e
    else:
        print("done")
        return True


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
        corpus_name = vrt_file.name[:vrt_file.name.index(".")]
        upper_corpus_name = corpus_name.upper()
        # in metadata: id name title description lang updated
        # TODO this is supposed to be the "NAME" field in the file registry/<corpus>/<id>
        long_name = "" # in the metadata file, indexed by id=corpus_name

        #sh loc_encode_gt_corpus_20181106.sh "$input_data" "$date" "$ln" "$lang_code" "$corpus_name" "$fd" "$ld"

        corpus_data_dir = data_dir / corpus_name
        corpus_data_dir.mkdir(parents=True, exist_ok=True)
        with open(corpus_data_dir / ".info", "w") as f:
            f.write(
                f"Sentences: {n_sentences}\nUpdated: {date}\n"
                f"FirstDate: {first_date}\nLastDate: {last_date}\n"
            )

        cwb_encode(vrt_file, corpus_name, cwb_binaries_directory, data_dir, registry_dir)
        cwb_makeall(cwb_binaries_directory, registry_dir, upper_corpus_name)
        cwb_huffcode(cwb_binaries_directory, registry_dir, upper_corpus_name)
        cwb_compress_rdx(cwb_binaries_directory, registry_dir, upper_corpus_name)
        rm_unneeded_data_files(data_dir, corpus_name)
        DESCRIPTIVE_NAME = "DESCRIPTIVE " + corpus_name
        update_registry(registry_dir, corpus_name, DESCRIPTIVE_NAME, lang)
        # create_korp_settings()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", action=CorpusDirectory)

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
             "available on the system path"
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

    if args.target:
        if (args.data_dir or args.registry_dir):
            parser.print_usage()
            parser.exit(1, "--target cannot be given at the same time as "
                           "--data-dir and --registry-dir\n")
    else:
        if not (args.data_dir and args.registry_dir):
            parser.print_usage()
            parser.exit(1, "either --target OR BOTH --data-dir and "
                           "--registry-dir must be given\n")

    if args.cwb_binaries_dir:
        args.cwb_binaries_dir = Path(args.cwb_binaries_dir)
    else:
        cmd = ["sh", "-c", "command -v cwb-encode"]
        proc = subprocess.run(cmd, text=True, capture_output=True)
        if proc.returncode != 0:
            print("critical: cannot find the cwb binaries on the system, "
                  "specify the directory where the binaries are located using "
                  "--cwb-binaries-dir")
            parser.print_usage()
            parser.exit(1)

        args.cwb_binaries_dir = Path(proc.stdout.strip()).parent

    if (
        not (args.cwb_binaries_dir / "cwb-encode").is_file() or
        not (args.cwb_binaries_dir / "cwb-makeall").is_file() or
        not (args.cwb_binaries_dir / "cwb-huffcode").is_file() or
        not (args.cwb_binaries_dir / "cwb-compress-rdx").is_file()
    ):
        print("critical: cannot find the cwb binaries in the given folder"
              f" ({args.cwb_binaries_dir.resolve()})")
        parser.print_usage()
        parser.exit(1)

    return args


def main(args):
    args.data_dir, args.registry_dir = ensure_data_and_registry_dirs(args)

    # the data/ directory must be empty, otherwise CWB gets very confused
    print("Making sure the data/ directory is empty...", end="", flush=True)
    remove_directory_contents(args.data_dir)
    print("done")

    concat_corpus(args.directory, args.date)

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
    args = parse_args()
    raise SystemExit(main(args))
