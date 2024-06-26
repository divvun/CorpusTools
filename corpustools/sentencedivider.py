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
#   Copyright © 2011-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://divvun.no & http://giellatekno.uit.no
#
"""Classes and functions to sentence align two files."""


from corpustools import ccat, modes


def to_plain_text(file_path):
    """Turn an xml formatted file into clean text.

    Args:
        file_path (CorpusPath): The path to the file

    Raises:
        UserWarning: if there is no text, raise a UserWarning

    Returns:
        (str): the content of ccat output
    """
    xml_printer = ccat.XMLPrinter(lang=file_path.lang, all_paragraphs=True)
    xml_printer.parse_file(file_path.converted)
    text = xml_printer.process_file().getvalue()
    if text:
        return text
    else:
        raise UserWarning(f"Empty file {file_path.converted}")


class SentenceDivider:
    """A class to divide plain text output into sentences.

    Uses hfst-tokenise as the motor for this purpose.

    Attributes:
        stops (list[str]): tokens that imply where a sentence ends.
        lang (str): three character language code
        relative_path (str): relative path to where files needed by
            modes.xml are found.
        tokeniser (modes.Pipeline): tokeniser pipeline
    """

    stops = [";", "!", "?", ".", "..", "...", "¶", "…"]

    def __init__(self, lang, giella_prefix=None):
        """Set the files needed by the tokeniser.

        Args:
            lang (str): language the analyser can tokenise
        """
        self.tokeniser = modes.Pipeline("tokenise", lang, giella_prefix)

    def make_sentences(self, tokenised_output):
        """Turn ccat output into cleaned up sentences.

        Args:
            tokenised_output (str): plain text output of ccat.

        Yields:
            (str): a cleaned up sentence
        """

        token_buffer = []
        for token in tokenised_output.split("\n"):
            if token != "¶":
                token_buffer.append(token)
            if token.strip() in self.stops:
                yield "".join(token_buffer).strip()
                token_buffer[:] = []
        if token_buffer:
            yield "".join(token_buffer).strip()

    def make_valid_sentences(self, ccat_output):
        """Turn ccat output into full sentences.

        Args:
            ccat_output (str): the plain text output of ccat

        Returns:
            (list[str]): The ccat output has been turned into a list
                of full sentences.
        """
        return [
            sentence
            for sentence in self.make_sentences(
                self.tokeniser.run(ccat_output.encode("utf8"))
            )
            if sentence
        ]
