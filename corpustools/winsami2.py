# Disable pylint warnings to follow the coding style of the python
# this class.
# pylint: disable=W0232, C0103
"""Python Character Mapping Codec for winsami2."""

import codecs

#  Codec APIs


class Codec(codecs.Codec):
    """Implement the interface for stateless encoders/decoders."""

    def encode(self, instring, errors='strict'):
        """Encode the object instring.

        Args:
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

        Args:
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

        Args:
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

        Args:
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
        name='ws2',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=codecs.StreamReader,
        streamwriter=codecs.StreamWriter,
    )


#  Decoding Table

decoding_table = (
    u'\u0000'  # 0x00 -> NULL
    u'\u0001'  # 0x01 -> START OF HEADING
    u'\u0002'  # 0x02 -> START OF TEXT
    u'\u0003'  # 0x03 -> END OF TEXT
    u'\u0004'  # 0x04 -> END OF TRANSMISSION
    u'\u0005'  # 0x05 -> ENQUIRY
    u'\u0006'  # 0x06 -> ACKNOWLEDGE
    u'\u0007'  # 0x07 -> BELL
    u'\u0008'  # 0x08 -> BACKSPACE
    u'\u0009'  # 0x09 -> CHARACTER TABULATION
    u'\u000A'  # 0x0a -> LINE FEED
    u'\u000B'  # 0x0b -> LINE TABULATION
    u'\u000C'  # 0x0c -> FORM FEED
    u'\u000D'  # 0x0d -> CARRIAGE RETURN
    u'\u000E'  # 0x0e -> SHIFT OUT
    u'\u000F'  # 0x0f -> SHIFT IN
    u'\u0010'  # 0x10 -> DATALINK ESCAPE
    u'\u0011'  # 0x11 -> DEVICE CONTROL ONE
    u'\u0012'  # 0x12 -> DEVICE CONTROL TWO
    u'\u0013'  # 0x13 -> DEVICE CONTROL THREE
    u'\u0014'  # 0x14 -> DEVICE CONTROL FOUR
    u'\u0015'  # 0x15 -> NEGATIVE ACKNOWLEDGE
    u'\u0016'  # 0x16 -> SYNCHRONOUS IDLE
    u'\u0017'  # 0x17 -> END OF TRANSMISSION BLOCK
    u'\u0018'  # 0x18 -> CANCEL
    u'\u0019'  # 0x19 -> END OF MEDIUM
    u'\u001A'  # 0x1a -> SUBSTITUTE
    u'\u001B'  # 0x1b -> ESCAPE
    u'\u001C'  # 0x1c -> FILE SEPARATOR
    u'\u001D'  # 0x1d -> GROUP SEPARATOR
    u'\u001E'  # 0x1e -> RECORD SEPARATOR
    u'\u001F'  # 0x1f -> UNIT SEPARATOR
    u'\u0020'  # 0x20 -> SPACE
    u'\u0021'  # 0x21 -> EXCLAMATION MARK
    u'\u0022'  # 0x22 -> QUOTATION MARK
    u'\u0023'  # 0x23 -> NUMBER SIGN
    u'\u0024'  # 0x24 -> DOLLAR SIGN
    u'\u0025'  # 0x25 -> PERCENT SIGN
    u'\u0026'  # 0x26 -> AMPERSAND
    u'\u0027'  # 0x27 -> APOSTROPHE
    u'\u0028'  # 0x28 -> LEFT PARENTHESIS
    u'\u0029'  # 0x29 -> RIGHT PARENTHESIS
    u'\u002A'  # 0x2a -> ASTERISK
    u'\u002B'  # 0x2b -> PLUS SIGN
    u'\u002C'  # 0x2c -> COMMA
    u'\u002D'  # 0x2d -> HYPHEN-MINUS
    u'\u002E'  # 0x2e -> FULL STOP
    u'\u002F'  # 0x2f -> SOLIDUS
    u'\u0030'  # 0x30 -> DIGIT ZERO
    u'\u0031'  # 0x31 -> DIGIT ONE
    u'\u0032'  # 0x32 -> DIGIT TWO
    u'\u0033'  # 0x33 -> DIGIT THREE
    u'\u0034'  # 0x34 -> DIGIT FOUR
    u'\u0035'  # 0x35 -> DIGIT FIVE
    u'\u0036'  # 0x36 -> DIGIT SIX
    u'\u0037'  # 0x37 -> DIGIT SEVEN
    u'\u0038'  # 0x38 -> DIGIT EIGHT
    u'\u0039'  # 0x39 -> DIGIT NINE
    u'\u003A'  # 0x3a -> COLON
    u'\u003B'  # 0x3b -> SEMICOLON
    u'\u003C'  # 0x3c -> LESS-THAN SIGN
    u'\u003D'  # 0x3d -> EQUALS SIGN
    u'\u003E'  # 0x3e -> GREATER-THAN SIGN
    u'\u003F'  # 0x3f -> QUESTION MARK
    u'\u0040'  # 0x40 -> COMMERCIAL AT
    u'\u0041'  # 0x41 -> LATIN CAPITAL LETTER A
    u'\u0042'  # 0x42 -> LATIN CAPITAL LETTER B
    u'\u0043'  # 0x43 -> LATIN CAPITAL LETTER C
    u'\u0044'  # 0x44 -> LATIN CAPITAL LETTER D
    u'\u0045'  # 0x45 -> LATIN CAPITAL LETTER E
    u'\u0046'  # 0x46 -> LATIN CAPITAL LETTER F
    u'\u0047'  # 0x47 -> LATIN CAPITAL LETTER G
    u'\u0048'  # 0x48 -> LATIN CAPITAL LETTER H
    u'\u0049'  # 0x49 -> LATIN CAPITAL LETTER I
    u'\u004A'  # 0x4a -> LATIN CAPITAL LETTER J
    u'\u004B'  # 0x4b -> LATIN CAPITAL LETTER K
    u'\u004C'  # 0x4c -> LATIN CAPITAL LETTER L
    u'\u004D'  # 0x4d -> LATIN CAPITAL LETTER M
    u'\u004E'  # 0x4e -> LATIN CAPITAL LETTER N
    u'\u004F'  # 0x4f -> LATIN CAPITAL LETTER O
    u'\u0050'  # 0x50 -> LATIN CAPITAL LETTER P
    u'\u0051'  # 0x51 -> LATIN CAPITAL LETTER Q
    u'\u0052'  # 0x52 -> LATIN CAPITAL LETTER R
    u'\u0053'  # 0x53 -> LATIN CAPITAL LETTER S
    u'\u0054'  # 0x54 -> LATIN CAPITAL LETTER T
    u'\u0055'  # 0x55 -> LATIN CAPITAL LETTER U
    u'\u0056'  # 0x56 -> LATIN CAPITAL LETTER V
    u'\u0057'  # 0x57 -> LATIN CAPITAL LETTER W
    u'\u0058'  # 0x58 -> LATIN CAPITAL LETTER X
    u'\u0059'  # 0x59 -> LATIN CAPITAL LETTER Y
    u'\u005A'  # 0x5a -> LATIN CAPITAL LETTER Z
    u'\u005B'  # 0x5b -> LEFT SQUARE BRACKET
    u'\u005C'  # 0x5c -> REVERSE SOLIDUS
    u'\u005D'  # 0x5d -> RIGHT SQUARE BRACKET
    u'\u005E'  # 0x5e -> CIRCUMFLEX ACCENT
    u'\u005F'  # 0x5f -> LOW LINE
    u'\u0060'  # 0x60 -> GRAVE ACCENT
    u'\u0061'  # 0x61 -> LATIN SMALL LETTER A
    u'\u0062'  # 0x62 -> LATIN SMALL LETTER B
    u'\u0063'  # 0x63 -> LATIN SMALL LETTER C
    u'\u0064'  # 0x64 -> LATIN SMALL LETTER D
    u'\u0065'  # 0x65 -> LATIN SMALL LETTER E
    u'\u0066'  # 0x66 -> LATIN SMALL LETTER F
    u'\u0067'  # 0x67 -> LATIN SMALL LETTER G
    u'\u0068'  # 0x68 -> LATIN SMALL LETTER H
    u'\u0069'  # 0x69 -> LATIN SMALL LETTER I
    u'\u006A'  # 0x6a -> LATIN SMALL LETTER J
    u'\u006B'  # 0x6b -> LATIN SMALL LETTER K
    u'\u006C'  # 0x6c -> LATIN SMALL LETTER L
    u'\u006D'  # 0x6d -> LATIN SMALL LETTER M
    u'\u006E'  # 0x6e -> LATIN SMALL LETTER N
    u'\u006F'  # 0x6f -> LATIN SMALL LETTER O
    u'\u0070'  # 0x70 -> LATIN SMALL LETTER P
    u'\u0071'  # 0x71 -> LATIN SMALL LETTER Q
    u'\u0072'  # 0x72 -> LATIN SMALL LETTER R
    u'\u0073'  # 0x73 -> LATIN SMALL LETTER S
    u'\u0074'  # 0x74 -> LATIN SMALL LETTER T
    u'\u0075'  # 0x75 -> LATIN SMALL LETTER U
    u'\u0076'  # 0x76 -> LATIN SMALL LETTER V
    u'\u0077'  # 0x77 -> LATIN SMALL LETTER W
    u'\u0078'  # 0x78 -> LATIN SMALL LETTER X
    u'\u0079'  # 0x79 -> LATIN SMALL LETTER Y
    u'\u007A'  # 0x7a -> LATIN SMALL LETTER Z
    u'\u007B'  # 0x7b -> LEFT CURLY BRACKET
    u'\u007C'  # 0x7c -> VERTICAL LINE
    u'\u007D'  # 0x7d -> RIGHT CURLY BRACKET
    u'\u007E'  # 0x7e -> TILDE
    u'\u007F'  # 0x7f -> DELETE
    u'\u20AC'  # 0x80 -> EURO SIGN
    u'\ufffe'  # 0x81 -> UNDEFINED
    u'\u010C'  # 0x82 -> LATIN CAPITAL LETTER C WITH CARON
    u'\u0192'  # 0x83 -> LATIN SMALL LETTER F WITH HOOK
    u'\u010D'  # 0x84 -> LATIN SMALL LETTER C WITH CARON
    u'\u01B7'  # 0x85 -> LATIN CAPITAL LETTER EZH
    u'\u0292'  # 0x86 -> LATIN SMALL LETTER EZH
    u'\u01EE'  # 0x87 -> LATIN CAPITAL LETTER EZH WITH CARON
    u'\u01EF'  # 0x88 -> LATIN SMALL LETTER EZH WITH CARON
    u'\u0110'  # 0x89 -> LATIN CAPITAL LETTER D WITH STROKE
    u'\u0160'  # 0x8a -> LATIN CAPITAL LETTER S WITH CARON
    u'\u2039'  # 0x8b -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    u'\u0152'  # 0x8c -> LATIN CAPITAL LIGATURE OE
    u'\ufffe'  # 0x8D -> UNDEFINED
    u'\u017d'  # 0x8E -> LATIN CAPITAL LETTER Z WITH CARON
    u'\ufffe'  # 0x8F -> UNDEFINED
    u'\ufffe'  # 0x90 -> UNDEFINED
    u'\u2018'  # 0x91 -> LEFT SINGLE QUOTATION MARK
    u'\u2019'  # 0x92 -> RIGHT SINGLE QUOTATION MARK
    u'\u201C'  # 0x93 -> LEFT DOUBLE QUOTATION MARK
    u'\u201D'  # 0x94 -> RIGHT DOUBLE QUOTATION MARK
    u'\u2022'  # 0x95 -> BULLET
    u'\u2013'  # 0x96 -> EN DASH
    u'\u2014'  # 0x97 -> EM DASH
    u'\u0111'  # 0x98 -> LATIN SMALL LETTER D WITH STROKE
    u'\u01E6'  # 0x99 -> LATIN CAPITAL LETTER G WITH CARON
    u'\u0161'  # 0x9a -> LATIN SMALL LETTER S WITH CARON
    u'\u203A'  # 0x9b -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    u'\u0153'  # 0x9c -> LATIN SMALL LIGATURE OE
    u'\ufffe'  # 0x9D -> UNDEFINED
    u'\u017e'  # 0x9E -> LATIN SMALL LETTER Z WITH CARON
    u'\u0178'  # 0x9f -> LATIN CAPITAL LETTER Y WITH DIAERESIS
    u'\u00A0'  # 0xa0 -> NO-BREAK SPACE
    u'\u01E7'  # 0xa1 -> LATIN SMALL LETTER G WITH CARON
    u'\u01E4'  # 0xa2 -> LATIN CAPITAL LETTER G WITH STROKE
    u'\u00A3'  # 0xa3 -> POUND SIGN
    u'\u00A4'  # 0xa4 -> CURRENCY SIGN
    u'\u01E5'  # 0xa5 -> LATIN SMALL LETTER G WITH STROKE
    u'\u00A6'  # 0xa6 -> BROKEN BAR
    u'\u00A7'  # 0xa7 -> SECTION SIGN
    u'\u00A8'  # 0xa8 -> DIAERESIS
    u'\u00A9'  # 0xa9 -> COPYRIGHT SIGN
    u'\u021E'  # 0xaa -> LATIN CAPITAL LETTER H WITH CARON
    u'\u00AB'  # 0xab -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\u00AC'  # 0xac -> NOT SIGN
    u'\u00AD'  # 0xad -> SOFT HYPHEN
    u'\u00AE'  # 0xae -> REGISTERED SIGN
    u'\u021F'  # 0xaf -> LATIN SMALL LETTER H WITH CARON
    u'\u00B0'  # 0xb0 -> DEGREE SIGN
    u'\u00B1'  # 0xb1 -> PLUS-MINUS SIGN
    u'\u01E8'  # 0xb2 -> LATIN CAPITAL LETTER K WITH CARON
    u'\u01E9'  # 0xb3 -> LATIN SMALL LETTER K WITH CARON
    u'\u00B4'  # 0xb4 -> ACUTE ACCENT
    u'\u00B5'  # 0xb5 -> MICRO SIGN
    u'\u00B6'  # 0xb6 -> PILCROW SIGN
    u'\u00B7'  # 0xb7 -> MIDDLE DOT
    u'\u014A'  # 0xb8 -> LATIN CAPITAL LETTER ENG
    u'\u014B'  # 0xb9 -> LATIN SMALL LETTER ENG
    u'\u0166'  # 0xba -> LATIN CAPITAL LETTER T WITH STROKE
    u'\u00BB'  # 0xbb -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\u0167'  # 0xbc -> LATIN SMALL LETTER T WITH STROKE
    u'\u00BD'  # 0xbd -> VULGAR FRACTION ONE HALF
    u'\u017D'  # 0xbe -> LATIN CAPITAL LETTER Z WITH CARON
    u'\u017E'  # 0xbf -> LATIN SMALL LETTER Z WITH CARON
    u'\u00C0'  # 0xc0 -> LATIN CAPITAL LETTER A WITH GRAVE
    u'\u00C1'  # 0xc1 -> LATIN CAPITAL LETTER A WITH ACUTE
    u'\u00C2'  # 0xc2 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    u'\u00C3'  # 0xc3 -> LATIN CAPITAL LETTER A WITH TILDE
    u'\u00C4'  # 0xc4 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    u'\u00C5'  # 0xc5 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    u'\u00C6'  # 0xc6 -> LATIN CAPITAL LETTER AE
    u'\u00C7'  # 0xc7 -> LATIN CAPITAL LETTER C WITH CEDILLA
    u'\u00C8'  # 0xc8 -> LATIN CAPITAL LETTER E WITH GRAVE
    u'\u00C9'  # 0xc9 -> LATIN CAPITAL LETTER E WITH ACUTE
    u'\u00CA'  # 0xca -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    u'\u00CB'  # 0xcb -> LATIN CAPITAL LETTER E WITH DIAERESIS
    u'\u00CC'  # 0xcc -> LATIN CAPITAL LETTER I WITH GRAVE
    u'\u00CD'  # 0xcd -> LATIN CAPITAL LETTER I WITH ACUTE
    u'\u00CE'  # 0xce -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    u'\u00CF'  # 0xcf -> LATIN CAPITAL LETTER I WITH DIAERESIS
    u'\u00D0'  # 0xd0 -> LATIN CAPITAL LETTER ETH
    u'\u00D1'  # 0xd1 -> LATIN CAPITAL LETTER N WITH TILDE
    u'\u00D2'  # 0xd2 -> LATIN CAPITAL LETTER O WITH GRAVE
    u'\u00D3'  # 0xd3 -> LATIN CAPITAL LETTER O WITH ACUTE
    u'\u00D4'  # 0xd4 -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    u'\u00D5'  # 0xd5 -> LATIN CAPITAL LETTER O WITH TILDE
    u'\u00D6'  # 0xd6 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    u'\u00D7'  # 0xd7 -> MULTIPLICATION SIGN
    u'\u00D8'  # 0xd8 -> LATIN CAPITAL LETTER O WITH STROKE
    u'\u00D9'  # 0xd9 -> LATIN CAPITAL LETTER U WITH GRAVE
    u'\u00DA'  # 0xda -> LATIN CAPITAL LETTER U WITH ACUTE
    u'\u00DB'  # 0xdb -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    u'\u00DC'  # 0xdc -> LATIN CAPITAL LETTER U WITH DIAERESIS
    u'\u00DD'  # 0xdd -> LATIN CAPITAL LETTER Y WITH ACUTE
    u'\u00DE'  # 0xde -> LATIN CAPITAL LETTER THORN
    u'\u00DF'  # 0xdf -> LATIN SMALL LETTER SHARP S
    u'\u00E0'  # 0xe0 -> LATIN SMALL LETTER A WITH GRAVE
    u'\u00E1'  # 0xe1 -> LATIN SMALL LETTER A WITH ACUTE
    u'\u00E2'  # 0xe2 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    u'\u00E3'  # 0xe3 -> LATIN SMALL LETTER A WITH TILDE
    u'\u00E4'  # 0xe4 -> LATIN SMALL LETTER A WITH DIAERESIS
    u'\u00E5'  # 0xe5 -> LATIN SMALL LETTER A WITH RING ABOVE
    u'\u00E6'  # 0xe6 -> LATIN SMALL LETTER AE
    u'\u00E7'  # 0xe7 -> LATIN SMALL LETTER C WITH CEDILLA
    u'\u00E8'  # 0xe8 -> LATIN SMALL LETTER E WITH GRAVE
    u'\u00E9'  # 0xe9 -> LATIN SMALL LETTER E WITH ACUTE
    u'\u00EA'  # 0xea -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    u'\u00EB'  # 0xeb -> LATIN SMALL LETTER E WITH DIAERESIS
    u'\u00EC'  # 0xec -> LATIN SMALL LETTER I WITH GRAVE
    u'\u00ED'  # 0xed -> LATIN SMALL LETTER I WITH ACUTE
    u'\u00EE'  # 0xee -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    u'\u00EF'  # 0xef -> LATIN SMALL LETTER I WITH DIAERESIS
    u'\u00F0'  # 0xf0 -> LATIN SMALL LETTER ETH
    u'\u00F1'  # 0xf1 -> LATIN SMALL LETTER N WITH TILDE
    u'\u00F2'  # 0xf2 -> LATIN SMALL LETTER O WITH GRAVE
    u'\u00F3'  # 0xf3 -> LATIN SMALL LETTER O WITH ACUTE
    u'\u00F4'  # 0xf4 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    u'\u00F5'  # 0xf5 -> LATIN SMALL LETTER O WITH TILDE
    u'\u00F6'  # 0xf6 -> LATIN SMALL LETTER O WITH DIAERESIS
    u'\u00F7'  # 0xf7 -> DIVISION SIGN
    u'\u00F8'  # 0xf8 -> LATIN SMALL LETTER O WITH STROKE
    u'\u00F9'  # 0xf9 -> LATIN SMALL LETTER U WITH GRAVE
    u'\u00FA'  # 0xfa -> LATIN SMALL LETTER U WITH ACUTE
    u'\u00FB'  # 0xfb -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    u'\u00FC'  # 0xfc -> LATIN SMALL LETTER U WITH DIAERESIS
    u'\u00FD'  # 0xfd -> LATIN SMALL LETTER Y WITH ACUTE
    u'\u00FE'  # 0xfe -> LATIN SMALL LETTER THORN
    u'\u00FF'  # 0xff -> LATIN SMALL LETTER Y WITH DIAERESIS)
)

#  Encoding table
encoding_table = codecs.charmap_build(decoding_table)


def lookup(encoding):
    """Lookup the name of the encoding.

    Args:
        encoding (str): name of the encoding

    Returns:
        Codecs.CodecInfo if encoding is the name of the encoding of
            this file, None otherwise.
    """
    if encoding == 'ws2':
        return getregentry()
    return None


codecs.register(lookup)
