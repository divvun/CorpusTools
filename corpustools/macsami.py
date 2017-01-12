"""Python Character Mapping Codec for macsami"""

import codecs

### Codec APIs

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,encoding_table)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,encoding_table)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,decoding_table)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

def getregentry():
    return codecs.CodecInfo(
        name='macsami',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


### Decoding Table

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
    u'\x09'     # 0x09 -> HORIZONTAL TABULATION
    u'\x0A'     # 0x0a -> LINE FEED
    u'\x0B'     # 0x0b -> VERTICAL TABULATION
    u'\x0C'     # 0x0c -> FORM FEED
    u'\x0D'     # 0x0d -> CARRIAGE RETURN
    u'\x0E'     # 0x0e -> SHIFT OUT
    u'\x0F'     # 0x0f -> SHIFT IN
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
    u'\x1A'     # 0x1a -> SUBSTITUTE
    u'\x1B'     # 0x1b -> ESCAPE
    u'\x1C'     # 0x1c -> FILE SEPARATOR
    u'\x1D'     # 0x1d -> GROUP SEPARATOR
    u'\x1E'     # 0x1e -> RECORD SEPARATOR
    u'\x1F'     # 0x1f -> UNIT SEPARATOR
    u'\x20'     # 0x20 -> SPACE
    u'\x21'     # 0x21 -> EXCLAMATION MARK
    u'\x22'     # 0x22 -> QUOTATION MARK
    u'\x23'     # 0x23 -> NUMBER SIGN
    u'\x24'     # 0x24 -> DOLLAR SIGN
    u'\x25'     # 0x25 -> PERCENT SIGN
    u'\x26'     # 0x26 -> AMPERSAND
    u'\x27'     # 0x27 -> APOSTROPHE
    u'\x28'     # 0x28 -> LEFT PARENTHESIS
    u'\x29'     # 0x29 -> RIGHT PARENTHESIS
    u'\x2A'     # 0x2a -> ASTERISK
    u'\x2B'     # 0x2b -> PLUS SIGN
    u'\x2C'     # 0x2c -> COMMA
    u'\x2D'     # 0x2d -> HYPHEN-MINUS
    u'\x2E'     # 0x2e -> FULL STOP
    u'\x2F'     # 0x2f -> SOLIDUS
    u'\x30'     # 0x30 -> DIGIT ZERO
    u'\x31'     # 0x31 -> DIGIT ONE
    u'\x32'     # 0x32 -> DIGIT TWO
    u'\x33'     # 0x33 -> DIGIT THREE
    u'\x34'     # 0x34 -> DIGIT FOUR
    u'\x35'     # 0x35 -> DIGIT FIVE
    u'\x36'     # 0x36 -> DIGIT SIX
    u'\x37'     # 0x37 -> DIGIT SEVEN
    u'\x38'     # 0x38 -> DIGIT EIGHT
    u'\x39'     # 0x39 -> DIGIT NINE
    u'\x3A'     # 0x3a -> COLON
    u'\x3B'     # 0x3b -> SEMICOLON
    u'\x3C'     # 0x3c -> LESS-THAN SIGN
    u'\x3D'     # 0x3d -> EQUALS SIGN
    u'\x3E'     # 0x3e -> GREATER-THAN SIGN
    u'\x3F'     # 0x3f -> QUESTION MARK
    u'\x40'     # 0x40 -> COMMERCIAL AT
    u'\x41'     # 0x41 -> LATIN CAPITAL LETTER A
    u'\x42'     # 0x42 -> LATIN CAPITAL LETTER B
    u'\x43'     # 0x43 -> LATIN CAPITAL LETTER C
    u'\x44'     # 0x44 -> LATIN CAPITAL LETTER D
    u'\x45'     # 0x45 -> LATIN CAPITAL LETTER E
    u'\x46'     # 0x46 -> LATIN CAPITAL LETTER F
    u'\x47'     # 0x47 -> LATIN CAPITAL LETTER G
    u'\x48'     # 0x48 -> LATIN CAPITAL LETTER H
    u'\x49'     # 0x49 -> LATIN CAPITAL LETTER I
    u'\x4A'     # 0x4a -> LATIN CAPITAL LETTER J
    u'\x4B'     # 0x4b -> LATIN CAPITAL LETTER K
    u'\x4C'     # 0x4c -> LATIN CAPITAL LETTER L
    u'\x4D'     # 0x4d -> LATIN CAPITAL LETTER M
    u'\x4E'     # 0x4e -> LATIN CAPITAL LETTER N
    u'\x4F'     # 0x4f -> LATIN CAPITAL LETTER O
    u'\x50'     # 0x50 -> LATIN CAPITAL LETTER P
    u'\x51'     # 0x51 -> LATIN CAPITAL LETTER Q
    u'\x52'     # 0x52 -> LATIN CAPITAL LETTER R
    u'\x53'     # 0x53 -> LATIN CAPITAL LETTER S
    u'\x54'     # 0x54 -> LATIN CAPITAL LETTER T
    u'\x55'     # 0x55 -> LATIN CAPITAL LETTER U
    u'\x56'     # 0x56 -> LATIN CAPITAL LETTER V
    u'\x57'     # 0x57 -> LATIN CAPITAL LETTER W
    u'\x58'     # 0x58 -> LATIN CAPITAL LETTER X
    u'\x59'     # 0x59 -> LATIN CAPITAL LETTER Y
    u'\x5A'     # 0x5a -> LATIN CAPITAL LETTER Z
    u'\x5B'     # 0x5b -> LEFT SQUARE BRACKET
    u'\x5C'     # 0x5c -> REVERSE SOLIDUS
    u'\x5D'     # 0x5d -> RIGHT SQUARE BRACKET
    u'\x5E'     # 0x5e -> CIRCUMFLEX ACCENT
    u'\x5F'     # 0x5f -> LOW LINE
    u'\x60'     # 0x60 -> GRAVE ACCENT
    u'\x61'     # 0x61 -> LATIN SMALL LETTER A
    u'\x62'     # 0x62 -> LATIN SMALL LETTER B
    u'\x63'     # 0x63 -> LATIN SMALL LETTER C
    u'\x64'     # 0x64 -> LATIN SMALL LETTER D
    u'\x65'     # 0x65 -> LATIN SMALL LETTER E
    u'\x66'     # 0x66 -> LATIN SMALL LETTER F
    u'\x67'     # 0x67 -> LATIN SMALL LETTER G
    u'\x68'     # 0x68 -> LATIN SMALL LETTER H
    u'\x69'     # 0x69 -> LATIN SMALL LETTER I
    u'\x6A'     # 0x6a -> LATIN SMALL LETTER J
    u'\x6B'     # 0x6b -> LATIN SMALL LETTER K
    u'\x6C'     # 0x6c -> LATIN SMALL LETTER L
    u'\x6D'     # 0x6d -> LATIN SMALL LETTER M
    u'\x6E'     # 0x6e -> LATIN SMALL LETTER N
    u'\x6F'     # 0x6f -> LATIN SMALL LETTER O
    u'\x70'     # 0x70 -> LATIN SMALL LETTER P
    u'\x71'     # 0x71 -> LATIN SMALL LETTER Q
    u'\x72'     # 0x72 -> LATIN SMALL LETTER R
    u'\x73'     # 0x73 -> LATIN SMALL LETTER S
    u'\x74'     # 0x74 -> LATIN SMALL LETTER T
    u'\x75'     # 0x75 -> LATIN SMALL LETTER U
    u'\x76'     # 0x76 -> LATIN SMALL LETTER V
    u'\x77'     # 0x77 -> LATIN SMALL LETTER W
    u'\x78'     # 0x78 -> LATIN SMALL LETTER X
    u'\x79'     # 0x79 -> LATIN SMALL LETTER Y
    u'\x7A'     # 0x7a -> LATIN SMALL LETTER Z
    u'\x7B'     # 0x7b -> LEFT CURLY BRACKET
    u'\x7C'     # 0x7c -> VERTICAL LINE
    u'\x7D'     # 0x7d -> RIGHT CURLY BRACKET
    u'\x7E'     # 0x7e -> TILDE
    u'\x7F'     # 0x7f -> DELETE
    u'\xC4'     # 0x80 -> LATIN CAPITAL LETTER A WITH DIAERESIS
    u'\xC5'     # 0x81 -> LATIN CAPITAL LETTER A WITH RING ABOVE
    u'\xC7'     # 0x82 -> LATIN CAPITAL LETTER C WITH CEDILLA
    u'\xC9'     # 0x83 -> LATIN CAPITAL LETTER E WITH ACUTE
    u'\xD1'     # 0x84 -> LATIN CAPITAL LETTER N WITH TILDE
    u'\xD6'     # 0x85 -> LATIN CAPITAL LETTER O WITH DIAERESIS
    u'\xDC'     # 0x86 -> LATIN CAPITAL LETTER U WITH DIAERESIS
    u'\xE1'     # 0x87 -> LATIN SMALL LETTER A WITH ACUTE
    u'\xE0'     # 0x88 -> LATIN SMALL LETTER A WITH GRAVE
    u'\xE2'     # 0x89 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
    u'\xE4'     # 0x8a -> LATIN SMALL LETTER A WITH DIAERESIS
    u'\xE3'     # 0x8b -> LATIN SMALL LETTER A WITH TILDE
    u'\xE5'     # 0x8c -> LATIN SMALL LETTER A WITH RING ABOVE
    u'\xE7'     # 0x8d -> LATIN SMALL LETTER C WITH CEDILLA
    u'\xE9'     # 0x8e -> LATIN SMALL LETTER E WITH ACUTE
    u'\xE8'     # 0x8f -> LATIN SMALL LETTER E WITH GRAVE
    u'\xEA'     # 0x90 -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    u'\xEB'     # 0x91 -> LATIN SMALL LETTER E WITH DIAERESIS
    u'\xED'     # 0x92 -> LATIN SMALL LETTER I WITH ACUTE
    u'\xEC'     # 0x93 -> LATIN SMALL LETTER I WITH GRAVE
    u'\xEE'     # 0x94 -> LATIN SMALL LETTER I WITH CIRCUMFLEX
    u'\xEF'     # 0x95 -> LATIN SMALL LETTER I WITH DIAERESIS
    u'\xF1'     # 0x96 -> LATIN SMALL LETTER N WITH TILDE
    u'\xF3'     # 0x97 -> LATIN SMALL LETTER O WITH ACUTE
    u'\xF2'     # 0x98 -> LATIN SMALL LETTER O WITH GRAVE
    u'\xF4'     # 0x99 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
    u'\xF6'     # 0x9a -> LATIN SMALL LETTER O WITH DIAERESIS
    u'\xF5'     # 0x9b -> LATIN SMALL LETTER O WITH TILDE
    u'\xFA'     # 0x9c -> LATIN SMALL LETTER U WITH ACUTE
    u'\xF9'     # 0x9d -> LATIN SMALL LETTER U WITH GRAVE
    u'\xFB'     # 0x9e -> LATIN SMALL LETTER U WITH CIRCUMFLEX
    u'\xFC'     # 0x9f -> LATIN SMALL LETTER U WITH DIAERESIS
    u'\xDD'     # 0xa0 -> LATIN CAPITAL LETTER Y WITH ACUTE
    u'\xB0'     # 0xa1 -> DEGREE SIGN
    u'\u010C'     # 0xa2 -> LATIN CAPITAL LETTER C WITH CARON
    u'\xA3'     # 0xa3 -> POUND SIGN
    u'\xA7'     # 0xa4 -> SECTION SIGN
    u'\u2022'     # 0xa5 -> BULLET
    u'\xB6'     # 0xa6 -> PILCROW SIGN
    u'\xDF'     # 0xa7 -> LATIN SMALL LETTER SHARP S (German)
    u'\xAE'     # 0xa8 -> REGISTERED SIGN
    u'\xA9'     # 0xa9 -> COPYRIGHT SIGN
    u'\u2122'     # 0xaa -> TRADE MARK SIGN
    u'\xB4'     # 0xab -> ACUTE ACCENT
    u'\xA8'     # 0xac -> DIAERESIS
    u'\u2260'     # 0xad -> NOT EQUAL TO
    u'\xC6'     # 0xae -> LATIN CAPITAL LETTER AE
    u'\xD8'     # 0xaf -> LATIN CAPITAL LETTER O WITH STROKE
    u'\u0110'     # 0xb0 -> LATIN CAPITAL LETTER D WITH STROKE
    u'\u014A'     # 0xb1 -> LATIN CAPITAL LETTER ENG
    u'\u021E'     # 0xb2 -> LATIN CAPITAL LETTER H WITH CARON
    u'\u021F'     # 0xb3 -> LATIN SMALL LETTER H WITH CARON
    u'\u0160'     # 0xb4 -> LATIN CAPITAL LETTER S WITH CARON
    u'\u0166'     # 0xb5 -> LATIN CAPITAL LETTER T WITH STROKE
    u'\u2202'     # 0xb6 -> PARTIAL DIFFERENTIAL
    u'\u017D'     # 0xb7 -> LATIN CAPITAL LETTER Z WITH CARON
    u'\u010D'     # 0xb8 -> LATIN SMALL LETTER C WITH CARON
    u'\u0111'     # 0xb9 -> LATIN SMALL LETTER D WITH STROKE
    u'\u014B'     # 0xba -> LATIN SMALL LETTER ENG
    u'\u0161'     # 0xbb -> LATIN SMALL LETTER S WITH CARON
    u'\u0167'     # 0xbc -> LATIN SMALL LETTER T WITH STROKE
    u'\u017E'     # 0xbd -> LATIN SMALL LETTER Z WITH CARON
    u'\xE6'     # 0xbe -> LATIN SMALL LETTER AE
    u'\xF8'     # 0xbf -> LATIN SMALL LETTER O WITH STROKE
    u'\xBF'     # 0xc0 -> INVERTED QUESTION MARK
    u'\xA1'     # 0xc1 -> INVERTED EXCLAMATION MARK
    u'\xAC'     # 0xc2 -> NOT SIGN
    u'\u221A'     # 0xc3 -> SQUARE ROOT
    u'\u0192'     # 0xc4 -> LATIN SMALL LETTER F WITH HOOK
    u'\u2248'     # 0xc5 -> ALMOST EQUAL TO
    u'\u2206'     # 0xc6 -> INCREMENT
    u'\xAB'     # 0xc7 -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\xBB'     # 0xc8 -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    u'\u2026'     # 0xc9 -> HORIZONTAL ELLIPSIS
    u'\xA0'     # 0xca -> NO-BREAK SPACE
    u'\xC0'     # 0xcb -> LATIN CAPITAL LETTER A WITH GRAVE
    u'\xC3'     # 0xcc -> LATIN CAPITAL LETTER A WITH TILDE
    u'\xD5'     # 0xcd -> LATIN CAPITAL LETTER O WITH TILDE
    u'\u0152'     # 0xce -> LATIN CAPITAL LIGATURE OE
    u'\u0153'     # 0xcf -> LATIN SMALL LIGATURE OE
    u'\u2013'     # 0xd0 -> EN DASH
    u'\u2014'     # 0xd1 -> EM DASH
    u'\u201C'     # 0xd2 -> LEFT DOUBLE QUOTATION MARK
    u'\u201D'     # 0xd3 -> RIGHT DOUBLE QUOTATION MARK
    u'\u2018'     # 0xd4 -> LEFT SINGLE QUOTATION MARK
    u'\u2019'     # 0xd5 -> RIGHT SINGLE QUOTATION MARK
    u'\xF7'     # 0xd6 -> DIVISION SIGN
    u'\u25CA'     # 0xd7 -> LOZENGE
    u'\xFF'     # 0xd8 -> LATIN SMALL LETTER Y WITH DIAERESIS
    u'\u0178'     # 0xd9 -> LATIN CAPITAL LETTER Y WITH DIAERESIS
    u'\u2044'     # 0xda -> FRACTION SLASH
    u'\xA4'     # 0xdb -> CURRENCY SIGN
    u'\xD0'     # 0xdc -> LATIN CAPITAL LETTER ETH
    u'\xF0'     # 0xdd -> LATIN SMALL LETTER ETH
    u'\xDE'     # 0xde -> LATIN CAPITAL LETTER THORN
    u'\xFE'     # 0xdf -> LATIN SMALL LETTER THORN
    u'\xFD'     # 0xe0 -> LATIN SMALL LETTER Y WITH ACUTE
    u'\xB7'     # 0xe1 -> MIDDLE DOT
    u'\u201A'     # 0xe2 -> SINGLE LOW-9 QUOTATION MARK
    u'\u201E'     # 0xe3 -> DOUBLE LOW-9 QUOTATION MARK
    u'\u2030'     # 0xe4 -> PER MILLE SIGN
    u'\xC2'     # 0xe5 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    u'\xCA'     # 0xe6 -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    u'\xC1'     # 0xe7 -> LATIN CAPITAL LETTER A WITH ACUTE
    u'\xCB'     # 0xe8 -> LATIN CAPITAL LETTER E WITH DIAERESIS
    u'\xC8'     # 0xe9 -> LATIN CAPITAL LETTER E WITH GRAVE
    u'\xCD'     # 0xea -> LATIN CAPITAL LETTER I WITH ACUTE
    u'\xCE'     # 0xeb -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    u'\xCF'     # 0xec -> LATIN CAPITAL LETTER I WITH DIAERESIS
    u'\xCC'     # 0xed -> LATIN CAPITAL LETTER I WITH GRAVE
    u'\xD3'     # 0xee -> LATIN CAPITAL LETTER O WITH ACUTE
    u'\xD4'     # 0xef -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    u'\uF8FF'     # 0xf0 -> APPLE SIGN
    u'\xD2'     # 0xf1 -> LATIN CAPITAL LETTER O WITH GRAVE
    u'\xDA'     # 0xf2 -> LATIN CAPITAL LETTER U WITH ACUTE
    u'\xDB'     # 0xf3 -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    u'\xD9'     # 0xf4 -> LATIN CAPITAL LETTER U WITH GRAVE
    u'\u0131'     # 0xf5 -> LATIN SMALL LETTER DOTLESS I
    u'\u01B7'     # 0xf6 -> LATIN CAPITAL LETTER EZH
    u'\u0292'     # 0xf7 -> LATIN SMALL LETTER EZH
    u'\u01EE'     # 0xf8 -> LATIN CAPITAL LETTER EZH WITH CARON
    u'\u01EF'     # 0xf9 -> LATIN SMALL LETTER EZH WITH CARON
    u'\u01E4'     # 0xfa -> LATIN CAPITAL LETTER G WITH STROKE
    u'\u01E5'     # 0xfb -> LATIN SMALL LETTER G WITH STROKE
    u'\u01E6'     # 0xfc -> LATIN CAPITAL LETTER G WITH CARON
    u'\u01E7'     # 0xfd -> LATIN SMALL LETTER G WITH CARON
    u'\u01E8'     # 0xfe -> LATIN CAPITAL LETTER K WITH CARON
    u'\u01E9'     # 0xff -> LATIN SMALL LETTER K WITH CARON
)

### Encoding table
encoding_table=codecs.charmap_build(decoding_table)

def lookup(encoding):
    if encoding == 'macsami':
        return getregentry()
    return None

codecs.register(lookup)
