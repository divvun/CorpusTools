# -*- coding: utf-8 -*-

import unittest
from lxml import etree
import doctest
import lxml.doctestcompare as doctestcompare

from corpustools import errormarkup


class TestErrorMarkup(unittest.TestCase):
    def setUp(self):
        self.em = errormarkup.ErrorMarkup('testfilename')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

        pass

    def test_only_text_in_element(self):
        in_elem = etree.fromstring('<p>Muittán doložiid</p>')
        want = '<p>Muittán doložiid</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_parser_errorlang_infinity(self):
        in_elem = u'(molekylærbiologimi)∞(kal,bio)'
        want = u'<errorlang correct="kal,bio">molekylærbiologimi</errorlang>'

        got = self.em.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def test_error_parser_errorlang_infinity_with_new_lines(self):
        in_elem = u'\n\n\n\n(molekylærbiologimi)∞(kal,bio)\n\n\n\n'
        want = u'<errorlang correct="kal,bio">molekylærbiologimi</errorlang>'

        got = self.em.error_parser(in_elem)
        self.assertEqual(len(got), 2)
        self.assertXmlEqual(etree.tostring(got[1]), want)

    def test_quote_char(self):
        in_elem = u'”sjievnnijis”$(conc,vnn-vnnj|sjievnnjis)'
        want = u'<errorort errorinfo="conc,vnn-vnnj" \
        correct="sjievnnjis">”sjievnnijis”</errorort>'

        got = self.em.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def test_paragraph_character(self):
        in_elem = etree.fromstring('<p>Vuodoláhkaj §110a</p>')
        want = u'<p>Vuodoláhkaj §110a</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_parser_errorort1(self):
        in_elem = u'jne.$(adv,typo|jna.)'
        want = u'<errorort errorinfo="adv,typo" correct="jna.">jne.</errorort>'

        got = self.em.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def test_errorort1(self):
        in_elem = etree.fromstring('<p>jne.$(adv,typo|jna.)</p>')
        want = '<p><errorort errorinfo="adv,typo" \
        correct="jna.">jne.</errorort></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_errorort2(self):
        in_elem = etree.fromstring('<p>daesn\'$daesnie</p>')
        want = '<p><errorort correct="daesnie">daesn\'</errorort></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_input_contains_slash(self):
        in_elem = etree.fromstring(
            '<p>magistter/$(loan,vowlat,e-a|magisttar)</p>')
        want = '<p><errorort correct="magisttar" \
        errorinfo="loan,vowlat,e-a">magistter/</errorort></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct1(self):
        in_elem = etree.fromstring('<p>1]§Ij</p>')
        want = '<p><error correct="Ij">1]</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct2(self):
        in_elem = etree.fromstring('<p>væ]keles§(væjkeles)</p>')
        want = '<p><error correct="væjkeles">væ]keles</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct3(self):
        in_elem = etree.fromstring('<p>smávi-§smávit-</p>')
        want = '<p><error correct="smávit-">smávi-</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct4(self):
        in_elem = etree.fromstring('<p>CD:t§CD:at</p>')
        want = '<p><error correct="CD:at">CD:t</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct5(self):
        in_elem = etree.fromstring('<p>DNB-feaskáris§(DnB-feaskáris)</p>')
        want = '<p><error correct="DnB-feaskáris">DNB-feaskáris</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct6(self):
        in_elem = etree.fromstring('<p>boade§boađe</p>')
        want = '<p><error correct="boađe">boade</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct7(self):
        in_elem = etree.fromstring('<p>2005’as§2005:s</p>')
        want = '<p><error correct="2005:s">2005’as</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct8(self):
        in_elem = etree.fromstring('<p>NSRii§NSR:i</p>')
        want = '<p><error correct="NSR:i">NSRii</error></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_correct9(self):
        in_elem = etree.fromstring('<p>Nordkjosbotn\'ii§Nordkjosbotnii</p>')
        want = '<p><error correct="Nordkjosbotnii">Nordkjosbotn\'ii</error>\
        </p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_errorort3(self):
        in_elem = etree.fromstring('<p>nourra$(a,meta|nuorra)</p>')
        want = '<p><errorort errorinfo="a,meta" \
correct="nuorra">nourra</errorort></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_morphsyn1(self):
        in_elem = etree.fromstring('<p>(Nieiddat leat nuorra)£(a,spred,nompl,\
nomsg,agr|Nieiddat leat nuorat)</p>')
        want = '<p><errormorphsyn errorinfo="a,spred,nompl,nomsg,agr" \
correct="Nieiddat leat nuorat">Nieiddat leat nuorra</errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_parser_error_morphsyn1(self):
        in_elem = u'(Nieiddat leat nuorra)£(a,spred,nompl,nomsg,agr|Nieiddat \
leat nuorat)'
        want = u'<errormorphsyn errorinfo="a,spred,nompl,nomsg,agr" \
correct="Nieiddat leat nuorat">Nieiddat leat nuorra</errormorphsyn>'

        got = self.em.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def test_error_syn1(self):
        in_elem = etree.fromstring('<p>(riŋgen nieidda lusa)¥(x,pph|riŋgen \
niidii)</p>')
        want = '<p><errorsyn errorinfo="x,pph" correct="riŋgen niidii">riŋgen \
nieidda lusa</errorsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_syn2(self):
        in_elem = etree.fromstring('<p>ovtta¥(num,redun| )</p>')
        want = '<p><errorsyn errorinfo="num,redun" \
correct=" ">ovtta</errorsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_erro_lex1(self):
        in_elem = etree.fromstring('<p>dábálaš€(adv,adj,der|dábálaččat)</p>')
        want = '<p><errorlex errorinfo="adv,adj,der" \
correct="dábálaččat">dábálaš</errorlex></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_ortreal1(self):
        in_elem = \
            etree.fromstring('<p>ráhččamušaid¢(noun,mix|rahčamušaid)</p>')
        want = '<p><errorortreal errorinfo="noun,mix" \
        correct="rahčamušaid">ráhččamušaid</errorortreal></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_ortreal2(self):
        in_elem = etree.fromstring('<p>gitta Nordkjosbotn\'ii$Nordkjosbotnii (\
mii lea ge nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos</p>')
        want = '<p>gitta <errorort correct="Nordkjosbotnii">Nordkjosbotn\'ii\
</errorort> (mii lea ge <errorort correct="Nordkjosbotn">nordkjosbotn\
</errorort> sámegillii? Muhtin, veahket mu!) gos</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_parser_with_two_simple_errors(self):
        in_elem = u"gitta Nordkjosbotn'ii$Nordkjosbotnii (mii lea ge \
nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"
        got = self.em.error_parser(in_elem)

        self.assertEqual(len(got), 3)
        self.assertEqual(got[0], u'gitta ')
        self.assertEqual(etree.tostring(got[1], encoding='utf8'), '<errorort \
correct="Nordkjosbotnii">Nordkjosbotn\'ii</errorort> (mii lea ge ')
        self.assertEqual(
            etree.tostring(got[2], encoding='utf8'), '<errorort \
correct="Nordkjosbotn">nordkjosbotn</errorort> sámegillii? Muhtin, veahket \
mu!) gos')

    def test_error_morphsyn2(self):
        in_elem = etree.fromstring('<p>Čáppa muohtaskulptuvrraid ráhkadeapmi \
VSM olggobealde lei maiddái ovttasbargu gaskal (skuvla ohppiid)£\
(noun,attr,gensg,nomsg,case|skuvlla ohppiid) ja VSM.</p>')
        want = '<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei \
maiddái ovttasbargu gaskal <errormorphsyn \
errorinfo="noun,attr,gensg,nomsg,case" correct="skuvlla ohppiid">\
skuvla ohppiid</errormorphsyn> ja VSM.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_errorort4(self):
        in_elem = etree.fromstring('<p>- ruksesruonáčalmmehisvuohta lea \
sullii 8%:as$(acr,suf|8%:s)</p>')
        want = '<p>- ruksesruonáčalmmehisvuohta lea sullii <errorort \
correct="8%:s" errorinfo="acr,suf">8%:as</errorort></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_error_ortreal3(self):
        in_elem = etree.fromstring('<p>( nissonin¢(noun,suf|nissoniin) dušše \
(0.6 %:s)£(0.6 %) )</p>')
        want = '<p>( <errorortreal errorinfo="noun,suf" correct="nissoniin">\
nissonin</errorortreal> dušše <errormorphsyn correct="0.6 %">\
0.6 %:s</errormorphsyn> )</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_errorort5(self):
        in_elem = etree.fromstring('<p>(haploida) ja njiŋŋalas$(noun,á|\
njiŋŋálas) ságahuvvon$(verb,a|sagahuvvon) manneseallas (diploida)</p>')
        want = '<p>(haploida) ja <errorort errorinfo="noun,á" \
correct="njiŋŋálas">njiŋŋalas</errorort> <errorort errorinfo="verb,a" \
correct="sagahuvvon">ságahuvvon</errorort> manneseallas (diploida)</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_errorort6(self):
        in_elem = etree.fromstring('<p>(gii oahpaha) giinu$(x,notcmp|gii nu) \
manai intiánalávlagat$(loan,conc|indiánalávlagat) (guovža-klána)$\
(noun,cmp|guovžaklána) olbmuid</p>')
        want = '<p>(gii oahpaha) <errorort errorinfo="x,notcmp" \
correct="gii nu">giinu</errorort> manai <errorort \
errorinfo="loan,conc" correct="indiánalávlagat">intiánalávlagat</errorort> \
<errorort errorinfo="noun,cmp" correct="guovžaklána">guovža-klána</errorort> \
olbmuid</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_preserve_space_at_end_of_sentence(self):
        in_elem = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|\
Mikkelsen) lea ráhkadan. </p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" \
errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. </p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    def test_place_error_elements_before_old_element1(self):
        '''Test if errorlements are inserted before the span element.
        '''
        in_elem = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|\
Mikkelsen) lea ráhkadan. bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu. \
<span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" \
errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <errorort \
correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> \
miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»\
</span></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    def test_place_error_elements_before_old_element2(self):
        '''Test if errorlements are inserted before the span element.
        '''
        in_elem = etree.fromstring('<p>Mikkelsens$(typo|Mikkelsen) lea \
ráhkadan. bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu. <span type="quote" \
xml:lang="eng">«Best Shorts Competition»</span></p>')

        want = '<p><errorort correct="Mikkelsen" errorinfo="typo">\
Mikkelsens</errorort> lea ráhkadan. <errorort correct="bálkkašumi" errorinfo=\
"vowlat,á-a">bálkkášumi</errorort> miessemánu. <span type="quote" \
xml:lang="eng">«Best Shorts Competition»</span></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    def test_place_error_element_after_old_element(self):
        in_elem = etree.fromstring('<p>I 1864 ga han ut boka \
<span type="quote" xml:lang="swe">"Fornuftigt Madstel"</span>. \
Asbjørsen$(prop,typo|Asbjørnsen) døde 5. januar 1885, nesten 73 år \
gammel.</p>')

        want = '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">\
"Fornuftigt Madstel"</span>. <errorort correct="Asbjørnsen" \
errorinfo="prop,typo">Asbjørsen</errorort> døde 5. januar 1885, nesten \
73 år gammel.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    def test_place_error_element_before_and_after_old_element(self):
        '''The input:
        buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan.
        «Best Shorts Competition» bálkkášumi$(vowlat,á-a|bálkkašumi)
        miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">
         «Best Shorts Competition»</span>
         bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.
         <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort>
         lea ráhkadan.</p>
        '''
        in_elem = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|\
Mikkelsen) lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts \
Competition»</span> bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.</p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" \
errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" \
xml:lang="eng">«Best Shorts Competition»</span> <errorort correct=\
"bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    def test_add_error_markup3Levels(self):
        '''The input:
        buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan.
        «Best Shorts Competition» bálkkášumi$(vowlat,á-a|bálkkašumi)
        miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">
         «Best Shorts Competition»</span>
         bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.
         <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort>
         lea ráhkadan.</p>
        '''
        in_elem = etree.fromstring('<p>buvttadeaddji Anstein <errorort \
correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. \
<span type="quote" xml:lang="eng">«Best Shorts Competition»</span> \
<errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> \
miessemánu. <em>buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea \
ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> \
bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.</em></p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" \
errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" \
xml:lang="eng">«Best Shorts Competition»</span> <errorort \
correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu. \
<em>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">\
Mikkelsens</errorort> lea ráhkadan. <span type="quote" xml:lang="eng">«Best \
Shorts Competition»</span> <errorort correct="bálkkašumi" \
errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu.</em></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertEqual(got, want)

    #Nested markup
    def test_nested_markup1(self):
        in_elem = etree.fromstring('<p>(šaddai$(verb,conc|šattai) ollu áššit)£\
(verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit)</p>')
        want = '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,tense" \
correct="šadde ollu áššit"><errorort errorinfo="verb,conc" correct="šattai">\
šaddai</errorort> ollu áššit</errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup2(self):
        in_elem = etree.fromstring('<p>(guokte ganddat§(n,á|gánddat))£(n,nump,\
gensg,nompl,case|guokte gándda)</p>')
        want = '<p><errormorphsyn errorinfo="n,nump,gensg,nompl,case" \
correct="guokte gándda">guokte <error errorinfo="n,á" correct="gánddat">\
ganddat</error></errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup3(self):
        in_elem = etree.fromstring('<p>(Nieiddat leat nourra$(adj,meta|\
nuorra))£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)</p>')
        want = '<p><errormorphsyn errorinfo="adj,spred,nompl,nomsg,agr" \
correct="Nieiddat leat nuorat">Nieiddat leat <errorort errorinfo="adj,meta" \
correct="nuorra">nourra</errorort></errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup4(self):
        in_elem = etree.fromstring('<p>(leat (okta máná)£(n,spred,nomsg,gensg,\
case|okta mánná))£(v,v,sg3prs,pl3prs,agr|lea okta mánná)</p>')
        want = '<p><errormorphsyn errorinfo="v,v,sg3prs,pl3prs,agr" \
correct="lea okta mánná">leat <errormorphsyn errorinfo="n,spred,nomsg,gensg,\
case" correct="okta mánná">okta máná</errormorphsyn></errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup5(self):
        in_elem = etree.fromstring('<p>heaitit dáhkaluddame$(verb,a|\
dahkaluddame) ahte sis máhkaš¢(adv,á|mahkáš) livččii makkarge$(adv,á|makkárge)\
politihkka, muhto rahpasit baicca muitalivčče (makkar$(interr,á|makkár) \
soga)€(man soga) sii ovddasttit$(verb,conc|ovddastit).</p>')
        want = '<p>heaitit <errorort correct="dahkaluddame" \
errorinfo="verb,a">dáhkaluddame</errorort> ahte sis <errorortreal \
correct="mahkáš" errorinfo="adv,á">máhkaš</errorortreal> livččii \
<errorort correct="makkárge" errorinfo="adv,á">makkarge</errorort> \
politihkka, muhto rahpasit baicca muitalivčče <errorlex correct="man soga">\
<errorort correct="makkár" errorinfo="interr,á">makkar</errorort> soga\
</errorlex> sii <errorort correct="ovddastit" errorinfo="verb,conc">\
ovddasttit</errorort>.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_process_text29(self):
        text = u'(Bearpmahat$(noun,svow|Bearpmehat) earuha€(verb,v,w|sirre))\
£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit) uskki ja loaiddu.'
        want = [u'(Bearpmahat',
                u'$(noun,svow|Bearpmehat)',
                u' earuha',
                u'€(verb,v,w|sirre)',
                u')',
                u'£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit)',
                u' uskki ja loaiddu.']

        self.assertEqual(self.em.process_text(text), want)

    def test_nested_markup6(self):
        in_elem = etree.fromstring('<p>(Bearpmahat$(noun,svow|Bearpmehat) \
earuha€(verb,v,w|sirre))£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit) \
uskki ja loaiddu.</p>')
        want = '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,agr" \
correct="Bearpmehat sirrejit"><errorort errorinfo="noun,svow" \
correct="Bearpmehat">Bearpmahat</errorort> <errorlex errorinfo="verb,v,w" \
correct="sirre">earuha</errorlex></errormorphsyn> uskki ja loaiddu.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_process_text30(self):
        text = u'Mirja ja Line leaba (gulahallan olbmožat)¢(noun,cmp|\
gulahallanolbmožat)€gulahallanolbmot'
        want = [u'Mirja ja Line leaba (gulahallan olbmožat)',
                u'¢(noun,cmp|gulahallanolbmožat)',
                u'€gulahallanolbmot']

        self.assertEqual(self.em.process_text(text), want)

    def test_nested_markup7(self):
        in_elem = etree.fromstring('<p>Mirja ja Line leaba (gulahallan \
olbmožat)¢(noun,cmp|gulahallanolbmožat)€gulahallanolbmot</p>')
        want = '<p>Mirja ja Line leaba <errorlex correct="gulahallanolbmot">\
<errorortreal errorinfo="noun,cmp" correct="gulahallanolbmožat">gulahallan \
olbmožat</errorortreal></errorlex></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup8(self):
        in_elem = etree.fromstring('<p>(Ovddit geasis)£(noun,advl,gensg,locsg,\
case|Ovddit geasi) ((čoaggen$(verb,mono|čoggen) ollu jokŋat)£(noun,obj,genpl,\
nompl,case|čoggen ollu joŋaid) ja sarridat)£(noun,obj,genpl,nompl,case|čoggen \
ollu joŋaid ja sarridiid)</p>')
        want = '<p><errormorphsyn errorinfo="noun,advl,gensg,locsg,case" \
correct="Ovddit geasi">Ovddit geasis</errormorphsyn> <errormorphsyn \
errorinfo="noun,obj,genpl,nompl,case" correct="čoggen ollu joŋaid ja \
sarridiid"><errormorphsyn errorinfo="noun,obj,genpl,nompl,case" \
correct="čoggen ollu joŋaid"><errorort errorinfo="verb,mono" correct="čoggen">\
čoaggen</errorort> ollu jokŋat</errormorphsyn> ja sarridat</errormorphsyn></p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_nested_markup9(self):
        in_elem = etree.fromstring('<p>Bruk ((epoxi)$(noun,cons|epoksy) lim)¢\
(noun,mix|epoksylim) med god kvalitet.</p>')
        want = '<p>Bruk <errorortreal errorinfo="noun,mix" \
correct="epoksylim"><errorort errorinfo="noun,cons" correct="epoksy">epoxi\
</errorort> lim</errorortreal> med god kvalitet.</p>'

        self.em.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding='utf8')
        self.assertXmlEqual(got, want)

    def test_process_text1(self):
        text = u'jne.$(adv,typo|jna.)'
        want = [u'jne.', u'$(adv,typo|jna.)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text2(self):
        text = u"daesn'$daesnie"
        want = [u"daesn'", "$daesnie"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text3(self):
        text = u"1]§Ij"
        want = [u"1]", u"§Ij"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text4(self):
        text = u"væ]keles§(væjkeles)"
        want = [u"væ]keles", u"§(væjkeles)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text5(self):
        text = u"smávi-§smávit-"
        want = [u"smávi-", u"§smávit-"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text6(self):
        text = u"CD:t§CD:at"
        want = [u"CD:t", u"§CD:at"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text7(self):
        text = u"DNB-feaskáris§(DnB-feaskáris)"
        want = [u"DNB-feaskáris", u"§(DnB-feaskáris)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text8(self):
        text = u"boade§boađe"
        want = [u"boade", u"§boađe"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text9(self):
        text = u"2005’as§2005:s"
        want = [u"2005’as", u"§2005:s"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text10(self):
        text = u"NSRii§NSR:ii"
        want = [u"NSRii", u"§NSR:ii"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text11(self):
        text = u"Nordkjosbotn'ii§Nordkjosbotnii"
        want = [u"Nordkjosbotn'ii", u"§Nordkjosbotnii"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text12(self):
        text = u"nourra$(a,meta|nuorra)"
        want = [u"nourra", u"$(a,meta|nuorra)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text13(self):
        text = u"(Nieiddat leat nuorra)£(a,spred,nompl,nomsg,agr|Nieiddat \
leat nuorat)"
        want = [u"(Nieiddat leat nuorra)",
                u"£(a,spred,nompl,nomsg,agr|Nieiddat leat nuorat)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text14(self):
        text = u"(riŋgen nieidda lusa)¥(x,pph|riŋgen niidii)"
        want = [u"(riŋgen nieidda lusa)", u"¥(x,pph|riŋgen niidii)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text15(self):
        text = u"ovtta¥(num,redun| )"
        want = [u"ovtta", u"¥(num,redun| )"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text16(self):
        text = u"dábálaš€(adv,adj,der|dábálaččat)"
        want = [u"dábálaš", u"€(adv,adj,der|dábálaččat)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text17(self):
        text = u"ráhččamušaid¢(noun,mix|rahčamušaid)"
        want = [u"ráhččamušaid", u"¢(noun,mix|rahčamušaid)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text18(self):
        text = u"gitta Nordkjosbotn'ii$Nordkjosbotnii (mii lea ge \
nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"
        want = [u"gitta Nordkjosbotn'ii",
                u"$Nordkjosbotnii",
                u" (mii lea ge nordkjosbotn",
                u"$Nordkjosbotn",
                u" sámegillii? Muhtin, veahket mu!) gos"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text19(self):
        text = u"gaskal (skuvla ohppiid)£(noun,attr,gensg,nomsg,case|\
skuvlla ohppiid) ja VSM."
        want = [u"gaskal (skuvla ohppiid)",
                u"£(noun,attr,gensg,nomsg,case|skuvlla ohppiid)",
                u" ja VSM."]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text20(self):
        text = u"- ruksesruonáčalmmehisvuohta lea sullii 8%:as$(acr,suf|8%:s)"
        want = [u"- ruksesruonáčalmmehisvuohta lea sullii 8%:as",
                u"$(acr,suf|8%:s)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text21(self):
        text = u"( nissonin¢(noun,suf|nissoniin) dušše (0.6 %:s)£(0.6 %) )"
        want = [u"( nissonin",
                u"¢(noun,suf|nissoniin)",
                u" dušše (0.6 %:s)",
                u"£(0.6 %)",
                u" )"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text22(self):
        text = u"(haploida) ja njiŋŋalas$(noun,á|njiŋŋálas) \
ságahuvvon$(verb,a|sagahuvvon) manneseallas (diploida)"
        want = [u"(haploida) ja njiŋŋalas",
                u"$(noun,á|njiŋŋálas)",
                u" ságahuvvon",
                u"$(verb,a|sagahuvvon)",
                u" manneseallas (diploida)"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text23(self):
        text = u"(gii oahpaha) giinu$(x,notcmp|gii nu) manai \
intiánalávlagat$(loan,conc|indiánalávlagat) (guovža-klána)$(noun,cmp|\
guovžaklána) olbmuid"
        want = [u"(gii oahpaha) giinu",
                u"$(x,notcmp|gii nu)",
                u" manai intiánalávlagat",
                u"$(loan,conc|indiánalávlagat)",
                u" (guovža-klána)",
                u"$(noun,cmp|guovžaklána)",
                u" olbmuid"]

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text24(self):
        text = u'(šaddai$(verb,conc|šattai) ollu áššit)£(verb,fin,pl3prs,\
sg3prs,tense|šadde ollu áššit)'
        want = [u'(šaddai',
                u"$(verb,conc|šattai)",
                u" ollu áššit)",
                u'£(verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text25(self):
        text = u'(guokte ganddat§(n,á|gánddat))£(n,nump,gensg,nompl,\
case|guokte gándda)'
        want = [u'(guokte ganddat',
                u'§(n,á|gánddat)',
                u')',
                u'£(n,nump,gensg,nompl,case|guokte gándda)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text26(self):
        text = u'(Nieiddat leat nourra$(adj,meta|\
nuorra))£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)'
        want = [u'(Nieiddat leat nourra',
                u'$(adj,meta|nuorra)',
                u')',
                u'£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text27(self):
        text = u'(leat (okta máná)£(n,spred,nomsg,gensg,case|okta \
mánná))£(v,v,sg3prs,pl3prs,agr|lea okta mánná)'
        want = [u'(leat (okta máná)',
                u'£(n,spred,nomsg,gensg,case|okta mánná)',
                u')',
                u'£(v,v,sg3prs,pl3prs,agr|lea okta mánná)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text28(self):
        text = u'heaitit dáhkaluddame$(verb,a|dahkaluddame) ahte sis \
máhkaš¢(adv,á|mahkáš) livččii makkarge$(adv,á|makkárge) politihkka, muhto \
rahpasit baicca muitalivčče (makkar$(interr,á|makkár) soga)€(man soga) sii \
ovddasttit$(verb,conc|ovddastit).'
        want = [u'heaitit dáhkaluddame',
                u'$(verb,a|dahkaluddame)',
                u' ahte sis máhkaš',
                u'¢(adv,á|mahkáš)',
                u' livččii makkarge',
                u'$(adv,á|makkárge)',
                u' politihkka, muhto rahpasit baicca muitalivčče (makkar',
                u'$(interr,á|makkár)',
                u' soga)',
                u'€(man soga)',
                u' sii ovddasttit',
                u'$(verb,conc|ovddastit)',
                u'.']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text31(self):
        text = u'(Ovddit geasis)£(noun,advl,gensg,locsg,case|Ovddit geasi) \
((čoaggen$(verb,mono|čoggen) ollu jokŋat)£(noun,obj,genpl,nompl,case|čoggen \
ollu joŋaid) ja sarridat)£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja \
sarridiid)'
        want = [
            u'(Ovddit geasis)',
            u'£(noun,advl,gensg,locsg,case|Ovddit geasi)',
            u' ((čoaggen', u'$(verb,mono|čoggen)',
            u' ollu jokŋat)',
            u'£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid)',
            u' ja sarridat)',
            u'£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid)']

        self.assertEqual(self.em.process_text(text), want)

    def test_process_text32(self):
        text = u'Bruk ((epoxi)$(noun,cons|epoksy) lim)¢(noun,mix|epoksylim) \
med god kvalitet.'
        want = [u'Bruk ((epoxi)',
                u'$(noun,cons|epoksy)',
                u' lim)',
                u'¢(noun,mix|epoksylim)',
                u' med god kvalitet.']

        print self.em.process_text(text)
        self.assertEqual(self.em.process_text(text), want)

    def test_is_correction1(self):
        text = u'$(noun,cons|epoksy)'
        self.assertTrue(self.em.is_correction(text))

    def test_is_correction2(self):
        text = u'Bruk ((epoxi)'
        self.assertTrue(not self.em.is_correction(text))

    def test_is_error_with_slash(self):
        text = u'aba/'
        self.assertTrue(self.em.is_error(text))
