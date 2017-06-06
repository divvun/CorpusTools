# -*- coding: utf-8 -*-
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
#   Copyright © 2013-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Code to detect and fix semi official and unofficial encodings.

(Northern) sami character eight bit encodings have been semi or
non official standards and have been converted to the various systems'
internal encodings. This module has functions that revert the damage
done.
"""
from __future__ import absolute_import, print_function

import six

# macsami, winsami2, are needed, even if pylint
# flags them as unused
# pylint: disable=unused-import
from corpustools import macsami, util, winsami2, mari


CYRILLIC_LANGUAGES = ['mhr']


def fix_macsami_cp1252(instring):
    """Fix instring.

    Arguments:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            cp1252.

    Returns:
        str with fixed encoding.
    """
    bytestring = instring.encode('1252', errors='xmlcharrefreplace')
    encoded_unicode = bytestring.decode('macsami').replace(u'&#129;', u'Å')
    return encoded_unicode


def fix_macsami_latin1(instring):
    """Fix instring.

    Arguments:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            latin1.

    Returns:
        str with fixed encoding.
    """
    return instring.encode('latin1',
                           errors='xmlcharrefreplace').decode(
                               'macsami')


def fix_macsami_mac(instring):
    """Fix instring.

    Arguments:
        instring (str): A bytestring that originally was encoded as
            macsami but has been decoded to unicode as if it was
            macroman.

    Returns:
        str with fixed encoding.
    """
    bytestring = instring.encode('macroman', 'xmlcharrefreplace')
    encoded_string = bytestring.decode('macsami').replace(u'&#8486;', u'ž')

    return encoded_string


def fix_winsami2_cp1252(instring):
    """Fix instring.

    Arguments:
        instring (str): A bytestring that originally was encoded as
            winsami2 but has been decoded to unicode as if it was
            cp1252.

    Returns:
        str with fixed encoding.
    """
    return instring.encode('cp1252', errors='xmlcharrefreplace').decode('ws2')


def fix_meadowmari_cp1252(instring):
    """Fix instring.

    Arguments:
        instring (str): A bytestring that originally was encoded as
            meadowmari but has been decoded to unicode as if it was
            cp1252.

    Returns:
        str with fixed encoding.
    """
    return instring.encode('cp1252',
                           errors='xmlcharrefreplace').decode(
                               'meadowmari')

CTYPES = {
    u'mix-mac-sami-and-some-unknown-encoding': {
        u'': u'á',  # 0x87, á in macsami, same as in macsami->latin1
        u'_': u'š',  # 0x5F, LOW LINE in macsami, winsami2, ir197, ir209
        u'ã': u'č',  # 0xE3, a with tilde in macsami, winsami2, ir197, ir209
        u'÷': u'đ',  # 0xF7, division sign in macsami
        u'À': u'ž',
        u'ç': u'Á',  # macsami -> cp1252
        u'â': u'Č',  # 0xE2
        u'¼': u'ŧ',  # winsami2 -> cp1252
        u'¿': u'ø',  # macsami -> latin1, macsami -> cp1252
    },

    # latin4 as cp1252/latin1
    # á, æ, å, ø, ö, ä appear as themselves
    u'latin4_to_cp1252': {
        u'á': u'á',
        u'¹': u'š',
        u'è': u'č',
        u'ð': u'đ',
        u'¾': u'ž',
        u'¿': u'ŋ',
        u'Á': u'Á',
        u'È': u'Č',
        u'¼': u'ŧ',
        u'©': u'Š',
        u'Ð': u'Đ',  # U+00D0 to U+0110
        u'½': u'Ŋ',
        u'®': u'Ž',
        u'¬': u'Ŧ',
    },

    # winsam as cp1252
    u'winsam_to_cp1252': {
        u'á': u'á',
        u'ó': u'š',
        u'ç': u'č',
        u'ð': u'đ',
        u'þ': u'ž',
        u'ñ': u'ŋ',
        u'Á': u'Á',
        u'Ç': u'Č',
        u'ý': u'ŧ',
        u'Ó': u'Š',
        u'Ð': u'Đ',  # U+00D0 to U+0110
        u'Ñ': u'Ŋ',
        u'Þ': u'Ž',
        u'Ý': u'Ŧ',
    },

    # iso-ir-197 converted as iconv -f latin1/cp1252 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    u'iso-ir-197_to_cp1252': {
        u'á': u'á',
        u'³': u'š',
        u'¢': u'č',
        u'¤': u'đ',
        u'º': u'ž',
        u'±': u'ŋ',
        u'Á': u'Á',
        u'¡': u'Č',
        u'¸': u'ŧ',
        u'²': u'Š',
        u'£': u'Đ',
        u'¯': u'Ŋ',
        u'¹': u'Ž',
        u'µ': u'Ŧ',
    },

    u'mix-of-latin4-and-iso-ir-197_to_cp1252': {
        u'á': u'á',
        u'ó': u'š',
        u'ç': u'č',
        u'¤': u'đ',
        u'º': u'ž',
        u'Á': u'Á',
        u'Ç': u'Č',
        u'Ó': u'Š',
        u'£': u'Đ',
    },

    u'double-utf8': {
        u'Ã¡': u'á',
        u'Ã?': u'Á',
        u'Å¡': u'š',
        u'Â¹': u'š',
        u'Å ': u'Š',
        u'Å§': u'ŧ',
        u'Å‹': u'ŋ',
        u'ÅŠ': u'Ŋ',
        u'Ä‘': u'đ',
        u'Ã°': u'đ',
        u'Å¾': u'ž',
        u'Âº': u'ž',
        u'Å½': u'Ž',
        u'Ä?': u'č',
        u'Ã¨': u'č',
        u'ÄŒ': u'Č',
        u'Ã¦': u'æ',
        u'Ã¸': u'ø',
        u'Ã˜': u'Ø',
        u'Ã¥': u'å',
        u'Ã…': u'Å',
        u'Ã¤': u'ä',
        u'Ã„': u'Ä',
        u'Ã¶': u'ö',
        u'â€œ': u'“',
        u'â€?': u'”',
        u'â€“': u'–',
        u'Â«': u'«',
        u'â‰¤': u'«',
        u'Â»': u'»',
        u'â‰¥': u'»',
        u'Â´': u'´',
        u'â€¢': u'•',
    },

    u'finnish-lawtexts-in-pdf': {
        u'þ': u'č',
        u'á': u'á',
    },

}


def guess_file_encoding(filename, mainlang):
    """Guess the encoding of a file.

    @param filename name of an utf-8 encoded file
    @return winner is an int, pointing to a position in CTYPES, or -1
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

    @param content a unicode string
    @return winner is a key from CTYPES or None to tell that no known
    encoding is found
    """
    winner = None
    if u'à' in content and u'û' in content and mainlang in CYRILLIC_LANGUAGES:
        winner = u'cp1251_cp1252'
    elif (
            (u'‡' in content and u'ã' not in content) or
            (u'Œ' in content and u'ÄŒ' not in content)):
        winner = u'mac-sami_to_cp1252'
    elif (
            (u'' in content and u'ã' not in content) or
            (u'' in content) or
            (u'¯' in content and u'á' not in content)):
        winner = u'mac-sami_to_latin1'
    elif u'' in content and u'ã':
        winner = u'mix-mac-sami-and-some-unknown-encoding'
    elif u'³' in content and u'¢' in content and u'¤' in content:
        winner = u'iso-ir-197_to_cp1252'
    elif u'á' in content and (u'ª' in content or u'∫' in content):
        winner = u'mac-sami_to_mac'
    elif u'ó' in content and u'ç' in content and u'ð' in content:
        winner = u'winsam_to_cp1252'
    elif u'á' in content and u'è' in content and u'ð' in content:
        winner = u'latin4_to_cp1252'
    elif u'ó' in content and u'ç' in content and u'¤' in content:
        winner = u'mix-of-latin4-and-iso-ir-197_to_cp1252'
    elif u'„' in content and (u'˜' in content or u'¹' in content):
        winner = u'winsami2_to_cp1252'
    elif u'þ' in content and u'š' in content and u'á' in content:
        winner = u'finnish-lawtexts-in-pdf'
    elif u'Ã¡' in content:
        winner = u'double-utf8'

    return winner


def default_decoder(position, text):
    """The default decoder.

    Arguments:
        position
        text (str): The string that should be decoded.

    Returns:
        str
    """
    if position is not None:
        for key, value in six.iteritems(CTYPES[position]):
            text = text.replace(key, value)

    return text


def decode_para(position, text):
    """Decode the text given to this function.

    Replace letters in text with the ones from the dict at
    position position in CTYPES

    @param position which place the encoding has in the CTYPES list
    @param text str
    @return str
    """
    which_decoder = {
        'mac-sami_to_cp1252': fix_macsami_cp1252,
        'mac-sami_to_latin1': fix_macsami_latin1,
        'mac-sami_to_mac': fix_macsami_mac,
        'winsami2_to_cp1252': fix_winsami2_cp1252,
        'cp1251_cp1252': fix_meadowmari_cp1252,
    }

    try:
        return which_decoder[position](text)
    except KeyError:
        return default_decoder(position, text)
