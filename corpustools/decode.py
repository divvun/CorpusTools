# -*- coding: utf-8 -*-
'''(Northern) sami character eight bit encodings have been semi or
non official standards and have been converted to the various systems' 
internal encodings. This module have functions that revert the damage
done.
'''
import re

CTYPES = [

    # mac-sami converted as iconv -f mac -t utf8
    # mac-sami á appears at the same place as latin1 á
    # 0
    {
        u"ª": u"š",
        u"¥": u"Š",
        u"º": u"ŧ",
        u"µ": u"Ŧ",
        u"∫": u"ŋ",
        u"±": u"Ŋ",
        u"¸": u"Ŋ",
        u"π": u"đ",
        u"∞": u"Đ",
        u"Ω": u"ž",
        u"∑": u"Ž",
        u"∏": u"č",
        u"¢": u"Č"
    },

    # iso-ir-197 converted as iconv -f mac -t utf8
    # 1
    {
        u"·": u"á",
        u"¡": u"Á",
        u"≥": u"š",
        u"≤": u"Š",
        u"∏": u"ŧ",
        u"µ": u"Ŧ",
        u"±": u"ŋ",
        u"Ø": u"Ŋ",
        u"§": u"đ",
        u"£": u"Đ",
        u"∫": u"ž",
        u"π": u"Ž",
        u"¢": u"č",
        u"°": u"Č",
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

    # á, æ, å, ø, ö, ä appear as themselves
    # 2
    {
        u"ƒ": u"š",    #
        u"√": u"ŋ",    #
        u"∂": u"đ",    #
        u"π": u"ž",    #
        u"ª": u"č",    #
        u"º": u"Č",    #
    },

    # winsami2 converted as iconv -f latin1 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    # 3
    {
        u"": u"š",
        u"": u"Š",
        u"¼": u"ŧ",
        u"º": u"Ŧ",
        u"¹": u"ŋ",
        u"¸": u"Ŋ",
        u"": u"đ",
        u"": u"Đ",
        u"¿": u"ž",
        u"¾": u"Ž",
        u"": u"č",
        u"": u"Č",
    },

    # iso-ir-197 converted as iconv -f latin1 -t utf8
    # á, æ, å, ø, ö, ä appear as themselves
    # 4
    {
        u"³": u"š",
        u"²": u"Š",
        u"¸": u"ŧ",
        u"µ": u"Ŧ",
        u"±": u"ŋ",
        u"¯": u"Ŋ",
        u"¤": u"đ",
        u"£": u"Đ",
        u"º": u"ž",
        u"¹": u"Ž",
        u"¢": u"č",
        u"¡": u"Č",
    },

    # mac-sami to latin1
    # 5
    {
        u"": u"á",
        u"‡": u"á",
        u"ç": u"Á",
        u"»": u"š",
        u"´": u"Š",
        u"¼": u"ŧ",
        u"µ": u"Ŧ",
        u"º": u"ŋ",
        u"±": u"Ŋ",
        u"¹": u"đ",
        u"°": u"Đ",
        u"½": u"ž",
        u"·": u"Ž",
        u"¸": u"č",
        u"¢": u"Č",
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
        #"Ç": u"«",
        #"È": u"»",
    },

    # found in boundcorpus/goldstandard/orig/sme/facta/GIEHTAGIRJI.correct.doc
    # and
    # boundcorpus/goldstandard/orig/sme/facta/learerhefte_-_vaatmarksfugler.doc
    # á, æ, å, ø, ö, ä appear as themselves
    # 6
    {
        u"ð": u"đ",
        u"Ç": u"Č",
        u"ç": u"č",
        u"ó": u"š",
        u"ý": u"ŧ",
        u"þ": u"ž",
    },

    # found in freecorpus/orig/sme/admin/sd/other_files/dc_00_1.doc
    # and freecorpus/orig/sme/admin/guovda/KS_02.12.99.doc
    # found in boundcorpus/orig/sme/bible/other_files/vitkan.pdf
    # latin4 as latin1
    # á, æ, å, ø, ö, ä appear as themselves
    # 7
    {
        u"ð": u"đ",
        u"È": u"Č",
        u"è": u"č",
        u"¹": u"š",
        u"¿": u"ŋ",
        u"¾": u"ž",
        u"¼": u"ŧ",
        u"‚": u"Č",
        u"„": u"č",
        #"¹": u"ŋ",
        u"˜": u"đ",
        #"¿": u"ž",
    },

    # á, æ, å, ø, ö, ä appear as themselves
    # 8
    {
        u"t1": u"ŧ",
        u"T1": u"Ŧ",
        u"s1": u"š",
        u"S1": u"Š",
        u"n1": u"ŋ",
        u"N1": u"Ŋ",
        u"d1": u"đ",
        u"D1": u"Đ",
        u"z1": u"ž",
        u"Z1": u"Ž",
        u"c1": u"č",
        u"C1": u"Č",
        u"ï¾«": u"«",
        u"ï¾»": u"»",
    }
]

LIMITS = {0: 1, 1: 1, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 3}


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
        #return sami_letter_frequency is a dict of letters and their frequencies
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
        content = content.decode('utf8')
        sami_letter_frequency = self.get_sami_letter_frequency(content)

        maxhits = 0
        winner = -1
        for position in range(0, len(CTYPES)):
            encoding_frequency = self.get_encoding_frequency(content, position)

            num = len(encoding_frequency)
            hits = 0
            hitter = False
            for key in encoding_frequency.keys():
                try:
                    if not sami_letter_frequency[CTYPES[position][key].lower()]:
                        hitter = True
                except KeyError:
                    pass
                hits += encoding_frequency[key]

            #if hits > 0:
                #print "position", position, "hits", hits, "num", num

            if hits > maxhits and LIMITS[position] < num and hitter:
                winner = position
                maxhits = hits
                #print "winner", winner, "maxhits", maxhits

        #print "the winner is", winner

        return winner

    def guess_person_encoding(self, person):
        """@brief guess the encoding of the string person

        This is a little simplified version of guess_body_encoding because the
        person string is short

        @param content a utf-8 encoded string
        @return winner is an int pointing to a position in CTYPES or -1
        to tell that no known encoding is found
        """

        infile = open(filename)
        content = infile.read()
        content = content.decode('utf8')
        content = content.lower()
        infile.close()

        maxhits = 0
        for position in range(0, len(CTYPES)):
            hits = 0
            num = 0
            for key in CTYPES[position].viewkeys():

                #print len(re.compile(key).findall(content)), key
                if len(re.compile(key).findall(content)) > 0:
                    num = num + 1

                hits = hits + len(re.compile(key).findall(content))

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
        encoding = CTYPES[position]

        for key, value in encoding.items():
            text = text.replace(key, value)

        if position == 5:
            text = text.replace(u"Ç", u"«")
            text = text.replace(u"È", u"»")

        return text.encode('utf8')
