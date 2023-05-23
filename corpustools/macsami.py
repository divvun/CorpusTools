# Disable pylint warnings to follow the coding style of the python
# this class.
# pylint: disable=W0232, C0103
"""Python Character Mapping Codec for macsami."""

import codecs

#  Codec APIs


class Codec(codecs.Codec):
    """Implement the interface for stateless encoders/decoders."""

    def encode(self, instring, errors="strict"):
        """Encode the object input.

        Args:
            instring (str): the string that should be encoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace', 'ignore',  'xmlcharrefreplace' or
                'backslashreplace'.

        Returns:
            (tuple[bytes, int): a tuple of output object and length consumed
        """
        return codecs.charmap_encode(instring, errors, encoding_table)

    def decode(self, instring, errors="strict"):
        """Decode the object input.

        Args:
            instring (str): the string that should be decoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace' or 'ignore'.

        Returns:
            (tuple[bytes, int): a tuple of output object and length consumed
        """
        return codecs.charmap_decode(instring, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """Implement an IncrementalEncoder."""

    def encode(self, instring, final=False):
        """Encode input.

        Args:
            instring (str): the string that should be encoded with this
                codec.

        Returns:
            (tuple[bytes, int): a tuple of output object and length consumed
        """
        return codecs.charmap_encode(instring, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    """Implement an IncrementalDecoder."""

    def decode(self, instring, final=False):
        """Decode input.

        Args:
            instring (str): the string that should be decoded with this
                codec.

        Returns:
            (tuple[bytes, int): a tuple of output object and length consumed
        """
        return codecs.charmap_decode(instring, self.errors, decoding_table)[0]


#  encodings module API


def getregentry():
    """Get the info for this encoding."""
    return codecs.CodecInfo(
        name="macsami",
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
    "\x09"  # 0x09 -> HORIZONTAL TABULATION
    "\x0A"  # 0x0a -> LINE FEED
    "\x0B"  # 0x0b -> VERTICAL TABULATION
    "\x0C"  # 0x0c -> FORM FEED
    "\x0D"  # 0x0d -> CARRIAGE RETURN
    "\x0E"  # 0x0e -> SHIFT OUT
    "\x0F"  # 0x0f -> SHIFT IN
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
    "\x1A"  # 0x1a -> SUBSTITUTE
    "\x1B"  # 0x1b -> ESCAPE
    "\x1C"  # 0x1c -> FILE SEPARATOR
    "\x1D"  # 0x1d -> GROUP SEPARATOR
    "\x1E"  # 0x1e -> RECORD SEPARATOR
    "\x1F"  # 0x1f -> UNIT SEPARATOR
    "\x20"  # 0x20 -> SPACE
    "\x21"  # 0x21 -> EXCLAMATION MARK
    "\x22"  # 0x22 -> QUOTATION MARK
    "\x23"  # 0x23 -> NUMBER SIGN
    "\x24"  # 0x24 -> DOLLAR SIGN
    "\x25"  # 0x25 -> PERCENT SIGN
    "\x26"  # 0x26 -> AMPERSAND
    "\x27"  # 0x27 -> APOSTROPHE
    "\x28"  # 0x28 -> LEFT PARENTHESIS
    "\x29"  # 0x29 -> RIGHT PARENTHESIS
    "\x2A"  # 0x2a -> ASTERISK
    "\x2B"  # 0x2b -> PLUS SIGN
    "\x2C"  # 0x2c -> COMMA
    "\x2D"  # 0x2d -> HYPHEN-MINUS
    "\x2E"  # 0x2e -> FULL STOP
    "\x2F"  # 0x2f -> SOLIDUS
    "\x30"  # 0x30 -> DIGIT ZERO
    "\x31"  # 0x31 -> DIGIT ONE
    "\x32"  # 0x32 -> DIGIT TWO
    "\x33"  # 0x33 -> DIGIT THREE
    "\x34"  # 0x34 -> DIGIT FOUR
    "\x35"  # 0x35 -> DIGIT FIVE
    "\x36"  # 0x36 -> DIGIT SIX
    "\x37"  # 0x37 -> DIGIT SEVEN
    "\x38"  # 0x38 -> DIGIT EIGHT
    "\x39"  # 0x39 -> DIGIT NINE
    "\x3A"  # 0x3a -> COLON
    "\x3B"  # 0x3b -> SEMICOLON
    "\x3C"  # 0x3c -> LESS-THAN SIGN
    "\x3D"  # 0x3d -> EQUALS SIGN
    "\x3E"  # 0x3e -> GREATER-THAN SIGN
    "\x3F"  # 0x3f -> QUESTION MARK
    "\x40"  # 0x40 -> COMMERCIAL AT
    "\x41"  # 0x41 -> LATIN CAPITAL LETTER A
    "\x42"  # 0x42 -> LATIN CAPITAL LETTER B
    "\x43"  # 0x43 -> LATIN CAPITAL LETTER C
    "\x44"  # 0x44 -> LATIN CAPITAL LETTER D
    "\x45"  # 0x45 -> LATIN CAPITAL LETTER E
    "\x46"  # 0x46 -> LATIN CAPITAL LETTER F
    "\x47"  # 0x47 -> LATIN CAPITAL LETTER G
    "\x48"  # 0x48 -> LATIN CAPITAL LETTER H
    "\x49"  # 0x49 -> LATIN CAPITAL LETTER I
    "\x4A"  # 0x4a -> LATIN CAPITAL LETTER J
    "\x4B"  # 0x4b -> LATIN CAPITAL LETTER K
    "\x4C"  # 0x4c -> LATIN CAPITAL LETTER L
    "\x4D"  # 0x4d -> LATIN CAPITAL LETTER M
    "\x4E"  # 0x4e -> LATIN CAPITAL LETTER N
    "\x4F"  # 0x4f -> LATIN CAPITAL LETTER O
    "\x50"  # 0x50 -> LATIN CAPITAL LETTER P
    "\x51"  # 0x51 -> LATIN CAPITAL LETTER Q
    "\x52"  # 0x52 -> LATIN CAPITAL LETTER R
    "\x53"  # 0x53 -> LATIN CAPITAL LETTER S
    "\x54"  # 0x54 -> LATIN CAPITAL LETTER T
    "\x55"  # 0x55 -> LATIN CAPITAL LETTER U
    "\x56"  # 0x56 -> LATIN CAPITAL LETTER V
    "\x57"  # 0x57 -> LATIN CAPITAL LETTER W
    "\x58"  # 0x58 -> LATIN CAPITAL LETTER X
    "\x59"  # 0x59 -> LATIN CAPITAL LETTER Y
    "\x5A"  # 0x5a -> LATIN CAPITAL LETTER Z
    "\x5B"  # 0x5b -> LEFT SQUARE BRACKET
    "\x5C"  # 0x5c -> REVERSE SOLIDUS
    "\x5D"  # 0x5d -> RIGHT SQUARE BRACKET
    "\x5E"  # 0x5e -> CIRCUMFLEX ACCENT
    "\x5F"  # 0x5f -> LOW LINE
    "\x60"  # 0x60 -> GRAVE ACCENT
    "\x61"  # 0x61 -> LATIN SMALL LETTER A
    "\x62"  # 0x62 -> LATIN SMALL LETTER B
    "\x63"  # 0x63 -> LATIN SMALL LETTER C
    "\x64"  # 0x64 -> LATIN SMALL LETTER D
    "\x65"  # 0x65 -> LATIN SMALL LETTER E
    "\x66"  # 0x66 -> LATIN SMALL LETTER F
    "\x67"  # 0x67 -> LATIN SMALL LETTER G
    "\x68"  # 0x68 -> LATIN SMALL LETTER H
    "\x69"  # 0x69 -> LATIN SMALL LETTER I
    "\x6A"  # 0x6a -> LATIN SMALL LETTER J
    "\x6B"  # 0x6b -> LATIN SMALL LETTER K
    "\x6C"  # 0x6c -> LATIN SMALL LETTER L
    "\x6D"  # 0x6d -> LATIN SMALL LETTER M
    "\x6E"  # 0x6e -> LATIN SMALL LETTER N
    "\x6F"  # 0x6f -> LATIN SMALL LETTER O
    "\x70"  # 0x70 -> LATIN SMALL LETTER P
    "\x71"  # 0x71 -> LATIN SMALL LETTER Q
    "\x72"  # 0x72 -> LATIN SMALL LETTER R
    "\x73"  # 0x73 -> LATIN SMALL LETTER S
    "\x74"  # 0x74 -> LATIN SMALL LETTER T
    "\x75"  # 0x75 -> LATIN SMALL LETTER U
    "\x76"  # 0x76 -> LATIN SMALL LETTER V
    "\x77"  # 0x77 -> LATIN SMALL LETTER W
    "\x78"  # 0x78 -> LATIN SMALL LETTER X
    "\x79"  # 0x79 -> LATIN SMALL LETTER Y
    "\x7A"  # 0x7a -> LATIN SMALL LETTER Z
    "\x7B"  # 0x7b -> LEFT CURLY BRACKET
    "\x7C"  # 0x7c -> VERTICAL LINE
    "\x7D"  # 0x7d -> RIGHT CURLY BRACKET
    "\x7E"  # 0x7e -> TILDE
    "\x7F"  # 0x7f -> DELETE
    "\xC4"  # 0x80 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    "\xC5"  # 0x81 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    "\xC7"  # 0x82 -> LATIN CAPITAL LETTER C WITH CEDILLA
    "\xC9"  # 0x83 -> LATIN CAPITAL LETTER E WITH ACUTE
    "\xD1"  # 0x84 -> LATIN CAPITAL LETTER N WITH TILDE
    "\xD6"  # 0x85 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    "\xDC"  # 0x86 -> LATIN CAPITAL LETTER U WITH DIAERESIS
    "\xE1"  # 0x87 -> LATIN SMALL LETTER A WITH ACUTE
    "\xE0"  # 0x88 -> LATIN SMALL LETTER A WITH GRAVE
    "\xE2"  # 0x89 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    "\xE4"  # 0x8a -> LATIN SMALL LETTER A WITH DIAERESIS
    "\xE3"  # 0x8b -> LATIN SMALL LETTER A WITH TILDE
    "\xE5"  # 0x8c -> LATIN SMALL LETTER A WITH RING ABOVE
    "\xE7"  # 0x8d -> LATIN SMALL LETTER C WITH CEDILLA
    "\xE9"  # 0x8e -> LATIN SMALL LETTER E WITH ACUTE
    "\xE8"  # 0x8f -> LATIN SMALL LETTER E WITH GRAVE
    "\xEA"  # 0x90 -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    "\xEB"  # 0x91 -> LATIN SMALL LETTER E WITH DIAERESIS
    "\xED"  # 0x92 -> LATIN SMALL LETTER I WITH ACUTE
    "\xEC"  # 0x93 -> LATIN SMALL LETTER I WITH GRAVE
    "\xEE"  # 0x94 -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    "\xEF"  # 0x95 -> LATIN SMALL LETTER I WITH DIAERESIS
    "\xF1"  # 0x96 -> LATIN SMALL LETTER N WITH TILDE
    "\xF3"  # 0x97 -> LATIN SMALL LETTER O WITH ACUTE
    "\xF2"  # 0x98 -> LATIN SMALL LETTER O WITH GRAVE
    "\xF4"  # 0x99 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    "\xF6"  # 0x9a -> LATIN SMALL LETTER O WITH DIAERESIS
    "\xF5"  # 0x9b -> LATIN SMALL LETTER O WITH TILDE
    "\xFA"  # 0x9c -> LATIN SMALL LETTER U WITH ACUTE
    "\xF9"  # 0x9d -> LATIN SMALL LETTER U WITH GRAVE
    "\xFB"  # 0x9e -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    "\xFC"  # 0x9f -> LATIN SMALL LETTER U WITH DIAERESIS
    "\xDD"  # 0xa0 -> LATIN CAPITAL LETTER Y WITH ACUTE
    "\xB0"  # 0xa1 -> DEGREE SIGN
    "\u010C"  # 0xa2 -> LATIN CAPITAL LETTER C WITH CARON
    "\xA3"  # 0xa3 -> POUND SIGN
    "\xA7"  # 0xa4 -> SECTION SIGN
    "\u2022"  # 0xa5 -> BULLET
    "\xB6"  # 0xa6 -> PILCROW SIGN
    "\xDF"  # 0xa7 -> LATIN SMALL LETTER SHARP S (German)
    "\xAE"  # 0xa8 -> REGISTERED SIGN
    "\xA9"  # 0xa9 -> COPYRIGHT SIGN
    "\u2122"  # 0xaa -> TRADE MARK SIGN
    "\xB4"  # 0xab -> ACUTE ACCENT
    "\xA8"  # 0xac -> DIAERESIS
    "\u2260"  # 0xad -> NOT EQUAL TO
    "\xC6"  # 0xae -> LATIN CAPITAL LETTER AE
    "\xD8"  # 0xaf -> LATIN CAPITAL LETTER O WITH STROKE
    "\u0110"  # 0xb0 -> LATIN CAPITAL LETTER D WITH STROKE
    "\u014A"  # 0xb1 -> LATIN CAPITAL LETTER ENG
    "\u021E"  # 0xb2 -> LATIN CAPITAL LETTER H WITH CARON
    "\u021F"  # 0xb3 -> LATIN SMALL LETTER H WITH CARON
    "\u0160"  # 0xb4 -> LATIN CAPITAL LETTER S WITH CARON
    "\u0166"  # 0xb5 -> LATIN CAPITAL LETTER T WITH STROKE
    "\u2202"  # 0xb6 -> PARTIAL DIFFERENTIAL
    "\u017D"  # 0xb7 -> LATIN CAPITAL LETTER Z WITH CARON
    "\u010D"  # 0xb8 -> LATIN SMALL LETTER C WITH CARON
    "\u0111"  # 0xb9 -> LATIN SMALL LETTER D WITH STROKE
    "\u014B"  # 0xba -> LATIN SMALL LETTER ENG
    "\u0161"  # 0xbb -> LATIN SMALL LETTER S WITH CARON
    "\u0167"  # 0xbc -> LATIN SMALL LETTER T WITH STROKE
    "\u017E"  # 0xbd -> LATIN SMALL LETTER Z WITH CARON
    "\xE6"  # 0xbe -> LATIN SMALL LETTER AE
    "\xF8"  # 0xbf -> LATIN SMALL LETTER O WITH STROKE
    "\xBF"  # 0xc0 -> INVERTED QUESTION MARK
    "\xA1"  # 0xc1 -> INVERTED EXCLAMATION MARK
    "\xAC"  # 0xc2 -> NOT SIGN
    "\u221A"  # 0xc3 -> SQUARE ROOT
    "\u0192"  # 0xc4 -> LATIN SMALL LETTER F WITH HOOK
    "\u2248"  # 0xc5 -> ALMOST EQUAL TO
    "\u2206"  # 0xc6 -> INCREMENT
    "\xAB"  # 0xc7 -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\xBB"  # 0xc8 -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\u2026"  # 0xc9 -> HORIZONTAL ELLIPSIS
    "\xA0"  # 0xca -> NO-BREAK SPACE
    "\xC0"  # 0xcb -> LATIN CAPITAL LETTER A WITH GRAVE
    "\xC3"  # 0xcc -> LATIN CAPITAL LETTER A WITH TILDE
    "\xD5"  # 0xcd -> LATIN CAPITAL LETTER O WITH TILDE
    "\u0152"  # 0xce -> LATIN CAPITAL LIGATURE OE
    "\u0153"  # 0xcf -> LATIN SMALL LIGATURE OE
    "\u2013"  # 0xd0 -> EN DASH
    "\u2014"  # 0xd1 -> EM DASH
    "\u201C"  # 0xd2 -> LEFT DOUBLE QUOTATION MARK
    "\u201D"  # 0xd3 -> RIGHT DOUBLE QUOTATION MARK
    "\u2018"  # 0xd4 -> LEFT SINGLE QUOTATION MARK
    "\u2019"  # 0xd5 -> RIGHT SINGLE QUOTATION MARK
    "\xF7"  # 0xd6 -> DIVISION SIGN
    "\u25CA"  # 0xd7 -> LOZENGE
    "\xFF"  # 0xd8 -> LATIN SMALL LETTER Y WITH DIAERESIS
    "\u0178"  # 0xd9 -> LATIN CAPITAL LETTER Y WITH DIAERESIS
    "\u2044"  # 0xda -> FRACTION SLASH
    "\xA4"  # 0xdb -> CURRENCY SIGN
    "\xD0"  # 0xdc -> LATIN CAPITAL LETTER ETH
    "\xF0"  # 0xdd -> LATIN SMALL LETTER ETH
    "\xDE"  # 0xde -> LATIN CAPITAL LETTER THORN
    "\xFE"  # 0xdf -> LATIN SMALL LETTER THORN
    "\xFD"  # 0xe0 -> LATIN SMALL LETTER Y WITH ACUTE
    "\xB7"  # 0xe1 -> MIDDLE DOT
    "\u201A"  # 0xe2 -> SINGLE LOW-9 QUOTATION MARK
    "\u201E"  # 0xe3 -> DOUBLE LOW-9 QUOTATION MARK
    "\u2030"  # 0xe4 -> PER MILLE SIGN
    "\xC2"  # 0xe5 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    "\xCA"  # 0xe6 -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    "\xC1"  # 0xe7 -> LATIN CAPITAL LETTER A WITH ACUTE
    "\xCB"  # 0xe8 -> LATIN CAPITAL LETTER E WITH DIAERESIS
    "\xC8"  # 0xe9 -> LATIN CAPITAL LETTER E WITH GRAVE
    "\xCD"  # 0xea -> LATIN CAPITAL LETTER I WITH ACUTE
    "\xCE"  # 0xeb -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    "\xCF"  # 0xec -> LATIN CAPITAL LETTER I WITH DIAERESIS
    "\xCC"  # 0xed -> LATIN CAPITAL LETTER I WITH GRAVE
    "\xD3"  # 0xee -> LATIN CAPITAL LETTER O WITH ACUTE
    "\xD4"  # 0xef -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    "\uF8FF"  # 0xf0 -> APPLE SIGN
    "\xD2"  # 0xf1 -> LATIN CAPITAL LETTER O WITH GRAVE
    "\xDA"  # 0xf2 -> LATIN CAPITAL LETTER U WITH ACUTE
    "\xDB"  # 0xf3 -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    "\xD9"  # 0xf4 -> LATIN CAPITAL LETTER U WITH GRAVE
    "\u0131"  # 0xf5 -> LATIN SMALL LETTER DOTLESS I
    "\u01B7"  # 0xf6 -> LATIN CAPITAL LETTER EZH
    "\u0292"  # 0xf7 -> LATIN SMALL LETTER EZH
    "\u01EE"  # 0xf8 -> LATIN CAPITAL LETTER EZH WITH CARON
    "\u01EF"  # 0xf9 -> LATIN SMALL LETTER EZH WITH CARON
    "\u01E4"  # 0xfa -> LATIN CAPITAL LETTER G WITH STROKE
    "\u01E5"  # 0xfb -> LATIN SMALL LETTER G WITH STROKE
    "\u01E6"  # 0xfc -> LATIN CAPITAL LETTER G WITH CARON
    "\u01E7"  # 0xfd -> LATIN SMALL LETTER G WITH CARON
    "\u01E8"  # 0xfe -> LATIN CAPITAL LETTER K WITH CARON
    "\u01E9"  # 0xff -> LATIN SMALL LETTER K WITH CARON
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
    if encoding == "macsami":
        return getregentry()
    return None


codecs.register(lookup)
