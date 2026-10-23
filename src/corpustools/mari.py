""" Python Character Mapping Codec cp1251 generated from 'MAPPINGS/VENDORS/MICSFT/WINDOWS/CP1251.TXT' with gencodec.py.

"""  # "

import codecs

#  Codec APIs


class Codec(codecs.Codec):
    """Implement the interface for stateless encoders/decoders."""

    def encode(self, instring, errors="strict"):
        """Encode the object instring.

        Args:
            instring (str): the string that should be encoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace', 'ignore',  'xmlcharrefreplace' or
                'backslashreplace'.

        Returns:
            (tuple[Any, int]): a tuple of (output object, length consumed)
        """
        return codecs.charmap_encode(instring, errors, encoding_table)

    def decode(self, instring, errors="strict"):
        """Decode the object instring.

        Args:
            instring (str): the string that should be decoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace' or 'ignore'.

        Returns:
            (tuple[Any, int]): a tuple of (output object, length consumed)
        """
        return codecs.charmap_decode(instring, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """Implement an IncrementalEncoder."""

    def encode(self, instring, final=False):
        """Encode instring.

        Args:
            instring (str): the string that should be encoded with this
                codec.

        Returns:
            (str): output object.
        """
        return codecs.charmap_encode(instring, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    """Implement an IncrementalDecoder."""

    def decode(self, instring, final=False):
        """Decode instring.

        Args:
            instring (str): the string that should be decoded with this
                codec.

        Returns:
            (str): output object.
        """
        return codecs.charmap_decode(instring, self.errors, decoding_table)[0]


#  encodings module API


def getregentry():
    """Get the info for this encoding."""
    return codecs.CodecInfo(
        name="meadowmari",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=codecs.StreamReader,
        streamwriter=codecs.StreamWriter,
    )


#  Decoding Table

decoding_table = (
    "\x00"  # 0x00 -> NULL
    "\x01"  # 0x01 -> START OF HEADING
    "\x02"  # 0x02 -> START OF TEXT
    "\x03"  # 0x03 -> END OF TEXT
    "\x04"  # 0x04 -> END OF TRANSMISSION
    "\x05"  # 0x05 -> ENQUIRY
    "\x06"  # 0x06 -> ACKNOWLEDGE
    "\x07"  # 0x07 -> BELL
    "\x08"  # 0x08 -> BACKSPACE
    "\t"  # 0x09 -> HORIZONTAL TABULATION
    "\n"  # 0x0A -> LINE FEED
    "\x0b"  # 0x0B -> VERTICAL TABULATION
    "\x0c"  # 0x0C -> FORM FEED
    "\r"  # 0x0D -> CARRIAGE RETURN
    "\x0e"  # 0x0E -> SHIFT OUT
    "\x0f"  # 0x0F -> SHIFT IN
    "\x10"  # 0x10 -> DATA LINK ESCAPE
    "\x11"  # 0x11 -> DEVICE CONTROL ONE
    "\x12"  # 0x12 -> DEVICE CONTROL TWO
    "\x13"  # 0x13 -> DEVICE CONTROL THREE
    "\x14"  # 0x14 -> DEVICE CONTROL FOUR
    "\x15"  # 0x15 -> NEGATIVE ACKNOWLEDGE
    "\x16"  # 0x16 -> SYNCHRONOUS IDLE
    "\x17"  # 0x17 -> END OF TRANSMISSION BLOCK
    "\x18"  # 0x18 -> CANCEL
    "\x19"  # 0x19 -> END OF MEDIUM
    "\x1a"  # 0x1A -> SUBSTITUTE
    "\x1b"  # 0x1B -> ESCAPE
    "\x1c"  # 0x1C -> FILE SEPARATOR
    "\x1d"  # 0x1D -> GROUP SEPARATOR
    "\x1e"  # 0x1E -> RECORD SEPARATOR
    "\x1f"  # 0x1F -> UNIT SEPARATOR
    " "  # 0x20 -> SPACE
    "!"  # 0x21 -> EXCLAMATION MARK
    '"'  # 0x22 -> QUOTATION MARK
    "#"  # 0x23 -> NUMBER SIGN
    "$"  # 0x24 -> DOLLAR SIGN
    "%"  # 0x25 -> PERCENT SIGN
    "&"  # 0x26 -> AMPERSAND
    "'"  # 0x27 -> APOSTROPHE
    "("  # 0x28 -> LEFT PARENTHESIS
    ")"  # 0x29 -> RIGHT PARENTHESIS
    "*"  # 0x2A -> ASTERISK
    "+"  # 0x2B -> PLUS SIGN
    ","  # 0x2C -> COMMA
    "-"  # 0x2D -> HYPHEN-MINUS
    "."  # 0x2E -> FULL STOP
    "/"  # 0x2F -> SOLIDUS
    "0"  # 0x30 -> DIGIT ZERO
    "1"  # 0x31 -> DIGIT ONE
    "2"  # 0x32 -> DIGIT TWO
    "3"  # 0x33 -> DIGIT THREE
    "4"  # 0x34 -> DIGIT FOUR
    "5"  # 0x35 -> DIGIT FIVE
    "6"  # 0x36 -> DIGIT SIX
    "7"  # 0x37 -> DIGIT SEVEN
    "8"  # 0x38 -> DIGIT EIGHT
    "9"  # 0x39 -> DIGIT NINE
    ":"  # 0x3A -> COLON
    ";"  # 0x3B -> SEMICOLON
    "<"  # 0x3C -> LESS-THAN SIGN
    "="  # 0x3D -> EQUALS SIGN
    ">"  # 0x3E -> GREATER-THAN SIGN
    "?"  # 0x3F -> QUESTION MARK
    "@"  # 0x40 -> COMMERCIAL AT
    "A"  # 0x41 -> LATIN CAPITAL LETTER A
    "B"  # 0x42 -> LATIN CAPITAL LETTER B
    "C"  # 0x43 -> LATIN CAPITAL LETTER C
    "D"  # 0x44 -> LATIN CAPITAL LETTER D
    "E"  # 0x45 -> LATIN CAPITAL LETTER E
    "F"  # 0x46 -> LATIN CAPITAL LETTER F
    "G"  # 0x47 -> LATIN CAPITAL LETTER G
    "H"  # 0x48 -> LATIN CAPITAL LETTER H
    "I"  # 0x49 -> LATIN CAPITAL LETTER I
    "J"  # 0x4A -> LATIN CAPITAL LETTER J
    "K"  # 0x4B -> LATIN CAPITAL LETTER K
    "L"  # 0x4C -> LATIN CAPITAL LETTER L
    "M"  # 0x4D -> LATIN CAPITAL LETTER M
    "N"  # 0x4E -> LATIN CAPITAL LETTER N
    "O"  # 0x4F -> LATIN CAPITAL LETTER O
    "P"  # 0x50 -> LATIN CAPITAL LETTER P
    "Q"  # 0x51 -> LATIN CAPITAL LETTER Q
    "R"  # 0x52 -> LATIN CAPITAL LETTER R
    "S"  # 0x53 -> LATIN CAPITAL LETTER S
    "T"  # 0x54 -> LATIN CAPITAL LETTER T
    "U"  # 0x55 -> LATIN CAPITAL LETTER U
    "V"  # 0x56 -> LATIN CAPITAL LETTER V
    "W"  # 0x57 -> LATIN CAPITAL LETTER W
    "X"  # 0x58 -> LATIN CAPITAL LETTER X
    "Y"  # 0x59 -> LATIN CAPITAL LETTER Y
    "Z"  # 0x5A -> LATIN CAPITAL LETTER Z
    "["  # 0x5B -> LEFT SQUARE BRACKET
    "\\"  # 0x5C -> REVERSE SOLIDUS
    "]"  # 0x5D -> RIGHT SQUARE BRACKET
    "^"  # 0x5E -> CIRCUMFLEX ACCENT
    "_"  # 0x5F -> LOW LINE
    "`"  # 0x60 -> GRAVE ACCENT
    "a"  # 0x61 -> LATIN SMALL LETTER A
    "b"  # 0x62 -> LATIN SMALL LETTER B
    "c"  # 0x63 -> LATIN SMALL LETTER C
    "d"  # 0x64 -> LATIN SMALL LETTER D
    "e"  # 0x65 -> LATIN SMALL LETTER E
    "f"  # 0x66 -> LATIN SMALL LETTER F
    "g"  # 0x67 -> LATIN SMALL LETTER G
    "h"  # 0x68 -> LATIN SMALL LETTER H
    "i"  # 0x69 -> LATIN SMALL LETTER I
    "j"  # 0x6A -> LATIN SMALL LETTER J
    "k"  # 0x6B -> LATIN SMALL LETTER K
    "l"  # 0x6C -> LATIN SMALL LETTER L
    "m"  # 0x6D -> LATIN SMALL LETTER M
    "n"  # 0x6E -> LATIN SMALL LETTER N
    "o"  # 0x6F -> LATIN SMALL LETTER O
    "p"  # 0x70 -> LATIN SMALL LETTER P
    "q"  # 0x71 -> LATIN SMALL LETTER Q
    "r"  # 0x72 -> LATIN SMALL LETTER R
    "s"  # 0x73 -> LATIN SMALL LETTER S
    "t"  # 0x74 -> LATIN SMALL LETTER T
    "u"  # 0x75 -> LATIN SMALL LETTER U
    "v"  # 0x76 -> LATIN SMALL LETTER V
    "w"  # 0x77 -> LATIN SMALL LETTER W
    "x"  # 0x78 -> LATIN SMALL LETTER X
    "y"  # 0x79 -> LATIN SMALL LETTER Y
    "z"  # 0x7A -> LATIN SMALL LETTER Z
    "{"  # 0x7B -> LEFT CURLY BRACKET
    "|"  # 0x7C -> VERTICAL LINE
    "}"  # 0x7D -> RIGHT CURLY BRACKET
    "~"  # 0x7E -> TILDE
    "\x7f"  # 0x7F -> DELETE
    "Ђ"  # 0x80 -> CYRILLIC CAPITAL LETTER DJE
    "Ѓ"  # 0x81 -> CYRILLIC CAPITAL LETTER GJE
    "‚"  # 0x82 -> SINGLE LOW-9 QUOTATION MARK
    "ѓ"  # 0x83 -> CYRILLIC SMALL LETTER GJE
    "„"  # 0x84 -> DOUBLE LOW-9 QUOTATION MARK
    "…"  # 0x85 -> HORIZONTAL ELLIPSIS
    "†"  # 0x86 -> DAGGER
    "‡"  # 0x87 -> DOUBLE DAGGER
    "Ҥ"  # 0x88 -> CYRILLIC CAPITAL LIGATURE EN GHE
    "ҥ"  # 0x89 -> CYRILLIC SMALL LIGATURE EN
    "Љ"  # 0x8A -> CYRILLIC CAPITAL LETTER LJE
    "‹"  # 0x8B -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    "Њ"  # 0x8C -> CYRILLIC CAPITAL LETTER NJE
    "Ќ"  # 0x8D -> CYRILLIC CAPITAL LETTER KJE
    "Ћ"  # 0x8E -> CYRILLIC CAPITAL LETTER TSHE
    "Џ"  # 0x8F -> CYRILLIC CAPITAL LETTER DZHE
    "ђ"  # 0x90 -> CYRILLIC SMALL LETTER DJE
    "\u2018"  # 0x91 -> LEFT SINGLE QUOTATION MARK
    "\u2019"  # 0x92 -> RIGHT SINGLE QUOTATION MARK
    "\u201c"  # 0x93 -> LEFT DOUBLE QUOTATION MARK
    "\u201d"  # 0x94 -> RIGHT DOUBLE QUOTATION MARK
    "\u2022"  # 0x95 -> BULLET
    "\u2013"  # 0x96 -> EN DASH
    "\u2014"  # 0x97 -> EM DASH
    "\ufffe"  # 0x98 -> UNDEFINED
    "Ӱ"  # 0x99 -> CYRILLIC CAPITAL LETTER U WITH DIAERESIS
    "љ"  # 0x9A -> CYRILLIC SMALL LETTER LJE
    "›"  # 0x9B -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    "њ"  # 0x9C -> CYRILLIC SMALL LETTER NJE
    "ќ"  # 0x9D -> CYRILLIC SMALL LETTER KJE
    "ћ"  # 0x9E -> CYRILLIC SMALL LETTER TSHE
    "џ"  # 0x9F -> CYRILLIC SMALL LETTER DZHE
    "\xa0"  # 0xA0 -> NO-BREAK SPACE
    "Ў"  # 0xA1 -> CYRILLIC CAPITAL LETTER SHORT U
    "ӱ"  # 0xA2 -> CYRILLIC SMALL LETTER U WITH DIAERESIS
    "Ј"  # 0xA3 -> CYRILLIC CAPITAL LETTER JE
    "\xa4"  # 0xA4 -> CURRENCY SIGN
    "Ґ"  # 0xA5 -> CYRILLIC CAPITAL LETTER GHE WITH UPTURN
    "\xa6"  # 0xA6 -> BROKEN BAR
    "\xa7"  # 0xA7 -> SECTION SIGN
    "Ё"  # 0xA8 -> CYRILLIC CAPITAL LETTER IO
    "\xa9"  # 0xA9 -> COPYRIGHT SIGN
    "Ӧ"  # 0xAA -> CYRILLIC CAPITAL LETTER O WITH DIAERESIS
    "\xab"  # 0xAB -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\xac"  # 0xAC -> NOT SIGN
    "\xad"  # 0xAD -> SOFT HYPHEN
    "®"  # 0xAE -> REGISTERED SIGN
    "Ї"  # 0xAF -> CYRILLIC CAPITAL LETTER YI
    "\xb0"  # 0xB0 -> DEGREE SIGN
    "\xb1"  # 0xB1 -> PLUS-MINUS SIGN
    "І"  # 0xB2 -> CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
    "і"  # 0xB3 -> CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
    "ґ"  # 0xB4 -> CYRILLIC SMALL LETTER GHE WITH UPTURN
    "\xb5"  # 0xB5 -> MICRO SIGN
    "\xb6"  # 0xB6 -> PILCROW SIGN
    "\xb7"  # 0xB7 -> MIDDLE DOT
    "ё"  # 0xB8 -> CYRILLIC SMALL LETTER IO
    "\u2116"  # 0xB9 -> NUMERO SIGN
    "ӧ"  # 0xBA -> CYRILLIC SMALL LETTER O WITH DIAERESIS
    "\xbb"  # 0xBB -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "ј"  # 0xBC -> CYRILLIC SMALL LETTER JE
    "Ѕ"  # 0xBD -> CYRILLIC CAPITAL LETTER DZE
    "ѕ"  # 0xBE -> CYRILLIC SMALL LETTER DZE
    "ї"  # 0xBF -> CYRILLIC SMALL LETTER YI
    "А"  # 0xC0 -> CYRILLIC CAPITAL LETTER A
    "Б"  # 0xC1 -> CYRILLIC CAPITAL LETTER BE
    "В"  # 0xC2 -> CYRILLIC CAPITAL LETTER VE
    "Г"  # 0xC3 -> CYRILLIC CAPITAL LETTER GHE
    "Д"  # 0xC4 -> CYRILLIC CAPITAL LETTER DE
    "Е"  # 0xC5 -> CYRILLIC CAPITAL LETTER IE
    "Ж"  # 0xC6 -> CYRILLIC CAPITAL LETTER ZHE
    "З"  # 0xC7 -> CYRILLIC CAPITAL LETTER ZE
    "И"  # 0xC8 -> CYRILLIC CAPITAL LETTER I
    "Й"  # 0xC9 -> CYRILLIC CAPITAL LETTER SHORT I
    "К"  # 0xCA -> CYRILLIC CAPITAL LETTER KA
    "Л"  # 0xCB -> CYRILLIC CAPITAL LETTER EL
    "М"  # 0xCC -> CYRILLIC CAPITAL LETTER EM
    "Н"  # 0xCD -> CYRILLIC CAPITAL LETTER EN
    "О"  # 0xCE -> CYRILLIC CAPITAL LETTER O
    "П"  # 0xCF -> CYRILLIC CAPITAL LETTER PE
    "Р"  # 0xD0 -> CYRILLIC CAPITAL LETTER ER
    "С"  # 0xD1 -> CYRILLIC CAPITAL LETTER ES
    "Т"  # 0xD2 -> CYRILLIC CAPITAL LETTER TE
    "У"  # 0xD3 -> CYRILLIC CAPITAL LETTER U
    "Ф"  # 0xD4 -> CYRILLIC CAPITAL LETTER EF
    "Х"  # 0xD5 -> CYRILLIC CAPITAL LETTER HA
    "Ц"  # 0xD6 -> CYRILLIC CAPITAL LETTER TSE
    "Ч"  # 0xD7 -> CYRILLIC CAPITAL LETTER CHE
    "Ш"  # 0xD8 -> CYRILLIC CAPITAL LETTER SHA
    "Щ"  # 0xD9 -> CYRILLIC CAPITAL LETTER SHCHA
    "Ъ"  # 0xDA -> CYRILLIC CAPITAL LETTER HARD SIGN
    "Ы"  # 0xDB -> CYRILLIC CAPITAL LETTER YERU
    "Ь"  # 0xDC -> CYRILLIC CAPITAL LETTER SOFT SIGN
    "Э"  # 0xDD -> CYRILLIC CAPITAL LETTER E
    "Ю"  # 0xDE -> CYRILLIC CAPITAL LETTER YU
    "Я"  # 0xDF -> CYRILLIC CAPITAL LETTER YA
    "а"  # 0xE0 -> CYRILLIC SMALL LETTER A
    "б"  # 0xE1 -> CYRILLIC SMALL LETTER BE
    "в"  # 0xE2 -> CYRILLIC SMALL LETTER VE
    "г"  # 0xE3 -> CYRILLIC SMALL LETTER GHE
    "д"  # 0xE4 -> CYRILLIC SMALL LETTER DE
    "е"  # 0xE5 -> CYRILLIC SMALL LETTER IE
    "ж"  # 0xE6 -> CYRILLIC SMALL LETTER ZHE
    "з"  # 0xE7 -> CYRILLIC SMALL LETTER ZE
    "и"  # 0xE8 -> CYRILLIC SMALL LETTER I
    "й"  # 0xE9 -> CYRILLIC SMALL LETTER SHORT I
    "к"  # 0xEA -> CYRILLIC SMALL LETTER KA
    "л"  # 0xEB -> CYRILLIC SMALL LETTER EL
    "м"  # 0xEC -> CYRILLIC SMALL LETTER EM
    "н"  # 0xED -> CYRILLIC SMALL LETTER EN
    "о"  # 0xEE -> CYRILLIC SMALL LETTER O
    "п"  # 0xEF -> CYRILLIC SMALL LETTER PE
    "р"  # 0xF0 -> CYRILLIC SMALL LETTER ER
    "с"  # 0xF1 -> CYRILLIC SMALL LETTER ES
    "т"  # 0xF2 -> CYRILLIC SMALL LETTER TE
    "у"  # 0xF3 -> CYRILLIC SMALL LETTER U
    "ф"  # 0xF4 -> CYRILLIC SMALL LETTER EF
    "х"  # 0xF5 -> CYRILLIC SMALL LETTER HA
    "ц"  # 0xF6 -> CYRILLIC SMALL LETTER TSE
    "ч"  # 0xF7 -> CYRILLIC SMALL LETTER CHE
    "ш"  # 0xF8 -> CYRILLIC SMALL LETTER SHA
    "щ"  # 0xF9 -> CYRILLIC SMALL LETTER SHCHA
    "ъ"  # 0xFA -> CYRILLIC SMALL LETTER HARD SIGN
    "ы"  # 0xFB -> CYRILLIC SMALL LETTER YERU
    "ь"  # 0xFC -> CYRILLIC SMALL LETTER SOFT SIGN
    "э"  # 0xFD -> CYRILLIC SMALL LETTER E
    "ю"  # 0xFE -> CYRILLIC SMALL LETTER YU
    "я"  # 0xFF -> CYRILLIC SMALL LETTER YA
)

#  Encoding table
encoding_table = codecs.charmap_build(decoding_table)


def lookup(encoding):
    """Lookup the name of the encoding.

    Args:
        encoding (str): name of the encoding

    Returns:
        (Codecs.CodecInfo|None): Codecs.CodecInfo if encoding is the name
            of the encoding of this file, None otherwise.
    """
    if encoding == "meadowmari":
        return getregentry()
    return None


codecs.register(lookup)
