# -*- coding: utf-8 -*-
""" Python Character Mapping Codec cp1251 generated from 'MAPPINGS/VENDORS/MICSFT/WINDOWS/CP1251.TXT' with gencodec.py.

"""#"

import codecs

#  Codec APIs


class Codec(codecs.Codec):
    """Implement the interface for stateless encoders/decoders."""

    def encode(self, instring, errors='strict'):
        """Encode the object instring.

        Arguments:
            instring (str): the string that should be encoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace', 'ignore',  'xmlcharrefreplace' or
                'backslashreplace'.

        Returns:
            tuple (output object, length consumed)
        """
        return codecs.charmap_encode(instring, errors, encoding_table)

    def decode(self, instring, errors='strict'):
        """Decode the object instring.

        Arguments:
            instring (str): the string that should be decoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace' or 'ignore'.

        Returns:
            tuple (output object, length consumed)
        """
        return codecs.charmap_decode(instring, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """Implement an IncrementalEncoder."""

    def encode(self, instring, final=False):
        """Encode instring.

        Arguments:
            instring (str): the string that should be encoded with this
                codec.

        Returns:
            output object.
        """
        return codecs.charmap_encode(instring, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    """Implement an IncrementalDecoder."""

    def decode(self, instring, final=False):
        """Decode instring.

        Arguments:
            instring (str): the string that should be decoded with this
                codec.

        Returns:
            output object.
        """
        return codecs.charmap_decode(instring, self.errors, decoding_table)[0]

#  encodings module API


def getregentry():
    """Get the info for this encoding."""
    return codecs.CodecInfo(
        name='meadowmari',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=codecs.StreamReader,
        streamwriter=codecs.StreamWriter,
    )


#  Decoding Table

decoding_table = (
    u'\x00'     # 0x00 -> NULL
    u'\x01'     # 0x01 -> START OF HEADING
    u'\x02'     # 0x02 -> START OF TEXT
    u'\x03'     # 0x03 -> END OF TEXT
    u'\x04'     # 0x04 -> END OF TRANSMISSION
    u'\x05'     # 0x05 -> ENQUIRY
    u'\x06'     # 0x06 -> ACKNOWLEDGE
    u'\x07'     # 0x07 -> BELL
    u'\x08'     # 0x08 -> BACKSPACE
    u'\t'       # 0x09 -> HORIZONTAL TABULATION
    u'\n'       # 0x0A -> LINE FEED
    u'\x0b'     # 0x0B -> VERTICAL TABULATION
    u'\x0c'     # 0x0C -> FORM FEED
    u'\r'       # 0x0D -> CARRIAGE RETURN
    u'\x0e'     # 0x0E -> SHIFT OUT
    u'\x0f'     # 0x0F -> SHIFT IN
    u'\x10'     # 0x10 -> DATA LINK ESCAPE
    u'\x11'     # 0x11 -> DEVICE CONTROL ONE
    u'\x12'     # 0x12 -> DEVICE CONTROL TWO
    u'\x13'     # 0x13 -> DEVICE CONTROL THREE
    u'\x14'     # 0x14 -> DEVICE CONTROL FOUR
    u'\x15'     # 0x15 -> NEGATIVE ACKNOWLEDGE
    u'\x16'     # 0x16 -> SYNCHRONOUS IDLE
    u'\x17'     # 0x17 -> END OF TRANSMISSION BLOCK
    u'\x18'     # 0x18 -> CANCEL
    u'\x19'     # 0x19 -> END OF MEDIUM
    u'\x1a'     # 0x1A -> SUBSTITUTE
    u'\x1b'     # 0x1B -> ESCAPE
    u'\x1c'     # 0x1C -> FILE SEPARATOR
    u'\x1d'     # 0x1D -> GROUP SEPARATOR
    u'\x1e'     # 0x1E -> RECORD SEPARATOR
    u'\x1f'     # 0x1F -> UNIT SEPARATOR
    u' '        # 0x20 -> SPACE
    u'!'        # 0x21 -> EXCLAMATION MARK
    u'"'        # 0x22 -> QUOTATION MARK
    u'#'        # 0x23 -> NUMBER SIGN
    u'$'        # 0x24 -> DOLLAR SIGN
    u'%'        # 0x25 -> PERCENT SIGN
    u'&'        # 0x26 -> AMPERSAND
    u"'"        # 0x27 -> APOSTROPHE
    u'('        # 0x28 -> LEFT PARENTHESIS
    u')'        # 0x29 -> RIGHT PARENTHESIS
    u'*'        # 0x2A -> ASTERISK
    u'+'        # 0x2B -> PLUS SIGN
    u','        # 0x2C -> COMMA
    u'-'        # 0x2D -> HYPHEN-MINUS
    u'.'        # 0x2E -> FULL STOP
    u'/'        # 0x2F -> SOLIDUS
    u'0'        # 0x30 -> DIGIT ZERO
    u'1'        # 0x31 -> DIGIT ONE
    u'2'        # 0x32 -> DIGIT TWO
    u'3'        # 0x33 -> DIGIT THREE
    u'4'        # 0x34 -> DIGIT FOUR
    u'5'        # 0x35 -> DIGIT FIVE
    u'6'        # 0x36 -> DIGIT SIX
    u'7'        # 0x37 -> DIGIT SEVEN
    u'8'        # 0x38 -> DIGIT EIGHT
    u'9'        # 0x39 -> DIGIT NINE
    u':'        # 0x3A -> COLON
    u';'        # 0x3B -> SEMICOLON
    u'<'        # 0x3C -> LESS-THAN SIGN
    u'='        # 0x3D -> EQUALS SIGN
    u'>'        # 0x3E -> GREATER-THAN SIGN
    u'?'        # 0x3F -> QUESTION MARK
    u'@'        # 0x40 -> COMMERCIAL AT
    u'A'        # 0x41 -> LATIN CAPITAL LETTER A
    u'B'        # 0x42 -> LATIN CAPITAL LETTER B
    u'C'        # 0x43 -> LATIN CAPITAL LETTER C
    u'D'        # 0x44 -> LATIN CAPITAL LETTER D
    u'E'        # 0x45 -> LATIN CAPITAL LETTER E
    u'F'        # 0x46 -> LATIN CAPITAL LETTER F
    u'G'        # 0x47 -> LATIN CAPITAL LETTER G
    u'H'        # 0x48 -> LATIN CAPITAL LETTER H
    u'I'        # 0x49 -> LATIN CAPITAL LETTER I
    u'J'        # 0x4A -> LATIN CAPITAL LETTER J
    u'K'        # 0x4B -> LATIN CAPITAL LETTER K
    u'L'        # 0x4C -> LATIN CAPITAL LETTER L
    u'M'        # 0x4D -> LATIN CAPITAL LETTER M
    u'N'        # 0x4E -> LATIN CAPITAL LETTER N
    u'O'        # 0x4F -> LATIN CAPITAL LETTER O
    u'P'        # 0x50 -> LATIN CAPITAL LETTER P
    u'Q'        # 0x51 -> LATIN CAPITAL LETTER Q
    u'R'        # 0x52 -> LATIN CAPITAL LETTER R
    u'S'        # 0x53 -> LATIN CAPITAL LETTER S
    u'T'        # 0x54 -> LATIN CAPITAL LETTER T
    u'U'        # 0x55 -> LATIN CAPITAL LETTER U
    u'V'        # 0x56 -> LATIN CAPITAL LETTER V
    u'W'        # 0x57 -> LATIN CAPITAL LETTER W
    u'X'        # 0x58 -> LATIN CAPITAL LETTER X
    u'Y'        # 0x59 -> LATIN CAPITAL LETTER Y
    u'Z'        # 0x5A -> LATIN CAPITAL LETTER Z
    u'['        # 0x5B -> LEFT SQUARE BRACKET
    u'\\'       # 0x5C -> REVERSE SOLIDUS
    u']'        # 0x5D -> RIGHT SQUARE BRACKET
    u'^'        # 0x5E -> CIRCUMFLEX ACCENT
    u'_'        # 0x5F -> LOW LINE
    u'`'        # 0x60 -> GRAVE ACCENT
    u'a'        # 0x61 -> LATIN SMALL LETTER A
    u'b'        # 0x62 -> LATIN SMALL LETTER B
    u'c'        # 0x63 -> LATIN SMALL LETTER C
    u'd'        # 0x64 -> LATIN SMALL LETTER D
    u'e'        # 0x65 -> LATIN SMALL LETTER E
    u'f'        # 0x66 -> LATIN SMALL LETTER F
    u'g'        # 0x67 -> LATIN SMALL LETTER G
    u'h'        # 0x68 -> LATIN SMALL LETTER H
    u'i'        # 0x69 -> LATIN SMALL LETTER I
    u'j'        # 0x6A -> LATIN SMALL LETTER J
    u'k'        # 0x6B -> LATIN SMALL LETTER K
    u'l'        # 0x6C -> LATIN SMALL LETTER L
    u'm'        # 0x6D -> LATIN SMALL LETTER M
    u'n'        # 0x6E -> LATIN SMALL LETTER N
    u'o'        # 0x6F -> LATIN SMALL LETTER O
    u'p'        # 0x70 -> LATIN SMALL LETTER P
    u'q'        # 0x71 -> LATIN SMALL LETTER Q
    u'r'        # 0x72 -> LATIN SMALL LETTER R
    u's'        # 0x73 -> LATIN SMALL LETTER S
    u't'        # 0x74 -> LATIN SMALL LETTER T
    u'u'        # 0x75 -> LATIN SMALL LETTER U
    u'v'        # 0x76 -> LATIN SMALL LETTER V
    u'w'        # 0x77 -> LATIN SMALL LETTER W
    u'x'        # 0x78 -> LATIN SMALL LETTER X
    u'y'        # 0x79 -> LATIN SMALL LETTER Y
    u'z'        # 0x7A -> LATIN SMALL LETTER Z
    u'{'        # 0x7B -> LEFT CURLY BRACKET
    u'|'        # 0x7C -> VERTICAL LINE
    u'}'        # 0x7D -> RIGHT CURLY BRACKET
    u'~'        # 0x7E -> TILDE
    u'\x7f'     # 0x7F -> DELETE
    u'Ђ'        # 0x80 -> CYRILLIC CAPITAL LETTER DJE
    u'Ѓ'        # 0x81 -> CYRILLIC CAPITAL LETTER GJE
    u'‚'        # 0x82 -> SINGLE LOW-9 QUOTATION MARK
    u'ѓ'        # 0x83 -> CYRILLIC SMALL LETTER GJE
    u'„'        # 0x84 -> DOUBLE LOW-9 QUOTATION MARK
    u'…'        # 0x85 -> HORIZONTAL ELLIPSIS
    u'†'        # 0x86 -> DAGGER
    u'‡'        # 0x87 -> DOUBLE DAGGER
    u'Ҥ'        # 0x88 -> CYRILLIC CAPITAL LIGATURE EN GHE
    u'ҥ'        # 0x89 -> CYRILLIC SMALL LIGATURE EN
    u'Љ'        # 0x8A -> CYRILLIC CAPITAL LETTER LJE
    u'‹'        # 0x8B -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u'Њ'        # 0x8C -> CYRILLIC CAPITAL LETTER NJE
    u'Ќ'        # 0x8D -> CYRILLIC CAPITAL LETTER KJE
    u'Ћ'        # 0x8E -> CYRILLIC CAPITAL LETTER TSHE
    u'Џ'        # 0x8F -> CYRILLIC CAPITAL LETTER DZHE
    u'ђ'        # 0x90 -> CYRILLIC SMALL LETTER DJE
    u'\u2018'   # 0x91 -> LEFT SINGLE QUOTATION MARK
    u'\u2019'   # 0x92 -> RIGHT SINGLE QUOTATION MARK
    u'\u201c'   # 0x93 -> LEFT DOUBLE QUOTATION MARK
    u'\u201d'   # 0x94 -> RIGHT DOUBLE QUOTATION MARK
    u'\u2022'   # 0x95 -> BULLET
    u'\u2013'   # 0x96 -> EN DASH
    u'\u2014'   # 0x97 -> EM DASH
    u'\ufffe'   # 0x98 -> UNDEFINED
    u'Ӱ'        # 0x99 -> CYRILLIC CAPITAL LETTER U WITH DIAERESIS
    u'љ'        # 0x9A -> CYRILLIC SMALL LETTER LJE
    u'›'        # 0x9B -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u'њ'        # 0x9C -> CYRILLIC SMALL LETTER NJE
    u'ќ'        # 0x9D -> CYRILLIC SMALL LETTER KJE
    u'ћ'        # 0x9E -> CYRILLIC SMALL LETTER TSHE
    u'џ'        # 0x9F -> CYRILLIC SMALL LETTER DZHE
    u'\xa0'     # 0xA0 -> NO-BREAK SPACE
    u'Ў'        # 0xA1 -> CYRILLIC CAPITAL LETTER SHORT U
    u'ӱ'        # 0xA2 -> CYRILLIC SMALL LETTER U WITH DIAERESIS
    u'Ј'        # 0xA3 -> CYRILLIC CAPITAL LETTER JE
    u'\xa4'     # 0xA4 -> CURRENCY SIGN
    u'Ґ'        # 0xA5 -> CYRILLIC CAPITAL LETTER GHE WITH UPTURN
    u'\xa6'     # 0xA6 -> BROKEN BAR
    u'\xa7'     # 0xA7 -> SECTION SIGN
    u'Ё'        # 0xA8 -> CYRILLIC CAPITAL LETTER IO
    u'\xa9'     # 0xA9 -> COPYRIGHT SIGN
    u'Ӧ'        # 0xAA -> CYRILLIC CAPITAL LETTER O WITH DIAERESIS
    u'\xab'     # 0xAB -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\xac'     # 0xAC -> NOT SIGN
    u'\xad'     # 0xAD -> SOFT HYPHEN
    u'®'        # 0xAE -> REGISTERED SIGN
    u'Ї'        # 0xAF -> CYRILLIC CAPITAL LETTER YI
    u'\xb0'     # 0xB0 -> DEGREE SIGN
    u'\xb1'     # 0xB1 -> PLUS-MINUS SIGN
    u'І'        # 0xB2 -> CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
    u'і'        # 0xB3 -> CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
    u'ґ'        # 0xB4 -> CYRILLIC SMALL LETTER GHE WITH UPTURN
    u'\xb5'     # 0xB5 -> MICRO SIGN
    u'\xb6'     # 0xB6 -> PILCROW SIGN
    u'\xb7'     # 0xB7 -> MIDDLE DOT
    u'ё'        # 0xB8 -> CYRILLIC SMALL LETTER IO
    u'\u2116'   # 0xB9 -> NUMERO SIGN
    u'ӧ'        # 0xBA -> CYRILLIC SMALL LETTER O WITH DIAERESIS
    u'\xbb'     # 0xBB -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'ј'        # 0xBC -> CYRILLIC SMALL LETTER JE
    u'Ѕ'        # 0xBD -> CYRILLIC CAPITAL LETTER DZE
    u'ѕ'        # 0xBE -> CYRILLIC SMALL LETTER DZE
    u'ї'        # 0xBF -> CYRILLIC SMALL LETTER YI
    u'А'        # 0xC0 -> CYRILLIC CAPITAL LETTER A
    u'Б'        # 0xC1 -> CYRILLIC CAPITAL LETTER BE
    u'В'        # 0xC2 -> CYRILLIC CAPITAL LETTER VE
    u'Г'        # 0xC3 -> CYRILLIC CAPITAL LETTER GHE
    u'Д'        # 0xC4 -> CYRILLIC CAPITAL LETTER DE
    u'Е'        # 0xC5 -> CYRILLIC CAPITAL LETTER IE
    u'Ж'        # 0xC6 -> CYRILLIC CAPITAL LETTER ZHE
    u'З'        # 0xC7 -> CYRILLIC CAPITAL LETTER ZE
    u'И'        # 0xC8 -> CYRILLIC CAPITAL LETTER I
    u'Й'        # 0xC9 -> CYRILLIC CAPITAL LETTER SHORT I
    u'К'        # 0xCA -> CYRILLIC CAPITAL LETTER KA
    u'Л'        # 0xCB -> CYRILLIC CAPITAL LETTER EL
    u'М'        # 0xCC -> CYRILLIC CAPITAL LETTER EM
    u'Н'        # 0xCD -> CYRILLIC CAPITAL LETTER EN
    u'О'        # 0xCE -> CYRILLIC CAPITAL LETTER O
    u'П'        # 0xCF -> CYRILLIC CAPITAL LETTER PE
    u'Р'        # 0xD0 -> CYRILLIC CAPITAL LETTER ER
    u'С'        # 0xD1 -> CYRILLIC CAPITAL LETTER ES
    u'Т'        # 0xD2 -> CYRILLIC CAPITAL LETTER TE
    u'У'        # 0xD3 -> CYRILLIC CAPITAL LETTER U
    u'Ф'        # 0xD4 -> CYRILLIC CAPITAL LETTER EF
    u'Х'        # 0xD5 -> CYRILLIC CAPITAL LETTER HA
    u'Ц'        # 0xD6 -> CYRILLIC CAPITAL LETTER TSE
    u'Ч'        # 0xD7 -> CYRILLIC CAPITAL LETTER CHE
    u'Ш'        # 0xD8 -> CYRILLIC CAPITAL LETTER SHA
    u'Щ'        # 0xD9 -> CYRILLIC CAPITAL LETTER SHCHA
    u'Ъ'        # 0xDA -> CYRILLIC CAPITAL LETTER HARD SIGN
    u'Ы'        # 0xDB -> CYRILLIC CAPITAL LETTER YERU
    u'Ь'        # 0xDC -> CYRILLIC CAPITAL LETTER SOFT SIGN
    u'Э'        # 0xDD -> CYRILLIC CAPITAL LETTER E
    u'Ю'        # 0xDE -> CYRILLIC CAPITAL LETTER YU
    u'Я'        # 0xDF -> CYRILLIC CAPITAL LETTER YA
    u'а'        # 0xE0 -> CYRILLIC SMALL LETTER A
    u'б'        # 0xE1 -> CYRILLIC SMALL LETTER BE
    u'в'        # 0xE2 -> CYRILLIC SMALL LETTER VE
    u'г'        # 0xE3 -> CYRILLIC SMALL LETTER GHE
    u'д'        # 0xE4 -> CYRILLIC SMALL LETTER DE
    u'е'        # 0xE5 -> CYRILLIC SMALL LETTER IE
    u'ж'        # 0xE6 -> CYRILLIC SMALL LETTER ZHE
    u'з'        # 0xE7 -> CYRILLIC SMALL LETTER ZE
    u'и'        # 0xE8 -> CYRILLIC SMALL LETTER I
    u'й'        # 0xE9 -> CYRILLIC SMALL LETTER SHORT I
    u'к'        # 0xEA -> CYRILLIC SMALL LETTER KA
    u'л'        # 0xEB -> CYRILLIC SMALL LETTER EL
    u'м'        # 0xEC -> CYRILLIC SMALL LETTER EM
    u'н'        # 0xED -> CYRILLIC SMALL LETTER EN
    u'о'        # 0xEE -> CYRILLIC SMALL LETTER O
    u'п'        # 0xEF -> CYRILLIC SMALL LETTER PE
    u'р'        # 0xF0 -> CYRILLIC SMALL LETTER ER
    u'с'        # 0xF1 -> CYRILLIC SMALL LETTER ES
    u'т'        # 0xF2 -> CYRILLIC SMALL LETTER TE
    u'у'        # 0xF3 -> CYRILLIC SMALL LETTER U
    u'ф'        # 0xF4 -> CYRILLIC SMALL LETTER EF
    u'х'        # 0xF5 -> CYRILLIC SMALL LETTER HA
    u'ц'        # 0xF6 -> CYRILLIC SMALL LETTER TSE
    u'ч'        # 0xF7 -> CYRILLIC SMALL LETTER CHE
    u'ш'        # 0xF8 -> CYRILLIC SMALL LETTER SHA
    u'щ'        # 0xF9 -> CYRILLIC SMALL LETTER SHCHA
    u'ъ'        # 0xFA -> CYRILLIC SMALL LETTER HARD SIGN
    u'ы'        # 0xFB -> CYRILLIC SMALL LETTER YERU
    u'ь'        # 0xFC -> CYRILLIC SMALL LETTER SOFT SIGN
    u'э'        # 0xFD -> CYRILLIC SMALL LETTER E
    u'ю'        # 0xFE -> CYRILLIC SMALL LETTER YU
    u'я'        # 0xFF -> CYRILLIC SMALL LETTER YA
)

#  Encoding table
encoding_table = codecs.charmap_build(decoding_table)


def lookup(encoding):
    """Lookup the name of the encoding.

    Arguments:
        encoding (str): name of the encoding

    Returns:
        Codecs.CodecInfo if encoding is the name of the encoding of
            this file, None otherwise.
    """
    if encoding == 'meadowmari':
        return getregentry()
    return None

codecs.register(lookup)
