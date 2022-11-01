#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2011-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to sentence align two files."""


import argparse
import os
import re
import subprocess
import tempfile

from lxml import etree

from corpustools import (
    argparse_version,
    corpuspath,
    generate_anchor_list,
    sentencedivider,
    tmx,
    util,
)

HERE = os.path.dirname(__file__)


class Tca2SentenceDivider:
    """Make tca2 compatible input files.

    It spits out an xml document that has divided the text into sentences.
    Each sentence is encased in an s tag, and has an id number
    """

    @staticmethod
    def make_sentence_xml(lang, xmlfile, giella_prefix):
        """Make sentence xml that tca2 can use.

        Args:
            lang (str): three character name of main language of document.
            filename (str): name of the xmlfile

        Returns:
            lxml.etree._Element: an xml element containing all sentences.
        """
        document = etree.Element("document")

        divider = sentencedivider.SentenceDivider(lang, giella_prefix)
        for index, sentence in enumerate(
            divider.make_valid_sentences(sentencedivider.to_plain_text(lang, xmlfile))
        ):
            s_elem = etree.Element("s")
            s_elem.attrib["id"] = str(index)
            s_elem.text = sentence
            document.append(s_elem)

        return document

    def make_sentence_file(self, lang, xmlfile, outfile, giella_prefix):
        """Make input document for tca2.

        Args:
            lang (str): three character name for main language of document.
            xmlfile (str): name of the xmlfile
            outfile (str): name of the input file for tca2
        """
        o_path, _ = os.path.split(outfile)
        o_rel_path = o_path.replace(os.getcwd() + "/", "", 1)
        with util.ignored(OSError):
            os.makedirs(o_rel_path)
        with open(outfile, "wb") as sentence_file:
            tree = etree.ElementTree(
                self.make_sentence_xml(lang, xmlfile, giella_prefix=giella_prefix)
            )
            tree.write(
                sentence_file, pretty_print=True, encoding="utf8", xml_declaration=True
            )


class Parallelize:
    """A class to parallelize two files.

    Input is the xml file that should be parallellized and the language that it
    should be parallellized with.
    The language of the input file is found in the metadata of the input file.
    The other file is found via the metadata in the input file
    """

    def __init__(
        self, origfile1, lang2, anchor_file=None, quiet=False, giella_prefix=None
    ):
        """Initialise the Parallelize class.

        Args:
            origfile1 (str): path to one of the files that should be
                sentence aligned.
            lang2 (str): language of the other file that should be
                sentence aligned.
            anchor_file (str): path to the anchor file. Defaults to None.
                A real file is only needed when using tca2 for sentence
                alignment.
            quiet (bool): If True, be verbose. Otherwise, be quiet.
        """
        self.quiet = quiet
        self.origfiles = []
        self.giella_prefix = giella_prefix
        self.origfiles.append(corpuspath.CorpusPath(os.path.abspath(origfile1)))

        para_file = self.origfiles[0].parallel(lang2)
        if para_file is not None:
            self.origfiles.append(corpuspath.CorpusPath(para_file))
        else:
            raise OSError(f"{origfile1} doesn't have a parallel file in {lang2}")

        # As stated in --help, we assume user-specified anchor file
        # has columns based on input files, where --parallel_file is
        # column two regardless of what file was translated from what,
        # therefore we set this before reshuffling:
        if self.is_translated_from_lang2():
            (self.origfiles[1], self.origfiles[0]) = (
                self.origfiles[0],
                self.origfiles[1],
            )

        self.gal = self.setup_anchors(anchor_file)

    def setup_anchors(self, path):
        """Setup anchor file.

        Args:
            path (str): where the anchor file will be written.
            cols (list of str): list of all the possible langs.

        Returns:
            generate_anchor_list.GenerateAnchorList
        """
        if path is None:
            path1 = os.path.join(
                os.environ["GTHOME"],
                f"gt/common/src/anchor-{self.lang1}-{self.lang2}.txt",
            )
            path2 = os.path.join(
                os.environ["GTHOME"],
                f"gt/common/src/anchor-{self.lang2}-{self.lang1}.txt",
            )
            if os.path.exists(path1):

                return generate_anchor_list.GenerateAnchorList(
                    self.lang1, self.lang2, [self.lang1, self.lang2], path1
                )
            elif os.path.exists(path2):
                return generate_anchor_list.GenerateAnchorList(
                    self.lang1, self.lang2, [self.lang2, self.lang1], path2
                )
            else:
                if not self.quiet:
                    util.note(
                        "No anchor file for the {}/{} combo. "
                        "Making a fake anchor file".format(self.lang1, self.lang2)
                    )

    @property
    def outfile_name(self):
        """Compute the name of the final tmx file."""
        return self.origfiles[0].prestable_tmx(self.lang2)

    @property
    def lang1(self):
        """Get language 1."""
        return self.origfiles[0].pathcomponents.lang

    @property
    def lang2(self):
        """Get language 2."""
        return self.origfiles[1].pathcomponents.lang

    @property
    def origfile1(self):
        """Name of the original file 1."""
        return self.origfiles[0].orig

    @property
    def origfile2(self):
        """Name of the original file 2."""
        return self.origfiles[1].orig

    def is_translated_from_lang2(self):
        """Find out if the given doc is translated from lang2."""
        translated_from = self.origfiles[0].metadata.get_variable("translated_from")

        if translated_from is not None:
            return translated_from == self.lang2
        else:
            return False

    def parallelize_files(self):
        """Parallelize two files."""
        if not self.quiet:
            util.note("Aligning files …")
        return self.align()

    def run_command(self, command):
        """Run a parallelize command and return its output."""
        if not self.quiet:
            util.note("Running {}".format(" ".join(command)))
        subp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            raise UserWarning(
                "Could not parallelize {} and {} into "
                "sentences\n{}\n\n{}\n".format(
                    self.origfile1,
                    self.origfile2,
                    output.decode("utf8"),
                    error.decode("utf8"),
                )
            )

        return output, error

    def align(self):
        """Sentence align two corpus files."""
        raise NotImplementedError("You have to subclass and override align")


class ParallelizeHunalign(Parallelize):
    """Use hunalign to parallelise two converted corpus files."""

    split_anchors_on = re.compile(r" *, *")

    def anchor_to_dict(self, words_pairs):
        """Turn anchorfile tuples into a dictionary."""
        # turn [("foo, bar", "fie")] into [("foo", "fie"), ("bar", "fie")]:
        expanded_pairs = [
            (w1, w2)
            for w1s, w2s in words_pairs
            for w1 in re.split(self.split_anchors_on, w1s)
            for w2 in re.split(self.split_anchors_on, w2s)
            if w1 and w2
        ]
        return expanded_pairs

    def make_dict(self):
        """Turn an anchorlist to a dictionary."""
        if self.gal is not None:
            assert self.gal.lang1 == self.lang1
            assert self.gal.lang2 == self.lang2
            words_pairs = self.gal.read_anchors(quiet=self.quiet)
            expanded_pairs = self.anchor_to_dict(words_pairs)
            cleaned_pairs = [
                (w1.replace("*", ""), w2.replace("*", "")) for w1, w2 in expanded_pairs
            ]
        else:
            cleaned_pairs = [(self.lang1, self.lang2)]
        # Hunalign expects the _reverse_ format for the dictionary!
        # See Dictionary under http://mokk.bme.hu/resources/hunalign/
        return "\n".join([f"{w2} @ {w1}" for w1, w2 in cleaned_pairs]) + "\n"

    def to_sents(self, origfile):
        """Divide the content of origfile to sentences."""
        divider = sentencedivider.SentenceDivider(
            origfile.pathcomponents.lang, giella_prefix=self.giella_prefix
        )
        return "\n".join(
            divider.make_valid_sentences(
                sentencedivider.to_plain_text(
                    origfile.pathcomponents.lang, origfile.converted
                )
            )
        )

    def align(self):
        """Parallelize two files using hunalign."""

        def tmp():
            """Temporary filename.

            Returns:
                str: name of the temporary file
            """
            return tempfile.NamedTemporaryFile("wb")

        with tmp() as dict_f, tmp() as sent0_f, tmp() as sent1_f:
            dict_f.write(self.make_dict().encode("utf8"))
            sent0_f.write(self.to_sents(self.origfiles[0]).encode("utf8"))
            sent1_f.write(self.to_sents(self.origfiles[1]).encode("utf8"))
            dict_f.flush()
            sent0_f.flush()
            sent1_f.flush()

            command = [
                "hunalign",
                "-utf",
                "-realign",
                "-text",
                dict_f.name,
                sent0_f.name,
                sent1_f.name,
            ]
            output, _ = self.run_command(command)

        translation_mem_ex = tmx.HunalignToTmx(self.origfiles, output.decode("utf-8"))
        return translation_mem_ex


class ParallelizeTCA2(Parallelize):
    """Use tca2 to parallelise two converted corpus files."""

    def generate_anchor_file(self, outpath):
        """Generate an anchor file with lang1 and lang2."""
        if self.gal is not None:
            assert self.gal.lang1 == self.lang1
            assert self.gal.lang2 == self.lang2
            self.gal.generate_file(outpath, quiet=self.quiet)
        else:
            with open(outpath, "w") as outfile:
                print(f"{self.lang1} / {self.lang2}", file=outfile)

    def divide_p_into_sentences(self):
        """Tokenize the text in the given file and reassemble it again."""
        for pfile in self.origfiles:
            divider = Tca2SentenceDivider()
            divider.make_sentence_file(
                pfile.pathcomponents.lang,
                pfile.converted,
                pfile.sent_filename,
                self.giella_prefix,
            )

    @property
    def sentfiles(self):
        """Get files containing the sentences."""
        return [name.sent_filename for name in self.origfiles]

    def align(self):
        """Parallelize two files using tca2."""
        if not self.quiet:
            util.note("Adding sentence structure for the aligner …")
        self.divide_p_into_sentences()

        tca2_jar = os.path.join(HERE, "tca2/dist/lib/alignment.jar")
        # util.sanity_check([tca2_jar])

        with tempfile.NamedTemporaryFile("w") as anchor_file:
            self.generate_anchor_file(anchor_file.name)
            anchor_file.flush()
            command = (
                "java -Xms512m -Xmx1024m -jar {} -cli-plain -anchor={} "
                "-in1={} -in2={}".format(
                    tca2_jar,
                    anchor_file.name,
                    self.origfiles[0].sent_filename,
                    self.origfiles[1].sent_filename,
                )
            )

            self.run_command(command.split())

        translation_mem_ex = tmx.Tca2ToTmx(self.origfiles, self.sentfiles)
        return translation_mem_ex


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Sentence align file pairs."
    )

    parser.add_argument(
        "sources",
        nargs="+",
        help="Files or directories to search for " "parallelisable files",
    )
    parser.add_argument(
        "-s",
        "--stdout",
        help="Whether output of the parallelisation "
        "should be written to stdout or a files. "
        "Defaults to "
        "prestable/tmx/{lang1}2{lang2}/{GENRE}/.../{BASENAME}.tmx",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Overwrite output file if it already exists." "This is the default.",
        action="store_false",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Don't mention anything out of the ordinary.",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--aligner",
        choices=["hunalign", "tca2"],
        default="tca2",
        help="Either hunalign or tca2 (the default).",
    )
    parser.add_argument(
        "-d",
        "--dict",
        default=None,
        help="Use a different bilingual seed dictionary. "
        "Must have two columns, with input_file language "
        "first, and --parallel_language second, separated "
        "by `/'. By default, "
        "$GTHOME/gt/common/src/anchor.txt is used, but this "
        "file only supports pairings between "
        "sme/sma/smj/fin/eng/nob. ",
    )
    parser.add_argument(
        "-l2",
        "--lang2",
        help="Indicate which language the given file should" "be parallelised with",
        required=True,
    )

    args = parser.parse_args()
    return args


def parallelise_file(input_file, lang2, dictionary, quiet, aligner, stdout, force):
    """Align sentences of two parallel files."""
    try:
        if aligner == "hunalign":
            parallelizer = ParallelizeHunalign(
                origfile1=input_file, lang2=lang2, anchor_file=dictionary, quiet=quiet
            )
        elif aligner == "tca2":
            parallelizer = ParallelizeTCA2(
                origfile1=input_file, lang2=lang2, anchor_file=dictionary, quiet=quiet
            )
    except OSError as error:
        if not quiet:
            util.note(error)
    except NameError:  # parallel filename is empty
        pass

    else:

        outfile = "/dev/stdout" if stdout else parallelizer.outfile_name

        if (
            outfile == "/dev/stdout"
            or not os.path.exists(outfile)
            or (os.path.exists(outfile) and force)
        ):
            if not quiet:
                util.note(f"Aligning {input_file} and its parallel file")
            translation_mem_ex = parallelizer.parallelize_files()
            translation_mem_ex.clean_toktmx()
            if not quiet:
                util.note(f"Generating the tmx file {outfile}")
            translation_mem_ex.write_tmx_file(outfile)
            translation_mem_ex.tmx2html(parallelizer.outfile_name + ".html")
            if not quiet:
                util.note("Wrote\n\t{}\n\t{}\n".format(outfile, outfile + ".html"))

            return outfile
        else:
            util.note(f"{outfile} already exists, skipping …")


def main():
    """Parallelise files."""
    args = parse_options()

    # TODO: filter out those pairs that already exist in presteable/tmx
    for source in args.sources:
        try:
            if os.path.isfile(source):
                parallelise_file(
                    source,
                    args.lang2,
                    args.dict,
                    args.quiet,
                    args.aligner,
                    args.stdout,
                    args.force,
                )
            elif os.path.isdir(source):
                for root, _, files in os.walk(source):
                    for converted in files:
                        path = os.path.join(root, converted)
                        try:
                            parallelise_file(
                                path,
                                args.lang2,
                                args.dict,
                                args.quiet,
                                args.aligner,
                                args.stdout,
                                args.force,
                            )
                        except UserWarning as error:
                            print(str(error))
        except util.ArgumentError as error:
            raise SystemExit(error)
