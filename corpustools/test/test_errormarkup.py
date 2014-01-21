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
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

        pass

    def testOnlyTextInElement(self):
        input = etree.fromstring('<p>Muittán doložiid</p>')
        want = '<p>Muittán doložiid</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorParserErrorlangInfinity(self):
        input = u'(molekylærbiologimi)∞(kal,bio)'
        want = u'<errorlang correct="kal,bio">molekylærbiologimi</errorlang>'

        got = self.em.errorParser(input)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def testErrorParserErrorlangInfinityWithNewLines(self):
        input = u'\n\n\n\n(molekylærbiologimi)∞(kal,bio)\n\n\n\n'
        want = u'<errorlang correct="kal,bio">molekylærbiologimi</errorlang>'

        got = self.em.errorParser(input)
        self.assertEqual(len(got), 2)
        self.assertXmlEqual(etree.tostring(got[1]), want)

    def testQuoteChar(self):
        input = u'”sjievnnijis”$(conc,vnn-vnnj|sjievnnjis)'
        want = u'<errorort errorinfo="conc,vnn-vnnj" correct="sjievnnjis">”sjievnnijis”</errorort>'

        got = self.em.errorParser(input)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def testParagraphCharacter(self):
        input = etree.fromstring('<p>Vuodoláhkaj §110a</p>')
        want = u'<p>Vuodoláhkaj §110a</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorParserErrorort1(self):
        input = u'jne.$(adv,typo|jna.)'
        want = u'<errorort errorinfo="adv,typo" correct="jna.">jne.</errorort>'

        got = self.em.errorParser(input)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def testErrorort1(self):
        input = etree.fromstring('<p>jne.$(adv,typo|jna.)</p>')
        want = '<p><errorort errorinfo="adv,typo" correct="jna.">jne.</errorort></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorort2(self):
        input = etree.fromstring('<p>daesn\'$daesnie</p>')
        want = '<p><errorort correct="daesnie">daesn\'</errorort></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testInputContainsSlash(self):
        input = etree.fromstring('<p>magistter/$(loan,vowlat,e-a|magisttar)</p>')
        want = '<p><errorort correct="magisttar" errorinfo="loan,vowlat,e-a">magistter/</errorort></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect1(self):
        input = etree.fromstring('<p>1]§Ij</p>')
        want = '<p><error correct="Ij">1]</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect2(self):
        input = etree.fromstring('<p>væ]keles§(væjkeles)</p>')
        want = '<p><error correct="væjkeles">væ]keles</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect3(self):
        input = etree.fromstring('<p>smávi-§smávit-</p>')
        want = '<p><error correct="smávit-">smávi-</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect4(self):
        input = etree.fromstring('<p>CD:t§CD:at</p>')
        want = '<p><error correct="CD:at">CD:t</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect5(self):
        input = etree.fromstring('<p>DNB-feaskáris§(DnB-feaskáris)</p>')
        want = '<p><error correct="DnB-feaskáris">DNB-feaskáris</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect6(self):
        input = etree.fromstring('<p>boade§boađe</p>')
        want = '<p><error correct="boađe">boade</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect7(self):
        input = etree.fromstring('<p>2005’as§2005:s</p>')
        want = '<p><error correct="2005:s">2005’as</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect8(self):
        input = etree.fromstring('<p>NSRii§NSR:i</p>')
        want = '<p><error correct="NSR:i">NSRii</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorCorrect9(self):
        input = etree.fromstring('<p>Nordkjosbotn\'ii§Nordkjosbotnii</p>')
        want = '<p><error correct="Nordkjosbotnii">Nordkjosbotn\'ii</error></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorort3(self):
        input = etree.fromstring('<p>nourra$(a,meta|nuorra)</p>')
        want = '<p><errorort errorinfo="a,meta" correct="nuorra">nourra</errorort></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorMorphsyn1(self):
        input = etree.fromstring('<p>(Nieiddat leat nuorra)£(a,spred,nompl,nomsg,agr|Nieiddat leat nuorat)</p>')
        want = '<p><errormorphsyn errorinfo="a,spred,nompl,nomsg,agr" correct="Nieiddat leat nuorat">Nieiddat leat nuorra</errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorParserErrorMorphsyn1(self):
        input = u'(Nieiddat leat nuorra)£(a,spred,nompl,nomsg,agr|Nieiddat leat nuorat)'
        want = u'<errormorphsyn errorinfo="a,spred,nompl,nomsg,agr" correct="Nieiddat leat nuorat">Nieiddat leat nuorra</errormorphsyn>'

        got = self.em.errorParser(input)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(etree.tostring(got[0]), want)

    def testErrorSyn1(self):
        input = etree.fromstring('<p>(riŋgen nieidda lusa)¥(x,pph|riŋgen niidii)</p>')
        want = '<p><errorsyn errorinfo="x,pph" correct="riŋgen niidii">riŋgen nieidda lusa</errorsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorSyn2(self):
        input = etree.fromstring('<p>ovtta¥(num,redun| )</p>')
        want = '<p><errorsyn errorinfo="num,redun" correct=" ">ovtta</errorsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorLex1(self):
        input = etree.fromstring('<p>dábálaš€(adv,adj,der|dábálaččat)</p>')
        want = '<p><errorlex errorinfo="adv,adj,der" correct="dábálaččat">dábálaš</errorlex></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorOrtreal1(self):
        input = etree.fromstring('<p>ráhččamušaid¢(noun,mix|rahčamušaid)</p>')
        want = '<p><errorortreal errorinfo="noun,mix" correct="rahčamušaid">ráhččamušaid</errorortreal></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorOrtreal2(self):
        input = etree.fromstring('<p>gitta Nordkjosbotn\'ii$Nordkjosbotnii (mii lea ge nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos</p>')
        want = '<p>gitta <errorort correct="Nordkjosbotnii">Nordkjosbotn\'ii</errorort> (mii lea ge <errorort correct="Nordkjosbotn">nordkjosbotn</errorort> sámegillii? Muhtin, veahket mu!) gos</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorParserWithTwoSimpleErrors(self):
        input = u"gitta Nordkjosbotn'ii$Nordkjosbotnii (mii lea ge nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"
        got = self.em.errorParser(input)

        self.assertEqual(len(got), 3)
        self.assertEqual(got[0], u'gitta ')
        self.assertEqual(etree.tostring(got[1], encoding='utf8'), '<errorort correct="Nordkjosbotnii">Nordkjosbotn\'ii</errorort> (mii lea ge ')
        self.assertEqual(etree.tostring(got[2], encoding='utf8'), '<errorort correct="Nordkjosbotn">nordkjosbotn</errorort> sámegillii? Muhtin, veahket mu!) gos')


    def testErrorMorphsyn2(self):
        input = etree.fromstring('<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei maiddái ovttasbargu gaskal (skuvla ohppiid)£(noun,attr,gensg,nomsg,case|skuvlla ohppiid) ja VSM.</p>')
        want = '<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei maiddái ovttasbargu gaskal <errormorphsyn errorinfo="noun,attr,gensg,nomsg,case" correct="skuvlla ohppiid">skuvla ohppiid</errormorphsyn> ja VSM.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorort4(self):
        input = etree.fromstring('<p>- ruksesruonáčalmmehisvuohta lea sullii 8%:as$(acr,suf|8%:s)</p>')
        want = '<p>- ruksesruonáčalmmehisvuohta lea sullii <errorort correct="8%:s" errorinfo="acr,suf">8%:as</errorort></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorOrtreal3(self):
        input = etree.fromstring('<p>( nissonin¢(noun,suf|nissoniin) dušše (0.6 %:s)£(0.6 %) )</p>')
        want = '<p>( <errorortreal errorinfo="noun,suf" correct="nissoniin">nissonin</errorortreal> dušše <errormorphsyn correct="0.6 %">0.6 %:s</errormorphsyn> )</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorort5(self):
        input = etree.fromstring('<p>(haploida) ja njiŋŋalas$(noun,á|njiŋŋálas) ságahuvvon$(verb,a|sagahuvvon) manneseallas (diploida)</p>')
        want = '<p>(haploida) ja <errorort errorinfo="noun,á" correct="njiŋŋálas">njiŋŋalas</errorort> <errorort errorinfo="verb,a" correct="sagahuvvon">ságahuvvon</errorort> manneseallas (diploida)</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testErrorort6(self):
        input = etree.fromstring('<p>(gii oahpaha) giinu$(x,notcmp|gii nu) manai intiánalávlagat$(loan,conc|indiánalávlagat) (guovža-klána)$(noun,cmp|guovžaklána) olbmuid</p>')
        want = '<p>(gii oahpaha) <errorort errorinfo="x,notcmp" correct="gii nu">giinu</errorort> manai <errorort errorinfo="loan,conc" correct="indiánalávlagat">intiánalávlagat</errorort> <errorort errorinfo="noun,cmp" correct="guovžaklána">guovža-klána</errorort> olbmuid</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testPreserveSpaceAtEndOfSentence(self):
        input = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. </p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. </p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)

    def testPlaceErrorElementsBeforeOldElement1(self):
        '''Test if errorlements are inserted before the span element.
        '''
        input = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)

    def testPlaceErrorElementsBeforeOldElement2(self):
        '''Test if errorlements are inserted before the span element.
        '''
        input = etree.fromstring('<p>Mikkelsens$(typo|Mikkelsen) lea ráhkadan. bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>')

        want = '<p><errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)

    def testPlaceErrorElementAfterOldElement(self):
        input = etree.fromstring('<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">"Fornuftigt Madstel"</span>. Asbjørsen$(prop,typo|Asbjørnsen) døde 5. januar 1885, nesten 73 år gammel.</p>')

        want = '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">"Fornuftigt Madstel"</span>. <errorort correct="Asbjørnsen" errorinfo="prop,typo">Asbjørsen</errorort> døde 5. januar 1885, nesten 73 år gammel.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)


    def testPlaceErrorElementBeforeAndAfterOldElement(self):
        '''The input:
        buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. «Best Shorts Competition» bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.<errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan.</p>
        '''
        input = etree.fromstring('<p>buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.</p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)

    def testAddErrorMarkup3Levels(self):
        '''The input:
        buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. «Best Shorts Competition» bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.<errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan.</p>
        '''
        input = etree.fromstring('<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu. <em>buvttadeaddji Anstein Mikkelsens$(typo|Mikkelsen) lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> bálkkášumi$(vowlat,á-a|bálkkašumi) miessemánu.</em></p>')

        want = '<p>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu. <em>buvttadeaddji Anstein <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort> lea ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span> <errorort correct="bálkkašumi" errorinfo="vowlat,á-a">bálkkášumi</errorort> miessemánu.</em></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertEqual(got, want)

    #Nested markup
    def testNestedMarkup1(self):
        input = etree.fromstring('<p>(šaddai$(verb,conc|šattai) ollu áššit)£(verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit)</p>')
        want = '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,tense" correct="šadde ollu áššit"><errorort errorinfo="verb,conc" correct="šattai">šaddai</errorort> ollu áššit</errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup2(self):
        input = etree.fromstring('<p>(guokte ganddat§(n,á|gánddat))£(n,nump,gensg,nompl,case|guokte gándda)</p>')
        want = '<p><errormorphsyn errorinfo="n,nump,gensg,nompl,case" correct="guokte gándda">guokte <error errorinfo="n,á" correct="gánddat">ganddat</error></errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup3(self):
        input = etree.fromstring('<p>(Nieiddat leat nourra$(adj,meta|nuorra))£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)</p>')
        want = '<p><errormorphsyn errorinfo="adj,spred,nompl,nomsg,agr" correct="Nieiddat leat nuorat">Nieiddat leat <errorort errorinfo="adj,meta" correct="nuorra">nourra</errorort></errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup4(self):
        input = etree.fromstring('<p>(leat (okta máná)£(n,spred,nomsg,gensg,case|okta mánná))£(v,v,sg3prs,pl3prs,agr|lea okta mánná)</p>')
        want = '<p><errormorphsyn errorinfo="v,v,sg3prs,pl3prs,agr" correct="lea okta mánná">leat <errormorphsyn errorinfo="n,spred,nomsg,gensg,case" correct="okta mánná">okta máná</errormorphsyn></errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup5(self):
        input = etree.fromstring('<p>heaitit dáhkaluddame$(verb,a|dahkaluddame) ahte sis máhkaš¢(adv,á|mahkáš) livččii makkarge$(adv,á|makkárge) politihkka, muhto rahpasit baicca muitalivčče (makkar$(interr,á|makkár) soga)€(man soga) sii ovddasttit$(verb,conc|ovddastit).</p>')
        want = '<p>heaitit <errorort correct="dahkaluddame" errorinfo="verb,a">dáhkaluddame</errorort> ahte sis <errorortreal correct="mahkáš" errorinfo="adv,á">máhkaš</errorortreal> livččii <errorort correct="makkárge" errorinfo="adv,á">makkarge</errorort> politihkka, muhto rahpasit baicca muitalivčče <errorlex correct="man soga"><errorort correct="makkár" errorinfo="interr,á">makkar</errorort> soga</errorlex> sii <errorort correct="ovddastit" errorinfo="verb,conc">ovddasttit</errorort>.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testProcessText29(self):
        text = u'(Bearpmahat$(noun,svow|Bearpmehat) earuha€(verb,v,w|sirre))£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit) uskki ja loaiddu.'
        want = [u'(Bearpmahat', u'$(noun,svow|Bearpmehat)', u' earuha', u'€(verb,v,w|sirre)', u')', u'£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit)', u' uskki ja loaiddu.']

        self.assertEqual(self.em.processText(text), want)

    def testNestedMarkup6(self):
        input = etree.fromstring('<p>(Bearpmahat$(noun,svow|Bearpmehat) earuha€(verb,v,w|sirre))£(verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit) uskki ja loaiddu.</p>')
        want = '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,agr" correct="Bearpmehat sirrejit"><errorort errorinfo="noun,svow" correct="Bearpmehat">Bearpmahat</errorort> <errorlex errorinfo="verb,v,w" correct="sirre">earuha</errorlex></errormorphsyn> uskki ja loaiddu.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testProcessText30(self):
        text = u'Mirja ja Line leaba (gulahallan olbmožat)¢(noun,cmp|gulahallanolbmožat)€gulahallanolbmot'
        want = [u'Mirja ja Line leaba (gulahallan olbmožat)', u'¢(noun,cmp|gulahallanolbmožat)', u'€gulahallanolbmot']

        self.assertEqual(self.em.processText(text), want)

    def testNestedMarkup7(self):
        input = etree.fromstring('<p>Mirja ja Line leaba (gulahallan olbmožat)¢(noun,cmp|gulahallanolbmožat)€gulahallanolbmot</p>')
        want = '<p>Mirja ja Line leaba <errorlex correct="gulahallanolbmot"><errorortreal errorinfo="noun,cmp" correct="gulahallanolbmožat">gulahallan olbmožat</errorortreal></errorlex></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup8(self):
        input = etree.fromstring('<p>(Ovddit geasis)£(noun,advl,gensg,locsg,case|Ovddit geasi) ((čoaggen$(verb,mono|čoggen) ollu jokŋat)£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid) ja sarridat)£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid)</p>')
        want = '<p><errormorphsyn errorinfo="noun,advl,gensg,locsg,case" correct="Ovddit geasi">Ovddit geasis</errormorphsyn> <errormorphsyn errorinfo="noun,obj,genpl,nompl,case" correct="čoggen ollu joŋaid ja sarridiid"><errormorphsyn errorinfo="noun,obj,genpl,nompl,case" correct="čoggen ollu joŋaid"><errorort errorinfo="verb,mono" correct="čoggen">čoaggen</errorort> ollu jokŋat</errormorphsyn> ja sarridat</errormorphsyn></p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testNestedMarkup9(self):
        input = etree.fromstring('<p>Bruk ((epoxi)$(noun,cons|epoksy) lim)¢(noun,mix|epoksylim) med god kvalitet.</p>')
        want = '<p>Bruk <errorortreal errorinfo="noun,mix" correct="epoksylim"><errorort errorinfo="noun,cons" correct="epoksy">epoxi</errorort> lim</errorortreal> med god kvalitet.</p>'

        self.em.addErrorMarkup(input)
        got = etree.tostring(input, encoding = 'utf8')
        self.assertXmlEqual(got, want)

    def testProcessText1(self):
        text = u'jne.$(adv,typo|jna.)'
        want = [u'jne.', u'$(adv,typo|jna.)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText2(self):
        text = u"daesn'$daesnie"
        want = [u"daesn'", "$daesnie"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText3(self):
        text = u"1]§Ij"
        want = [u"1]", u"§Ij"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText4(self):
        text = u"væ]keles§(væjkeles)"
        want = [u"væ]keles", u"§(væjkeles)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText5(self):
        text = u"smávi-§smávit-"
        want = [u"smávi-", u"§smávit-"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText6(self):
        text = u"CD:t§CD:at"
        want = [u"CD:t", u"§CD:at"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText7(self):
        text = u"DNB-feaskáris§(DnB-feaskáris)"
        want = [u"DNB-feaskáris", u"§(DnB-feaskáris)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText8(self):
        text = u"boade§boađe"
        want = [u"boade", u"§boađe"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText9(self):
        text = u"2005’as§2005:s"
        want = [u"2005’as", u"§2005:s"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText10(self):
        text = u"NSRii§NSR:ii"
        want = [u"NSRii", u"§NSR:ii"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText11(self):
        text = u"Nordkjosbotn'ii§Nordkjosbotnii"
        want = [u"Nordkjosbotn'ii", u"§Nordkjosbotnii"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText12(self):
        text = u"nourra$(a,meta|nuorra)"
        want = [u"nourra", u"$(a,meta|nuorra)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText13(self):
        text = u"(Nieiddat leat nuorra)£(a,spred,nompl,nomsg,agr|Nieiddat leat nuorat)"
        want = [u"(Nieiddat leat nuorra)", u"£(a,spred,nompl,nomsg,agr|Nieiddat leat nuorat)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText14(self):
        text = u"(riŋgen nieidda lusa)¥(x,pph|riŋgen niidii)"
        want = [u"(riŋgen nieidda lusa)", u"¥(x,pph|riŋgen niidii)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText15(self):
        text = u"ovtta¥(num,redun| )"
        want = [u"ovtta", u"¥(num,redun| )"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText16(self):
        text = u"dábálaš€(adv,adj,der|dábálaččat)"
        want = [u"dábálaš", u"€(adv,adj,der|dábálaččat)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText17(self):
        text = u"ráhččamušaid¢(noun,mix|rahčamušaid)"
        want = [u"ráhččamušaid", u"¢(noun,mix|rahčamušaid)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText18(self):
        text = u"gitta Nordkjosbotn'ii$Nordkjosbotnii (mii lea ge nordkjosbotn$Nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"
        want = [u"gitta Nordkjosbotn'ii", u"$Nordkjosbotnii", u" (mii lea ge nordkjosbotn", u"$Nordkjosbotn", u" sámegillii? Muhtin, veahket mu!) gos"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText19(self):
        text = u"Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei maiddái ovttasbargu gaskal (skuvla ohppiid)£(noun,attr,gensg,nomsg,case|skuvlla ohppiid) ja VSM."
        want = [u"Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei maiddái ovttasbargu gaskal (skuvla ohppiid)", u"£(noun,attr,gensg,nomsg,case|skuvlla ohppiid)", u" ja VSM."]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText20(self):
        text = u"- ruksesruonáčalmmehisvuohta lea sullii 8%:as$(acr,suf|8%:s)"
        want = [u"- ruksesruonáčalmmehisvuohta lea sullii 8%:as", u"$(acr,suf|8%:s)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText21(self):
        text = u"( nissonin¢(noun,suf|nissoniin) dušše (0.6 %:s)£(0.6 %) )"
        want = [u"( nissonin", u"¢(noun,suf|nissoniin)", u" dušše (0.6 %:s)", u"£(0.6 %)", u" )"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText22(self):
        text = u"(haploida) ja njiŋŋalas$(noun,á|njiŋŋálas) ságahuvvon$(verb,a|sagahuvvon) manneseallas (diploida)"
        want = [u"(haploida) ja njiŋŋalas", u"$(noun,á|njiŋŋálas)", u" ságahuvvon", u"$(verb,a|sagahuvvon)", u" manneseallas (diploida)"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText23(self):
        text = u"(gii oahpaha) giinu$(x,notcmp|gii nu) manai intiánalávlagat$(loan,conc|indiánalávlagat) (guovža-klána)$(noun,cmp|guovžaklána) olbmuid"
        want = [u"(gii oahpaha) giinu", "$(x,notcmp|gii nu)", u" manai intiánalávlagat", u"$(loan,conc|indiánalávlagat)", u" (guovža-klána)", u"$(noun,cmp|guovžaklána)", u" olbmuid"]

        self.assertEqual(self.em.processText(text), want)

    def testProcessText24(self):
        text = u'(šaddai$(verb,conc|šattai) ollu áššit)£(verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit)'
        want = [u'(šaddai', u"$(verb,conc|šattai)", u" ollu áššit)", u'£(verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText25(self):
        text = u'(guokte ganddat§(n,á|gánddat))£(n,nump,gensg,nompl,case|guokte gándda)'
        want = [u'(guokte ganddat', u'§(n,á|gánddat)', u')', u'£(n,nump,gensg,nompl,case|guokte gándda)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText26(self):
        text = u'(Nieiddat leat nourra$(adj,meta|nuorra))£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)'
        want = [u'(Nieiddat leat nourra', u'$(adj,meta|nuorra)', u')', u'£(adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText27(self):
        text = u'(leat (okta máná)£(n,spred,nomsg,gensg,case|okta mánná))£(v,v,sg3prs,pl3prs,agr|lea okta mánná)'
        want = [u'(leat (okta máná)', u'£(n,spred,nomsg,gensg,case|okta mánná)', u')', u'£(v,v,sg3prs,pl3prs,agr|lea okta mánná)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText28(self):
        text = u'heaitit dáhkaluddame$(verb,a|dahkaluddame) ahte sis máhkaš¢(adv,á|mahkáš) livččii makkarge$(adv,á|makkárge) politihkka, muhto rahpasit baicca muitalivčče (makkar$(interr,á|makkár) soga)€(man soga) sii ovddasttit$(verb,conc|ovddastit).'
        want = [u'heaitit dáhkaluddame', u'$(verb,a|dahkaluddame)', u' ahte sis máhkaš', u'¢(adv,á|mahkáš)', u' livččii makkarge', u'$(adv,á|makkárge)', u' politihkka, muhto rahpasit baicca muitalivčče (makkar', u'$(interr,á|makkár)', u' soga)', u'€(man soga)', u' sii ovddasttit', u'$(verb,conc|ovddastit)', u'.']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText31(self):
        text = u'(Ovddit geasis)£(noun,advl,gensg,locsg,case|Ovddit geasi) ((čoaggen$(verb,mono|čoggen) ollu jokŋat)£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid) ja sarridat)£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid)'
        want = [u'(Ovddit geasis)', u'£(noun,advl,gensg,locsg,case|Ovddit geasi)', u' ((čoaggen', u'$(verb,mono|čoggen)', u' ollu jokŋat)', u'£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid)', u' ja sarridat)', u'£(noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid)']

        self.assertEqual(self.em.processText(text), want)

    def testProcessText32(self):
        text = u'Bruk ((epoxi)$(noun,cons|epoksy) lim)¢(noun,mix|epoksylim) med god kvalitet.'
        want = [u'Bruk ((epoxi)', u'$(noun,cons|epoksy)', u' lim)', u'¢(noun,mix|epoksylim)', u' med god kvalitet.']

        print self.em.processText(text)
        self.assertEqual(self.em.processText(text), want)

    def testIsCorrection1(self):
        text = u'$(noun,cons|epoksy)'
        self.assertTrue(self.em.isCorrection(text))

    def testIsCorrection2(self):
        text = u'Bruk ((epoxi)'
        self.assertTrue(not self.em.isCorrection(text))

    def testIsErrorWithSlash(self):
        text = u'aba/'
        self.assertTrue(self.em.isError(text))
