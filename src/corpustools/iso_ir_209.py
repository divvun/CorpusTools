# Disable pylint warnings to follow the coding style of the python
# this class.
# pylint: disable=W0232, C0103
"""Python Character Mapping Codec for iso-ir-209."""

import codecs

# Codec APIs


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
            (tuple[bytes, int]): a tuple of output object and length consumed
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
            (tuple[bytes, int]): a tuple of output object and length consumed
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
            (tuple[bytes, int]): a tuple of output object and length consumed
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
            (tuple[bytes, int]): a tuple of output object and length consumed
        """
        return codecs.charmap_decode(instring, self.errors, decoding_table)[0]


# encodings module API


def getregentry():
    """Get the info for this encoding."""
    return codecs.CodecInfo(
        name="ir209",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=codecs.StreamReader,
        streamwriter=codecs.StreamWriter,
    )


# Decoding Table

decoding_table = (
    "\u0000"  # 0x00 -> NULL (NUL)
    "\u0001"  # 0x01 -> START OF HEADING (SOH)
    "\u0002"  # 0x02 -> START OF TEXT (STX)
    "\u0003"  # 0x03 -> END OF TEXT (ETX)
    "\u0004"  # 0x04 -> END OF TRANSMISSION (EOT)
    "\u0005"  # 0x05 -> ENQUIRY (ENQ)
    "\u0006"  # 0x06 -> ACKNOWLEDGE (ACK)
    "\u0007"  # 0x07 -> BELL (BEL)
    "\u0008"  # 0x08 -> BACKSPACE (BS)
    "\u0009"  # 0x09 -> CHARACTER TABULATION (HT)
    "\u000A"  # 0x0a -> LINE FEED (LF)
    "\u000B"  # 0x0b -> LINE TABULATION (VT)
    "\u000C"  # 0x0c -> FORM FEED (FF)
    "\u000D"  # 0x0d -> CARRIAGE RETURN (CR)
    "\u000E"  # 0x0e -> SHIFT OUT (SO)
    "\u000F"  # 0x0f -> SHIFT IN (SI)
    "\u0010"  # 0x10 -> DATALINK ESCAPE (DLE)
    "\u0011"  # 0x11 -> DEVICE CONTROL ONE (DC1)
    "\u0012"  # 0x12 -> DEVICE CONTROL TWO (DC2)
    "\u0013"  # 0x13 -> DEVICE CONTROL THREE (DC3)
    "\u0014"  # 0x14 -> DEVICE CONTROL FOUR (DC4)
    "\u0015"  # 0x15 -> NEGATIVE ACKNOWLEDGE (NAK)
    "\u0016"  # 0x16 -> SYNCHRONOUS IDLE (SYN)
    "\u0017"  # 0x17 -> END OF TRANSMISSION BLOCK (ETB)
    "\u0018"  # 0x18 -> CANCEL (CAN)
    "\u0019"  # 0x19 -> END OF MEDIUM (EM)
    "\u001A"  # 0x1a -> SUBSTITUTE (SUB)
    "\u001B"  # 0x1b -> ESCAPE (ESC)
    "\u001C"  # 0x1c -> FILE SEPARATOR (IS4)
    "\u001D"  # 0x1d -> GROUP SEPARATOR (IS3)
    "\u001E"  # 0x1e -> RECORD SEPARATOR (IS2)
    "\u001F"  # 0x1f -> UNIT SEPARATOR (IS1)
    "\u0020"  # 0x20 -> SPACE
    "\u0021"  # 0x21 -> EXCLAMATION MARK
    "\u0022"  # 0x22 -> QUOTATION MARK
    "\u0023"  # 0x23 -> NUMBER SIGN
    "\u0024"  # 0x24 -> DOLLAR SIGN
    "\u0025"  # 0x25 -> PERCENT SIGN
    "\u0026"  # 0x26 -> AMPERSAND
    "\u0027"  # 0x27 -> APOSTROPHE
    "\u0028"  # 0x28 -> LEFT PARENTHESIS
    "\u0029"  # 0x29 -> RIGHT PARENTHESIS
    "\u002A"  # 0x2a -> ASTERISK
    "\u002B"  # 0x2b -> PLUS SIGN
    "\u002C"  # 0x2c -> COMMA
    "\u002D"  # 0x2d -> HYPHEN-MINUS
    "\u002E"  # 0x2e -> FULL STOP
    "\u002F"  # 0x2f -> SOLIDUS
    "\u0030"  # 0x30 -> DIGIT ZERO
    "\u0031"  # 0x31 -> DIGIT ONE
    "\u0032"  # 0x32 -> DIGIT TWO
    "\u0033"  # 0x33 -> DIGIT THREE
    "\u0034"  # 0x34 -> DIGIT FOUR
    "\u0035"  # 0x35 -> DIGIT FIVE
    "\u0036"  # 0x36 -> DIGIT SIX
    "\u0037"  # 0x37 -> DIGIT SEVEN
    "\u0038"  # 0x38 -> DIGIT EIGHT
    "\u0039"  # 0x39 -> DIGIT NINE
    "\u003A"  # 0x3a -> COLON
    "\u003B"  # 0x3b -> SEMICOLON
    "\u003C"  # 0x3c -> LESS-THAN SIGN
    "\u003D"  # 0x3d -> EQUALS SIGN
    "\u003E"  # 0x3e -> GREATER-THAN SIGN
    "\u003F"  # 0x3f -> QUESTION MARK
    "\u0040"  # 0x40 -> COMMERCIAL AT
    "\u0041"  # 0x41 -> LATIN CAPITAL LETTER A
    "\u0042"  # 0x42 -> LATIN CAPITAL LETTER B
    "\u0043"  # 0x43 -> LATIN CAPITAL LETTER C
    "\u0044"  # 0x44 -> LATIN CAPITAL LETTER D
    "\u0045"  # 0x45 -> LATIN CAPITAL LETTER E
    "\u0046"  # 0x46 -> LATIN CAPITAL LETTER F
    "\u0047"  # 0x47 -> LATIN CAPITAL LETTER G
    "\u0048"  # 0x48 -> LATIN CAPITAL LETTER H
    "\u0049"  # 0x49 -> LATIN CAPITAL LETTER I
    "\u004A"  # 0x4a -> LATIN CAPITAL LETTER J
    "\u004B"  # 0x4b -> LATIN CAPITAL LETTER K
    "\u004C"  # 0x4c -> LATIN CAPITAL LETTER L
    "\u004D"  # 0x4d -> LATIN CAPITAL LETTER M
    "\u004E"  # 0x4e -> LATIN CAPITAL LETTER N
    "\u004F"  # 0x4f -> LATIN CAPITAL LETTER O
    "\u0050"  # 0x50 -> LATIN CAPITAL LETTER P
    "\u0051"  # 0x51 -> LATIN CAPITAL LETTER Q
    "\u0052"  # 0x52 -> LATIN CAPITAL LETTER R
    "\u0053"  # 0x53 -> LATIN CAPITAL LETTER S
    "\u0054"  # 0x54 -> LATIN CAPITAL LETTER T
    "\u0055"  # 0x55 -> LATIN CAPITAL LETTER U
    "\u0056"  # 0x56 -> LATIN CAPITAL LETTER V
    "\u0057"  # 0x57 -> LATIN CAPITAL LETTER W
    "\u0058"  # 0x58 -> LATIN CAPITAL LETTER X
    "\u0059"  # 0x59 -> LATIN CAPITAL LETTER Y
    "\u005A"  # 0x5a -> LATIN CAPITAL LETTER Z
    "\u005B"  # 0x5b -> LEFT SQUARE BRACKET
    "\u005C"  # 0x5c -> REVERSE SOLIDUS
    "\u005D"  # 0x5d -> RIGHT SQUARE BRACKET
    "\u005E"  # 0x5e -> CIRCUMFLEX ACCENT
    "\u005F"  # 0x5f -> LOW LINE
    "\u0060"  # 0x60 -> GRAVE ACCENT
    "\u0061"  # 0x61 -> LATIN SMALL LETTER A
    "\u0062"  # 0x62 -> LATIN SMALL LETTER B
    "\u0063"  # 0x63 -> LATIN SMALL LETTER C
    "\u0064"  # 0x64 -> LATIN SMALL LETTER D
    "\u0065"  # 0x65 -> LATIN SMALL LETTER E
    "\u0066"  # 0x66 -> LATIN SMALL LETTER F
    "\u0067"  # 0x67 -> LATIN SMALL LETTER G
    "\u0068"  # 0x68 -> LATIN SMALL LETTER H
    "\u0069"  # 0x69 -> LATIN SMALL LETTER I
    "\u006A"  # 0x6a -> LATIN SMALL LETTER J
    "\u006B"  # 0x6b -> LATIN SMALL LETTER K
    "\u006C"  # 0x6c -> LATIN SMALL LETTER L
    "\u006D"  # 0x6d -> LATIN SMALL LETTER M
    "\u006E"  # 0x6e -> LATIN SMALL LETTER N
    "\u006F"  # 0x6f -> LATIN SMALL LETTER O
    "\u0070"  # 0x70 -> LATIN SMALL LETTER P
    "\u0071"  # 0x71 -> LATIN SMALL LETTER Q
    "\u0072"  # 0x72 -> LATIN SMALL LETTER R
    "\u0073"  # 0x73 -> LATIN SMALL LETTER S
    "\u0074"  # 0x74 -> LATIN SMALL LETTER T
    "\u0075"  # 0x75 -> LATIN SMALL LETTER U
    "\u0076"  # 0x76 -> LATIN SMALL LETTER V
    "\u0077"  # 0x77 -> LATIN SMALL LETTER W
    "\u0078"  # 0x78 -> LATIN SMALL LETTER X
    "\u0079"  # 0x79 -> LATIN SMALL LETTER Y
    "\u007A"  # 0x7a -> LATIN SMALL LETTER Z
    "\u007B"  # 0x7b -> LEFT CURLY BRACKET
    "\u007C"  # 0x7c -> VERTICAL LINE
    "\u007D"  # 0x7d -> RIGHT CURLY BRACKET
    "\u007E"  # 0x7e -> TILDE
    "\u007F"  # 0x7f -> DELETE (DEL)
    "\u20AC"  # 0x80 -> EURO SIGN
    "\ufffe"  # 0x81 -> UNDEFINED
    "\u201A"  # 0x82 -> SINGLE LOW-9 QUOTATION MARK
    "\u0192"  # 0x83 -> LATIN SMALL LETTER F WITH HOOK
    "\u201E"  # 0x84 -> DOUBLE LOW-9 QUOTATION MARK
    "\u2026"  # 0x85 -> HORIZONTAL ELLIPSIS
    "\u00AC"  # 0x86 -> NOT SIGN
    "\u2260"  # 0x87 -> NOT EQUAL TO
    "\u00A3"  # 0x88 -> POUND SIGN
    "\u2030"  # 0x89 -> PER MILLE SIGN
    "\u00BF"  # 0x8a -> INVERTED QUESTION MARK
    "\u2264"  # 0x8b -> LESS-THAN OR EQUAL TO
    "\u0152"  # 0x8c -> LATIN CAPITAL LIGATURE OE
    "\ufffe"  # 0x8D -> UNDEFINED
    "\u017d"  # 0x8E -> LATIN CAPITAL LETTER Z WITH CARON
    "\ufffe"  # 0x8F -> UNDEFINED
    "\ufffe"  # 0x90 -> UNDEFINED
    "\u2018"  # 0x91 -> LEFT SINGLE QUOTATION MARK
    "\u2019"  # 0x92 -> RIGHT SINGLE QUOTATION MARK
    "\u201C"  # 0x93 -> LEFT DOUBLE QUOTATION MARK
    "\u201D"  # 0x94 -> RIGHT DOUBLE QUOTATION MARK
    "\u2022"  # 0x95 -> BULLET
    "\u2013"  # 0x96 -> EN DASH
    "\u2014"  # 0x97 -> EM DASH
    "\u00AE"  # 0x98 -> REGISTERED SIGN
    "\u2122"  # 0x99 -> TRADE MARK SIGN
    "\u00A1"  # 0x9a -> INVERTED EXCLAMATION MARK
    "\u2265"  # 0x9b -> GREATER-THAN OR EQUAL TO
    "\u0153"  # 0x9c -> LATIN SMALL LIGATURE OE
    "\ufffe"  # 0x9D -> UNDEFINED
    "\u017e"  # 0x9E -> LATIN SMALL LETTER Z WITH CARON
    "\u0178"  # 0x9f -> LATIN CAPITAL LETTER Y WITH DIAERESIS
    "\u00A0"  # 0xa0 -> NO-BREAK SPACE
    "\u010C"  # 0xa1 -> LATIN CAPITAL LETTER C WITH CARON
    "\u010D"  # 0xa2 -> LATIN SMALL LETTER C WITH CARON
    "\u0110"  # 0xa3 -> LATIN CAPITAL LETTER D WITH STROKE
    "\u0111"  # 0xa4 -> LATIN SMALL LETTER D WITH STROKE
    "\u01E4"  # 0xa5 -> LATIN CAPITAL LETTER G WITH STROKE
    "\u01E5"  # 0xa6 -> LATIN SMALL LETTER G WITH STROKE
    "\u00A7"  # 0xa7 -> SECTION SIGN
    "\u01E6"  # 0xa8 -> LATIN CAPITAL LETTER G WITH CARON
    "\u00A9"  # 0xa9 -> COPYRIGHT SIGN
    "\u01E7"  # 0xaa -> LATIN SMALL LETTER G WITH CARON
    "\u021E"  # 0xab -> LATIN CAPITAL LETTER H WITH CARON
    "\u01E8"  # 0xac -> LATIN CAPITAL LETTER K WITH CARON
    "\u00AD"  # 0xad -> SOFT HYPHEN
    "\u01E9"  # 0xae -> LATIN SMALL LETTER K WITH CARON
    "\u014A"  # 0xaf -> LATIN CAPITAL LETTER ENG (Sami)
    "\u00B0"  # 0xb0 -> DEGREE SIGN
    "\u014B"  # 0xb1 -> LATIN SMALL LETTER ENG (Sami)
    "\u0160"  # 0xb2 -> LATIN CAPITAL LETTER S WITH CARON
    "\u0161"  # 0xb3 -> LATIN SMALL LETTER S WITH CARON
    "\u00B4"  # 0xb4 -> ACUTE ACCENT
    "\u0166"  # 0xb5 -> LATIN CAPITAL LETTER T WITH STROKE
    "\u00B6"  # 0xb6 -> PILCROW SIGN
    "\u00B7"  # 0xb7 -> MIDDLE DOT
    "\u0167"  # 0xb8 -> LATIN SMALL LETTER T WITH STROKE
    "\u017D"  # 0xb9 -> LATIN CAPITAL LETTER Z WITH CARON
    "\u017E"  # 0xba -> LATIN SMALL LETTER Z WITH CARON
    "\u021F"  # 0xbb -> LATIN SMALL LETTER H WITH CARON
    "\u01B7"  # 0xbc -> LATIN CAPITAL LETTER EZH
    "\u0292"  # 0xbd -> LATIN SMALL LETTER EZH
    "\u01EE"  # 0xbe -> LATIN CAPITAL LETTER EZH WITH CARON
    "\u01EF"  # 0xbf -> LATIN SMALL LETTER EZH WITH CARON
    "\u00C0"  # 0xc0 -> LATIN CAPITAL LETTER A WITH GRAVE
    "\u00C1"  # 0xc1 -> LATIN CAPITAL LETTER A WITH ACUTE
    "\u00C2"  # 0xc2 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    "\u00C3"  # 0xc3 -> LATIN CAPITAL LETTER A WITH TILDE
    "\u00C4"  # 0xc4 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    "\u00C5"  # 0xc5 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    "\u00C6"  # 0xc6 -> LATIN CAPITAL LETTER AE
    "\u00C7"  # 0xc7 -> LATIN CAPITAL LETTER C WITH CEDILLA
    "\u00C8"  # 0xc8 -> LATIN CAPITAL LETTER E WITH GRAVE
    "\u00C9"  # 0xc9 -> LATIN CAPITAL LETTER E WITH ACUTE
    "\u00CA"  # 0xca -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    "\u00CB"  # 0xcb -> LATIN CAPITAL LETTER E WITH DIAERESIS
    "\u00CC"  # 0xcc -> LATIN CAPITAL LETTER I WITH GRAVE
    "\u00CD"  # 0xcd -> LATIN CAPITAL LETTER I WITH ACUTE
    "\u00CE"  # 0xce -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    "\u00CF"  # 0xcf -> LATIN CAPITAL LETTER I WITH DIAERESIS
    "\u00D0"  # 0xd0 -> LATIN CAPITAL LETTER ETH (Icelandic)
    "\u00D1"  # 0xd1 -> LATIN CAPITAL LETTER N WITH TILDE
    "\u00D2"  # 0xd2 -> LATIN CAPITAL LETTER O WITH GRAVE
    "\u00D3"  # 0xd3 -> LATIN CAPITAL LETTER O WITH ACUTE
    "\u00D4"  # 0xd4 -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    "\u00D5"  # 0xd5 -> LATIN CAPITAL LETTER O WITH TILDE
    "\u00D6"  # 0xd6 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    "\u00D7"  # 0xd7 -> MULTIPLICATION SIGN
    "\u00D8"  # 0xd8 -> LATIN CAPITAL LETTER O WITH STROKE
    "\u00D9"  # 0xd9 -> LATIN CAPITAL LETTER U WITH GRAVE
    "\u00DA"  # 0xda -> LATIN CAPITAL LETTER U WITH ACUTE
    "\u00DB"  # 0xdb -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    "\u00DC"  # 0xdc -> LATIN CAPITAL LETTER U WITH DIAERESIS
    "\u00DD"  # 0xdd -> LATIN CAPITAL LETTER Y WITH ACUTE
    "\u00DE"  # 0xde -> LATIN CAPITAL LETTER THORN (Icelandic)
    "\u00DF"  # 0xdf -> LATIN SMALL LETTER SHARP S (German)
    "\u00E0"  # 0xe0 -> LATIN SMALL LETTER A WITH GRAVE
    "\u00E1"  # 0xe1 -> LATIN SMALL LETTER A WITH ACUTE
    "\u00E2"  # 0xe2 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    "\u00E3"  # 0xe3 -> LATIN SMALL LETTER A WITH TILDE
    "\u00E4"  # 0xe4 -> LATIN SMALL LETTER A WITH DIAERESIS
    "\u00E5"  # 0xe5 -> LATIN SMALL LETTER A WITH RING ABOVE
    "\u00E6"  # 0xe6 -> LATIN SMALL LETTER AE
    "\u00E7"  # 0xe7 -> LATIN SMALL LETTER C WITH CEDILLA
    "\u00E8"  # 0xe8 -> LATIN SMALL LETTER E WITH GRAVE
    "\u00E9"  # 0xe9 -> LATIN SMALL LETTER E WITH ACUTE
    "\u00EA"  # 0xea -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    "\u00EB"  # 0xeb -> LATIN SMALL LETTER E WITH DIAERESIS
    "\u00EC"  # 0xec -> LATIN SMALL LETTER I WITH GRAVE
    "\u00ED"  # 0xed -> LATIN SMALL LETTER I WITH ACUTE
    "\u00EE"  # 0xee -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    "\u00EF"  # 0xef -> LATIN SMALL LETTER I WITH DIAERESIS
    "\u00F0"  # 0xf0 -> LATIN SMALL LETTER ETH (Icelandic)
    "\u00F1"  # 0xf1 -> LATIN SMALL LETTER N WITH TILDE
    "\u00F2"  # 0xf2 -> LATIN SMALL LETTER O WITH GRAVE
    "\u00F3"  # 0xf3 -> LATIN SMALL LETTER O WITH ACUTE
    "\u00F4"  # 0xf4 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    "\u00F5"  # 0xf5 -> LATIN SMALL LETTER O WITH TILDE
    "\u00F6"  # 0xf6 -> LATIN SMALL LETTER O WITH DIAERESIS
    "\u00F7"  # 0xf7 -> DIVISION SIGN
    "\u00F8"  # 0xf8 -> LATIN SMALL LETTER O WITH STROKE
    "\u00F9"  # 0xf9 -> LATIN SMALL LETTER U WITH GRAVE
    "\u00FA"  # 0xfa -> LATIN SMALL LETTER U WITH ACUTE
    "\u00FB"  # 0xfb -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    "\u00FC"  # 0xfc -> LATIN SMALL LETTER U WITH DIAERESIS
    "\u00FD"  # 0xfd -> LATIN SMALL LETTER Y WITH ACUTE
    "\u00FE"  # 0xfe -> LATIN SMALL LETTER THORN (Icelandic)
    "\u00FF"  # 0xff -> LATIN SMALL LETTER Y WITH DIAERESIS
)

# Encoding table
encoding_table = codecs.charmap_build(decoding_table)


def lookup(encoding):
    """Lookup the name of the encoding.

    Args:
        encoding (str): name of the encoding

    Returns:
        (Codecs.CodecInfo|None): Codecs.CodecInfo if encoding is the name of
            the encoding of this file, None otherwise.
    """
    if encoding == "ir209":
        return getregentry()
    return None


codecs.register(lookup)
