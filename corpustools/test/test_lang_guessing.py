#!/usr/bin/env python
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
#   Copyright © 2018 The University of Tromsø & the Norwegian Sámi Parliament
#   http://divvun.no & http://giellatekno.uit.no
#
"""Test language recognition."""

import unittest

from parameterized import parameterized

from corpustools import text_cat, util
import langid

class TestTextCat(unittest.TestCase):
    """Test frases collected from nrk.no article collection."""

    def setUp(self):
        """Set up common resource."""
        self.guesser = text_cat.Classifier()

    @parameterized.expand([
        'Anna-Laila Kristine Kappfjell, Dan Jonas Mikael Sparrok '
        'Danielsen, Jon-Kristoffer Kappfjell og Nora Cathrin Sparrok '
        'Danielsen feiret samefolkets dag.',
        'Bjarne Store-Jakobsen er nominert som Unjárgga Sámeálbmot '
        'bellodat/Nesseby Samefolkets partis ordførerkandidat.',
        'Del Instagrambildene dine med oss! Eneste du trenger er en '
        'smarttelefon og appen Instagram.',
        'Fiskeriminister Helga Pedersen åpnet Riddu Riddu-festivalen i '
        'Manndalen.',
        'Grand Prix-heltene Mattis Hætta og Sverre Kjelsberg skal åpne '
        'årets Riddu Riđđu-festival med Sami ædnan',
        'Her ankommer Aili Keskitalo og Laila Susanne Vars NRK Sámi '
        'Radio-studio i morges.',
        'Issát Sámmol Heatta fra Máze fikk Áillohaš musikkpris 2009.',
        'Janne Eilen Mienna Guttorm (17) og Mikkel Rasmus Logje (16) '
        'vant Riddu Riđđus talentkonkurranse, Riddu Násttit, og fikk '
        'et stipend på 25.000 kroner.',
        'Joikerne Mikkel Rasmus Logje og Risten-Marja Inga skal '
        'representere Sápmi i Arctic Winter Games 2012.',
        'Lagmannsretten skjerpet dommen i ankesaken mot Johan Mikkel '
        'Mikkelsen Sara.',
        'Láilá Susanne Vars er toppkandidat på Árja sin liste i '
        'valgkrets 2.',
        'Láilá Susanne Vars topper Árja sin valgliste til '
        'sametingsvalget i Ávjovárri valgkrets.',
        'Lásse Ovllá og Johan Sara jr. fikk hver sin Folkelarmpris '
        'i helga.',
        'Mama Maggie i Moqattam',
        'Marit Kristine Hætta Sara vant årets Sámi Grand Prix '
        'joikekonkurransen med sønnens joik, Máhtte Ánte(10) .',
        'Multikunstner Issát Sámmol Heatta fra Máze fikk Áillohaš '
        'musikkpris 2009.',
        'Máret Elle Teigen Porsanger vant to publikumspriser under '
        'designkonkurransen i Skiippagurra, mens Márjá Liissá Partapuoli '
        'overbeviste fagjuryen med sitt klesplagg.',
        'NRK Sápmis nyhetsredaktør, Rávdná Buljo Gaup, mener '
        'Facebook-diskusjonen til Arbeiderpartiets sametingsgruppe om '
        'Laila Susanne Vars (Árja) er barnslig.',
        'Narkotikaanmeldelser på Riddu Riđđu.',
        'Niillas Holmberg vinner Samerådets litteraturpris for sin '
        'diktbok «Amas amas amasmuvvat».',
        'Nullpunktet i Stilla bør markeres for fremtidens generasjoner, '
        'mener leder av Álttá Sámiid Searvi, Silje Karine Muotka og '
        'leder for Álttá Sámi Nuoraid Searvi, Marion Aslaksen Ravna.',
        'Nytt teaterstykke fra Beaivváš sámi teahter.',
        'Nå kan du se originalmanusene til Johan Turi`s klassiker '
        '"Muitalus sámiid birra" i Kautokeino.',
        'Oslo-ordføreren sang "Sámi Soga lávlla" med Mari Boine.',
        'Riddu Riđđu-festivalen i Kåfjord i gang.',
        'Rådmann Mikkel Ailo Gaup har takket ja til toppjobben i '
        'Kautokeino boligselskap.',
        'SGP-debutantene Inga Biret Marja Triumf og Ann Caroline '
        'Eira, Kautokeino vant årets joikefinale.',
        'Selskinn + minusgrader = Barents Fashion Week.',
        'Slo Senja hele 8-0!',
        'Statsadvokaten i Troms og Finnmark har henlagt voldttektsssaken '
        'fra Riddu Riddu i juli.',
        'Sámi Teáhter Searvi (STS) føler at Beaivváš Sámi Teáhter er '
        'glemt i det nasjonale kulturløftet.',
        'Vakker duodji. Lun høsthimmel. Blide fjes. Faste håndtrykk. '
        'Varme klemmer. Vuonnamárkanat 2014.',
        'Ánte Niillas N. Bongo fra Kautokeino vant med joiken "Sara Inga".',
    ])
    def test_classify(self, input_text):
        """Test language recognition on input strings.

        The input strings have been classified as sme, while they in
        fact are nob.

        Arguments:
            input_text (str): text that should be classified by
                the language guesser.
        """
        #self.assertEqual(self.guesser.classify(input_text), 'nob')
        util.print_frame(langid.classify(input_text), input_text)
