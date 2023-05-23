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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Code to detect and fix semi official and unofficial encodings.

(Northern) sami character eight bit encodings have been semi or
non official standards and have been converted to the various systems'
internal encodings. This module has functions that revert the damage
done.
"""


# macsami, winsami2, are needed, even if pylint
# flags them as unused
# pylint: disable=unused-import
from corpustools import macsami, mari, util, winsami2

CYRILLIC_LANGUAGES = ["mhr", "mrj"]


def fix_macsami_cp1252(instring):
    """Fix instring.

    Args:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            cp1252.

    Returns:
        (str): str with fixed encoding.
    """
    bytestring = instring.encode("1252", errors="xmlcharrefreplace")
    encoded_unicode = bytestring.decode("macsami").replace("&#129;", "Å")
    return encoded_unicode


def fix_macsami_latin1(instring):
    """Fix instring.

    Args:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            latin1.

    Returns:
        (str): a string with fixed encoding.
    """
    return instring.encode("latin1", errors="xmlcharrefreplace").decode("macsami")


def fix_macsami_mac(instring):
    """Fix instring.

    Args:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            macroman.

    Returns:
        (str): a string with fixed encoding.
    """
    bytestring = instring.encode("macroman", "xmlcharrefreplace")
    encoded_string = bytestring.decode("macsami").replace("&#8486;", "ž")

    return encoded_string


def fix_winsami2_cp1252(instring):
    """Fix instring.

    Args:
        instring (str): A bytestring that originally was encoded as
            winsami2 but has been decoded to unicode as if it was
            cp1252.

    Returns:
        (str): a string with fixed encoding.
    """
    return instring.encode("cp1252", errors="xmlcharrefreplace").decode("ws2")


def fix_meadowmari_cp1252(instring):
    """Fix instring.

    Args:
        instring (str): A bytestring that originally was encoded as
            meadowmari but has been decoded to unicode as if it was
            cp1252.

    Returns:
        (str): a string with fixed encoding.
    """
    mari_replacements = [
        ("&#1118;", "ӱ"),  # xml char ref CYRILLIC SMALL LETTER SHORT U
        ("&#1038;", "Ӱ"),  # xml char ref CYRILLIC CAPITAL LETTER SHORT U
        ("Ў", "Ӱ"),
        ("&#1108;", "ӧ"),  # xml char ref CYRILLIC SMALL LETTER UKRAINIAN IE
        ("&#1028;", "Ӧ"),  # xml char ref CYRILLIC CAPITAL LETTER UKRAINIAN IE
    ]

    return util.replace_all(
        mari_replacements,
        instring.encode("cp1252", errors="xmlcharrefreplace").decode("meadowmari"),
    )


CTYPES = {
    "mix-mac-sami-and-some-unknown-encoding": {
        "": "á",  # 0x87, á in macsami, same as in macsami->latin1
        "_": "š",  # 0x5F, LOW LINE in macsami, winsami2, ir197, ir209
        "ã": "č",  # 0xE3, a with tilde in macsami, winsami2, ir197, ir209
        "÷": "đ",  # 0xF7, division sign in macsami
        "À": "ž",
        "ç": "Á",  # macsami -> cp1252
        "â": "Č",  # 0xE2
        "¼": "ŧ",  # winsami2 -> cp1252
        "¿": "ø",  # macsami -> latin1, macsami -> cp1252
    },
    # latin4 as cp1252/latin1
    # á, æ, å, ø, ö, ä appear as themselves
    "latin4_to_cp1252": {
        "á": "á",
        "¹": "š",
        "è": "č",
        "ð": "đ",
        "¾": "ž",
        "¿": "ŋ",
        "Á": "Á",
        "È": "Č",
        "¼": "ŧ",
        "©": "Š",
        "Ð": "Đ",  # U+00D0 to U+0110
        "½": "Ŋ",
        "®": "Ž",
        "¬": "Ŧ",
    },
    # winsam as cp1252
    "winsam_to_cp1252": {
        "á": "á",
        "ó": "š",
        "ç": "č",
        "ð": "đ",
        "þ": "ž",
        "ñ": "ŋ",
        "Á": "Á",
        "Ç": "Č",
        "ý": "ŧ",
        "Ó": "Š",
        "Ð": "Đ",  # U+00D0 to U+0110
        "Ñ": "Ŋ",
        "Þ": "Ž",
        "Ý": "Ŧ",
    },
    # iso-ir-197 converted as iconv -f latin1/cp1252 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    "iso-ir-197_to_cp1252": {
        "á": "á",
        "³": "š",
        "¢": "č",
        "¤": "đ",
        "º": "ž",
        "±": "ŋ",
        "Á": "Á",
        "¡": "Č",
        "¸": "ŧ",
        "²": "Š",
        "£": "Đ",
        "¯": "Ŋ",
        "¹": "Ž",
        "µ": "Ŧ",
    },
    "mix-of-latin4-and-iso-ir-197_to_cp1252": {
        "á": "á",
        "ó": "š",
        "ç": "č",
        "¤": "đ",
        "º": "ž",
        "Á": "Á",
        "Ç": "Č",
        "Ó": "Š",
        "£": "Đ",
    },
    "double-utf8": {
        "Ã¡": "á",
        "Ã?": "Á",
        "Å¡": "š",
        "Â¹": "š",
        "Å ": "Š",
        "Å§": "ŧ",
        "Å‹": "ŋ",
        "ÅŠ": "Ŋ",
        "Ä‘": "đ",
        "Ã°": "đ",
        "Å¾": "ž",
        "Âº": "ž",
        "Å½": "Ž",
        "Ä?": "č",
        "Ã¨": "č",
        "ÄŒ": "Č",
        "Ã¦": "æ",
        "Ã¸": "ø",
        "Ã˜": "Ø",
        "Ã¥": "å",
        "Ã…": "Å",
        "Ã¤": "ä",
        "Ã„": "Ä",
        "Ã¶": "ö",
        "â€œ": "“",
        "â€?": "”",
        "â€“": "–",
        "Â«": "«",
        "â‰¤": "«",
        "Â»": "»",
        "â‰¥": "»",
        "Â´": "´",
        "â€¢": "•",
    },
    "finnish-lawtexts-in-pdf": {
        "þ": "č",
        "á": "á",
    },
    "cyrillic_in_pdf": {
        #  '_': 'Ҥ',
        #  '_': 'ҥ',
        "¡": "ӱ",
        "¢": "ӱ",
        "ª": "Ӧ",
        "¯": "Ӹ",
        "²": "Ӓ",
        "³": "ӓ",
        "·": "Ё",
        "¸": "ё",
        "¹": "№",
        "º": "ӧ",
        "¿": "ӹ",
        "À": "A",
        "Á": "б",
        "Â": "В",
        "Ã": "Г",
        "Ä": "Д",
        "Å": "Е",
        "Æ": "Ж",
        "Ç": "З",
        "È": "И",
        "É": "Й",
        "Ê": "К",
        "Ë": "Л",
        "Ì": "М",
        "Í": "Н",
        "Î": "О",
        "Ï": "П",
        "Ð": "Р",
        "Ñ": "С",
        "Ò": "Т",
        "Ó": "У",
        "Ô": "Ф",
        "Õ": "Х",
        "Ö": "Ц",
        "×": "Ч",
        "Ø": "Ш",
        "Ù": "Щ",
        "Ú": "Ъ",
        "Û": "Ы",
        "Ü": "Ь",
        "Ý": "Э",
        "Þ": "Ю",
        "ß": "Я",
        "à": "а",
        "á": "б",
        "â": "в",
        "ã": "г",
        "ä": "д",
        "å": "е",
        "æ": "ж",
        "ç": "з",
        "è": "и",
        "é": "й",
        "ê": "к",
        "ë": "л",
        "ì": "м",
        "í": "н",
        "î": "о",
        "ï": "п",
        "ð": "р",
        "ñ": "с",
        "ò": "т",
        "ó": "у",
        "ô": "ф",
        "õ": "х",
        "ö": "ц",
        "÷": "ч",
        "ø": "ш",
        "ù": "щ",
        "ú": "ъ",
        "û": "ы",
        "ü": "ь",
        "ý": "э",
        "þ": "ю",
        "ÿ": "я",
    },
}


def guess_file_encoding(filename, mainlang):
    """Guess the encoding of a file.

    Args:
        filename (str): the file to open

    Returns:
        (str): A codec name, as given in the keys of CTYPES, or None
            if no codec could be determined
    """
    with open(filename) as infile:
        content = infile.read()
        winner = guess_body_encoding(content, mainlang)

        return winner


def guess_body_encoding(content, mainlang):
    """Guess the encoding of the string content.

    First get the frequencies of the "sami letters"
    Then get the frequencies of the letters in the encodings in CTYPES

    If "sami letters" that the encoding tries to fix exist in "content",
    disregard the encoding

    Args:
        content (str): the content
        mainlang (str): Three-letter language code

    Returns:
        (str): A codec name, as given in the keys of CTYPES, or None
            if no codec could be determined
    """
    winner = None
    if "ì" in content and "ò" in content and mainlang in CYRILLIC_LANGUAGES:
        winner = "cyrillic_in_pdf"
    elif "à" in content and "û" in content and mainlang in CYRILLIC_LANGUAGES:
        winner = "cp1251_cp1252"
    elif ("‡" in content and "ã" not in content) or (
        "Œ" in content and "ÄŒ" not in content and "å" not in content
    ):
        winner = "mac-sami_to_cp1252"
    elif (
        ("" in content and "ã" not in content)
        or ("" in content)
        or ("¯" in content and "á" not in content)
    ):
        winner = "mac-sami_to_latin1"
    elif "" in content and "ã":
        winner = "mix-mac-sami-and-some-unknown-encoding"
    elif "³" in content and "¢" in content and "¤" in content:
        winner = "iso-ir-197_to_cp1252"
    elif "á" in content and ("ª" in content or "∫" in content):
        winner = "mac-sami_to_mac"
    elif "ó" in content and "ç" in content and "ð" in content:
        winner = "winsam_to_cp1252"
    elif "á" in content and "è" in content and "ð" in content:
        winner = "latin4_to_cp1252"
    elif "ó" in content and "ç" in content and "¤" in content:
        winner = "mix-of-latin4-and-iso-ir-197_to_cp1252"
    elif "„" in content and ("˜" in content or "¹" in content):
        winner = "winsami2_to_cp1252"
    elif "þ" in content and "š" in content and "á" in content:
        winner = "finnish-lawtexts-in-pdf"
    elif "Ã¡" in content:
        winner = "double-utf8"

    return winner


def default_decoder(position, text):
    """The default decoder.

    Args:
        position (str): 
        text (str): The string that should be decoded.

    Returns:
        (str): 
    """
    if position is not None:
        for key, value in CTYPES[position].items():
            text = text.replace(key, value)

    return text


def decode_para(position, text):
    """Decode the text given to this function.

    Replace letters in text with the ones from the dict at
    position position in CTYPES

    Args:
        position (str): an encoding name
        text (str): the text to decode

    Returns:
        (str): The decoded text
    """
    which_decoder = {
        "mac-sami_to_cp1252": fix_macsami_cp1252,
        "mac-sami_to_latin1": fix_macsami_latin1,
        "mac-sami_to_mac": fix_macsami_mac,
        "winsami2_to_cp1252": fix_winsami2_cp1252,
        "cp1251_cp1252": fix_meadowmari_cp1252,
    }

    try:
        return which_decoder[position](text)
    except KeyError:
        return default_decoder(position, text)
