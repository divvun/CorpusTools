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

    # iso-ir-197 converted as iconv -f mac -t utf8
    # 1
    {
        u"·": u"á",
        u"≥": u"š",
        u"¢": u"č",
        u"§": u"đ",
        u"∫": u"ž",
        u"±": u"ŋ",
        u"¡": u"Á",
        u"°": u"Č",
        u"∏": u"ŧ",
        u"≤": u"Š",
        u"£": u"Đ",
        u"Ø": u"Ŋ",
        u"π": u"Ž",
        u"µ": u"Ŧ",
        u"Ê": u"æ",
        u"Δ": u"Æ",
        u"¯": u"ø",
        u"ÿ": u"Ø",
        u"Â": u"å",
        u"≈": u"Å",
        u"‰": u"ä",
        u"ƒ": u"Ä",
        u"ˆ": u"ö",
        u"÷": u"Ö",
    },

    # winsami2 converted as iconv -f cp1252 -t utf8
    # á, æ, å, ø, ö, ä, š appear as themselves
    # found in freecorpus/orig/sme/admin/sd/other_files/dc_00_1.doc
    # and freecorpus/orig/sme/admin/guovda/KS_02.12.99.doc
    # 2
    {
        u"á": u"á",
        u"„": u"č",
        u"˜": u"đ",
        u"¹": u"ŋ",
        u"¿": u"ž",
        u"Á": u"Á",
        u"‚": u"Č",
        u"¼": u"ŧ",
        u"‰": u"Đ",
        u"¸": u"Ŋ",
        u"¾": u"Ž",
        u"º": u"Ŧ",
    },

    # iso-ir-197 converted as iconv -f latin1/cp1252 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    # 3
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
        u"¥": u"Đ",
        u"¯": u"Ŋ",
        u"¹": u"Ž",
        u"µ": u"Ŧ",
    },

    # mac-sami to latin1
    # 4
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
        u"ª ": u"™ ",
        u"ªÓ": u"™”",
        u"Ã": u"√",
        u"Ð": u"–",
        u"": u"",
        u"¥": u"•",
        u"": u"ü",
        u"": u"í"
        #"Ç": u"«",
        #"È": u"»",
    },

    # 5 winsam as cp1252
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
    # 6
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

    # 7
    {
        u"": u"á",
        u"_": u"š",
        u"ã": u"č",
        u"÷": u"đ",
        u"À": u"ž",
        u"ç": u"Á",
        u"â": u"Č",
        u"¿": u"ø"
    },
    # 8
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
    ,
]

LIMITS = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8:2}


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

    def get_sami_letter_frequency(self, content):
        """@brief Get the frequency of real "sami" letters in content

        @param content is a unicode text (not utf8 str)
        #return sami_letter_frequency is a dict of letters and their
        frequencies
        """
        sami_letter_frequency = {}

        for sami_letter in [u'á', u'š', u'ŧ', u'ŋ', u'đ', u'ž', u'č', u'æ',
                            u'ø', u'å', u'ä', u'ö']:
            sami_letter_frequency[sami_letter] = \
                len(re.compile(sami_letter).findall(content.lower()))

        #print len(content)
        #for (key, value) in sami_letter_frequency.items():
            #print key + ":", value

        return sami_letter_frequency

    def get_encoding_frequency(self, content, position):
        """@ brief Get the frequency of the letters found at position
        "position" in CTYPES

        @param content is a unicode text (not utf8 str)
        @param position is the position in CTYPES
        @return encoding_frequency is a dict of letters from CTYPES[position]
        and their frequencies
        """

        encoding_frequency = {}

        for key in CTYPES[position].viewkeys():

            if len(re.compile(key).findall(content)) > 0:
                encoding_frequency[key] = len(re.compile(key).findall(content))
                #print key + ":", CTYPES[position][key], \
                    #len(re.compile(key).findall(content))

        return encoding_frequency

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
        maxhits = 0

        content = content.decode('utf8')
        sami_letter_frequency = self.get_sami_letter_frequency(content)

        for position in range(0, len(CTYPES)):
            encoding_frequency = self.get_encoding_frequency(content, position)

            num = len(encoding_frequency)
            hits = 0
            hitter = False
            for key in encoding_frequency.keys():
                try:
                    if (not sami_letter_frequency[
                            CTYPES[position][key].lower()]):
                        hitter = True
                except KeyError:
                    pass
                hits += encoding_frequency[key]

            #if hits > 0:
                #print "position", position, "hits", hits, "num", num

            if hits > maxhits and LIMITS[position] <= num and hitter:
                winner = position
                maxhits = hits
                #print "winner", winner, "maxhits", maxhits

        #print "the winner is", winner

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

            if position == 5:
                text = text.replace(u"Ç", u"«")
                text = text.replace(u"È", u"»")

        return text.encode('utf8')

if __name__ == '__main__':
    eg = EncodingGuesser()
    print eg.guess_file_encoding(sys.argv[1])
