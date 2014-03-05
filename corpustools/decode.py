# -*- coding: utf-8 -*-
'''(Northern) sami character eight bit encodings have been semi or
non official standards and have been converted to the various systems'
internal encodings. This module have functions that revert the damage
done.
'''
import re
import sys

CTYPES = [

    # mac-sami converted as iconv -f mac -t utf8
    # mac-sami á appears at the same place as latin1 á
    # 0
    {
        u"á": u"á",
        u"ª": u"š",
        u"∏": u"č",
        u"π": u"đ",
        u"Ω": u"ž",
        u"∫": u"ŋ",
        u"Á": u"Á",
        u"¢": u"Č",
        u"º": u"ŧ",
        u"¥": u"Š",
        u"∞": u"Đ",
        u"±": u"Ŋ",
        u"¸": u"Ŋ",
        u"∑": u"Ž",
        u"µ": u"Ŧ",
    },

    # winsami2 converted as iconv -f cp1252 -t utf8
    # á, æ, å, ø, ö, ä, š appear as themselves
    # found in freecorpus/orig/sme/admin/sd/other_files/dc_00_1.doc
    # and freecorpus/orig/sme/admin/guovda/KS_02.12.99.doc
    # 1
    {
        u"á": u"á",
        u"š": u"š",
        u"„": u"č",
        u"˜": u"đ",
        u"¹": u"ŋ",
        u"¿": u"ž",
        u"Á": u"Á",
        u"‚": u"Č",
        u"¼": u"ŧ",
        u"Š": u"Š",
        u"‰": u"Đ",
        u"¸": u"Ŋ",
        u"¾": u"Ž",
        u"º": u"Ŧ",
    },

    # iso-ir-197 converted as iconv -f latin1/cp1252 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    # 2
    {
        u"á": u"á",
        u"³": u"š",
        u"¢": u"č",
        u"¤": u"đ",
        u"º": u"ž",
        u"±": u"ŋ",
        u"Á": u"Á",
        u"¡": u"Č",
        u"¸": u"ŧ",
        u"²": u"Š",
        u"£": u"Đ",
        u"¯": u"Ŋ",
        u"¹": u"Ž",
        u"µ": u"Ŧ",
    },

    # mac-sami to latin1
    # 3
    {
        u"": u"á",
        u"»": u"š",
        u"¸": u"č",
        u"¹": u"đ",
        u"½": u"ž",
        u"º": u"ŋ",
        u"ç": u"Á",
        u"¢": u"Č",
        u"¼": u"ŧ",
        u"´": u"Š",
        u"°": u"Đ",
        u"±": u"Ŋ",
        u"·": u"Ž",
        u"µ": u"Ŧ",

        u"¾": u"æ",
        u"®": u"Æ",
        u"¿": u"ø",
        u"¯": u"Ø",
        u"": u"å",
        u"": u"é",
        u"Œ": u"å",
        u"": u"Å",
        u"": u"ä",
        u"": u"Ä",
        u"": u"ö",
        u"": u"Ö",
        u"Ê": u" ",
        u"¤": u"§",
        u"Ò": u"“",
        u"Ó": u"”",
        u"ª": u"™",
        u"Ã": u"√",
        u"Ð": u"–",
        u"": u"",
        u"¥": u"•",
        u"": u"ü",
        u"": u"í",
        u"Ô": u"‘",
        u"Õ": u"’",
        u"¡": u"°",
        u"Ñ": u"—",
        u"¬": u"¨",
        u"": u"õ",
        u"": u"â",
        #"Ç": u"«",
        #"È": u"»",
    },

    # 4 winsam as cp1252
    {
        u"á": u"á",
        u"ó": u"š",
        u"ç": u"č",
        u"ð": u"đ",
        u"þ": u"ž",
        u"ñ": u"ŋ",
        u"Á": u"Á",
        u"Ç": u"Č",
        u"ý": u"ŧ",
        u"Ó": u"Š",
        u"Ð": u"Đ", # U+00D0 to U+0110
        u"Ñ": u"Ŋ",
        u"Þ": u"Ž",
        u"Ý": u"Ŧ",
    },

    # latin4 as cp1252/latin1
    # á, æ, å, ø, ö, ä appear as themselves
    # 5
    {
        u"á": u"á",
        u"¹": u"š",
        u"è": u"č",
        u"ð": u"đ",
        u"¾": u"ž",
        u"¿": u"ŋ",
        u"Á": u"Á",
        u"È": u"Č",
        u"¼": u"ŧ",
        u"©": u"Š",
        u"Ð": u"Đ", # U+00D0 to U+0110
        u"½": u"Ŋ",
        u"®": u"Ž",
        u"¬": u"Ŧ",
    },

    # 6
    {
        u"": u"á",
        u"_": u"š",
        u"ã": u"č",
        u"÷": u"đ",
        u"À": u"ž",
        u"ç": u"Á",
        u"â": u"Č",
        u"¿": u"ø",
        u"¼": u"ŧ",
    },

    # 7
    {
        u"á": u"á",
        u"ó": u"š",
        u"ç": u"č",
        u"¤": u"đ",
        u"º": u"ž",
        u"Á": u"Á",
        u"Ç": u"Č",
        u"Ó": u"Š",
        u"£": u"Đ",
    }
]

class EncodingGuesser(object):
    """Try to find out if some text or a file has faultily encoded (northern)
    sami letters
    """

    def guess_file_encoding(self, filename):
        """ @brief Guess the encoding of a file

        @param filename name of an utf-8 encoded file
        @return winner is an int, pointing to a position in CTYPES, or -1
        """

        infile = open(filename)
        content = infile.read()
        infile.close()
        winner = self.guess_body_encoding(content)

        return winner

    def guess_body_encoding(self, content):
        """@brief guess the encoding of the string content

        First get the frequencies of the "sami letters"
        Then get the frequencies of the letters in the encodings in CTYPES

        If "sami letters" that the encoding tries to fix exist in "content",
        disregard the encoding

        @param content a utf-8 encoded string
        @return winner is an int pointing to a position in CTYPES or -1
        to tell that no known encoding is found
        """
        winner = None

        content = content.decode('utf8')
        if ((u'' in content and not u'ã' in content) or (u"" in content)):
            winner = 3
        elif u'' in content and u'ã':
            winner = 6
        elif u'³' in content and u'¢' in content and u'¤' in content:
            winner = 2
        elif u'á' in content and u'ª' in content:
            winner = 0
        elif u'ó' in content and u'ç' in content and u'ð' in content:
            winner = 4
        elif u'á' in content and u'è' in content and u'ð' in content:
            winner = 5
        elif u'ó' in content and u'ç' in content and u'¤' in content:
            winner = 7
        elif u'„' in content and u'˜' in content and u'¿' in content:
            winner = 1

        return winner

    def guess_person_encoding(self, person):
        """@brief guess the encoding of the string person

        This is a little simplified version of guess_body_encoding because the
        person string is short

        @param person a utf-8 encoded string
        @return winner is an int pointing to a position in CTYPES or -1
        to tell that no known encoding is found
        """

        person = person.decode('utf8')
        person = person.lower()

        maxhits = 0
        for position in range(0, len(CTYPES)):
            hits = 0
            num = 0
            for key in CTYPES[position].viewkeys():

                #print len(re.compile(key).findall(content)), key
                if len(re.compile(key).findall(person)) > 0:
                    num = num + 1

                hits = hits + len(re.compile(key).findall(person))

            #print "position", position, "hits", hits, "num", num

            if hits > maxhits:
                winner = position
                maxhits = hits
                #print "winner", winner, "maxhits", maxhits

            # 8 always wins over 5 as long as there are any hits for 8
            if winner == 5 and num > 1:
                winner = 8

        #print "the winner is", winner
        return winner

    def decode_para(self, position, text):
        """@brief Replace letters in text with the ones from the dict at
        position position in CTYPES

        @param position which place the encoding has in the CTYPES list
        @param text utf8 encoded str
        @return utf8 encoded str
        """
        text = text.decode('utf8')

        if position is not None:
            encoding = CTYPES[position]

            for key, value in encoding.items():
                text = text.replace(key, value)

            if position == 3:
                text = text.replace(u"Ç", u"«")
                text = text.replace(u"È", u"»")

        return text.encode('utf8')

if __name__ == '__main__':
    eg = EncodingGuesser()
    print eg.guess_file_encoding(sys.argv[1])
