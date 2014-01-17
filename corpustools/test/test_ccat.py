# -*- coding:utf-8 -*-

from corpustools import ccat
import unittest
from lxml import etree
import io
import cStringIO
import os

class TestCcat(unittest.TestCase):
    def test_single_error_inline(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        input_error = etree.fromstring('''
<errorortreal correct="fiskeleting" errtype="nosplit" pos="noun">
    fiske leting
</errorortreal>''')

        textlist = []
        xml_printer.collect_inline_errors(input_error, textlist, 'nob')

        self.assertEqual('\n'.join(textlist), 'fiskeleting')

    def test_single_error_not_inline(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        input_error = etree.fromstring('''
<errorortreal correct="fiskeleting" errtype="nosplit" pos="noun">
    fiske leting
</errorortreal>''')

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t#errtype=nosplit,pos=noun')

    def test_single_error_not_inline_with_filename(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(print_filename=True)
        input_error = etree.fromstring('''
<errorortreal correct="fiskeleting" errtype="nosplit" pos="noun">
    fiske leting
</errorortreal>''')

        xml_printer.filename = 'p.xml'

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t\
#errtype=nosplit,pos=noun, file: p.xml')

    def test_single_error_not_inline_with_filename_without_attributes(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(print_filename=True)
        input_error = etree.fromstring('''
<errorortreal correct="fiskeleting">fiske leting</errorortreal>
''')

        xml_printer.filename = 'p.xml'

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t#file: p.xml')

    def test_multi_error_in_line(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(print_filename=True)

        input_error = etree.fromstring('''
<errormorphsyn cat="x" const="spred" correct="skoledagene er så vanskelige"
errtype="agr" orig="x" pos="adj">
    skoledagene er så
    <errorort correct="vanskelig" errtype="nosilent" pos="adj">
        vanskerlig
    </errorort>
</errormorphsyn>
''')
        textlist = []
        xml_printer.collect_inline_errors(input_error, textlist, 'nob')

        self.assertEqual('\n'.join(textlist),
                         u'skoledagene er så vanskelige')

    def test_multi_errormorphsyn_not_inline_with_filename(self):
        '''
        '''
        input_error = etree.fromstring('''
<errormorphsyn cat="x" const="spred" correct="skoledagene er så vanskelige"
errtype="agr" orig="x" pos="adj">
    skoledagene er så
    <errorort correct="vanskelig" errtype="nosilent" pos="adj">
        vanskerlig
    </errorort>
</errormorphsyn>
''')

        xml_printer = ccat.XMLPrinter(one_word_per_line=True,
                                      print_filename=True)
        xml_printer.filename = 'p.xml'

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         u'skoledagene er så vanskelig\t\
skoledagene er så vanskelige\t\
#cat=x,const=spred,errtype=agr,orig=x,pos=adj, file: p.xml\n\
vanskerlig\tvanskelig\t#errtype=nosilent,pos=adj, file: p.xml')

    def test_multi_errorlex_not_inline(self):
        '''
        '''
        input_error = etree.fromstring('''
<errorlex correct="man soga"><errorort correct="makkár" errtype="á" pos="interr">makkar</errorort> soga</errorlex>
''')
        textlist = []

        xml_printer = ccat.XMLPrinter(typos=True)
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         u'''makkár soga\tman soga
makkar\tmakkár\t#errtype=á,pos=interr''')

    def test_p(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()
        input_p = etree.fromstring('''
<p>Et stykke av Norge som er lite kjent - Litt om Norge i mellomkrigstiden</p>
''')

        xml_printer.collect_text(input_p, 'nob', buffer)
        self.assertEqual(buffer.getvalue(),
                         'Et stykke av Norge som er lite kjent - \
Litt om Norge i mellomkrigstiden ¶\n')

    def test_p_with_span(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()

        input_p = etree.fromstring('''
<p>I 1864 ga han ut boka <span type="quote" xml:lang="dan">"Fornuftigt Madstel"</span>.</p>
''')

        xml_printer.collect_text(input_p, 'nob', buffer)
        self.assertEqual(buffer.getvalue(),
                         'I 1864 ga han ut boka "Fornuftigt Madstel" . ¶\n')

    def test_p_with_error(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()

        input_p = etree.fromstring('''
<p><errormorphsyn cat="pl3prs" const="fin" correct="Bearpmehat sirrejit" errtype="agr" orig="sg3prs" pos="verb"><errorort correct="Bearpmehat" errtype="svow" pos="noun">Bearpmahat</errorort> <errorlex correct="sirre" errtype="w" origpos="v" pos="verb">earuha</errorlex></errormorphsyn> uskki ja loaiddu.</p>
''')

        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "Bearpmahat earuha uskki ja loaiddu. ¶\n")

    def test_p_one_word_per_line(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>Et stykke av Norge som er lite kjent - Litt om Norge i mellomkrigstiden</p>
''')

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)

        buffer = cStringIO.StringIO()

        xml_printer.collect_text(input_p, 'nob', buffer)
        self.assertEqual(buffer.getvalue(),
                         '''Et
stykke
av
Norge
som
er
lite
kjent
-
Litt
om
Norge
i
mellomkrigstiden
''')

    def test_p_with_span_one_word_per_line(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>I 1864 ga han ut boka <span type="quote" xml:lang="dan">"Fornuftigt Madstel"</span>.</p>
''')

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)
        buffer = cStringIO.StringIO()

        xml_printer.collect_text(input_p, 'nob', buffer)
        self.assertEqual(buffer.getvalue(),
                         '''I
1864
ga
han
ut
boka
\"Fornuftigt
Madstel\"
.
''')

    def test_p_with_error_one_word_per_line(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)

        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         '''livččii
makkarge\tmakkárge\t#errtype=á,pos=adv
politihkka,
muhto
rahpasit
baicca
muitalivčče
makkár soga\tman soga
makkar\tmakkár\t#errtype=á,pos=interr
soga
sii
''')

    def test_p_with_error_correction(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')

        xml_printer = ccat.XMLPrinter(correction=True)

        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "livččii makkárge politihkka, muhto rahpasit baicca \
muitalivčče man soga sii ¶\n")

    def test_p_with_error_filtering_errorlex(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')

        xml_printer = ccat.XMLPrinter(errorlex=True)

        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "livččii makkarge politihkka, muhto rahpasit baicca \
muitalivčče man soga sii ¶\n")

    def test_p_with_error_filtering_errormorphsyn(self):
        '''
        '''
        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')

        xml_printer = ccat.XMLPrinter(errormorphsyn=True)

        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "livččii makkarge politihkka, muhto rahpasit baicca \
muitalivčče makkar soga sii ¶\n")

    def test_p_with_error_filtering_errorort(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(errorort=True)

        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')


        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "livččii makkárge politihkka, muhto rahpasit baicca \
muitalivčče makkár soga sii ¶\n")

    def test_p_with_error_filtering_errorortreal(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(errorortreal=True)

        input_p = etree.fromstring('''
<p>livččii
    <errorort correct="makkárge" errtype="á" pos="adv">
        makkarge
    </errorort>
    politihkka, muhto rahpasit baicca muitalivčče
    <errorlex correct="man soga">
        <errorort correct="makkár" errtype="á" pos="interr">
            makkar
        </errorort>
        soga
    </errorlex>
    sii
</p>
''')

        buffer = cStringIO.StringIO()
        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "livččii makkarge politihkka, muhto rahpasit baicca \
muitalivčče makkar soga sii ¶\n")

    def test_visit_this_p_default(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()

        for types in [' type="title"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in ['',
                      ' type="text"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_title_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(title=True)

        for types in ['',
                      ' type="text"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="title"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_listitem_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(listitem=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="tablecell"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="listitem"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_tablecell_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(table=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="listitem"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="tablecell"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_allp_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(all_paragraphs=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            input_xml = etree.fromstring('<p' + types + '>ášŧŋđžčøåæ</p>')
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_process_file_default(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()

        for types in [' type="title"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), '')

        for types in ['',
                      ' type="text"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))


            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_title_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(title=True)

        for types in ['',
                      ' type="text"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))


            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="title"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_listitem_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(listitem=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="listitem"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_tablecell_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(table=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="listitem"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_allp_set(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(all_paragraphs=True)

        for types in ['',
                      ' type="text"',
                      ' type="title"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file('barabbas/p.xml')
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_one_word_per_line_errorlex(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(one_word_per_line=True,
                            errorlex=True)

        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="sme">
    <body>
        <p>
            livččii
            <errorort correct="makkárge" errtype="á" pos="adv">
                makkarge
            </errorort>
            politihkka, muhto rahpasit baicca muitalivčče
            <errorlex correct="man soga">
                <errorort correct="makkár" errtype="á" pos="interr">
                    makkar
                </errorort>
                soga
            </errorlex>
            sii
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(), '''livččii
makkarge
politihkka,
muhto
rahpasit
baicca
muitalivčče
makkár soga\tman soga
sii
''')

    def test_process_file_one_word_per_line_errorort(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(one_word_per_line=True,
                            errorort=True)

        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="sme">
    <body>
        <p>
            livččii
            <errorort correct="makkárge" errtype="á" pos="adv">
                makkarge
            </errorort>
            politihkka, muhto rahpasit baicca muitalivčče
            <errorlex correct="man soga">
                <errorort correct="makkár" errtype="á" pos="interr">
                    makkar
                </errorort>
                soga
            </errorlex>
            sii
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(), '''livččii
makkarge\tmakkárge\t#errtype=á,pos=adv
politihkka,
muhto
rahpasit
baicca
muitalivčče
makkar\tmakkár\t#errtype=á,pos=interr
soga
sii
''')

    def test_process_file_typos(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(typos=True)

        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="sme">
    <body>
        <p>
            livččii
            <errorort correct="makkárge" errtype="á" pos="adv">
                makkarge
            </errorort>
            politihkka, muhto rahpasit baicca muitalivčče
            <errorlex correct="man soga">
                <errorort correct="makkár" errtype="á" pos="interr">
                    makkar
                </errorort>
                soga
            </errorlex>
            sii
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(),
                         '''makkarge\tmakkárge\t#errtype=á,pos=adv
makkár soga\tman soga
makkar\tmakkár\t#errtype=á,pos=interr
''')

    def test_process_file_typos_errorlex(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(     typos=True,
                            errorlex=True)

        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="sme">
    <body>
        <p>
            livččii
            <errorort correct="makkárge" errtype="á" pos="adv">
                makkarge
            </errorort>
            politihkka, muhto rahpasit baicca muitalivčče
            <errorlex correct="man soga">
                <errorort correct="makkár" errtype="á" pos="interr">
                    makkar
                </errorort>
                soga
            </errorlex>
            sii
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(),
                         'makkár soga\tman soga\n')

    def test_process_file_typos_errorort(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(     typos=True,
                            one_word_per_line=True,
                            errorort=True)

        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="sme">
    <body>
        <p>
            livččii
            <errorort correct="makkárge" errtype="á" pos="adv">
                makkarge
            </errorort>
            politihkka, muhto rahpasit baicca muitalivčče
            <errorlex correct="man soga">
                <errorort correct="makkár" errtype="á" pos="interr">
                    makkar
                </errorort>
                soga
            </errorlex>
            sii
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(),
                         '''makkarge\tmakkárge\t#errtype=á,pos=adv
makkar\tmakkár\t#errtype=á,pos=interr
''')

    def test_get_lang(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        xml_printer.etree = etree.parse(io.BytesIO(
            '''<document id="no_id" xml:lang="sme"/>'''))

        self.assertEqual(xml_printer.get_lang(),  'sme')

    def test_get_element_language_same_as_parent(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring('<p/>')
        self.assertEqual(xml_printer.get_element_language(element, 'sme'),
                         'sme')

    def test_get_element_language_different_from_parent(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring('<p xml:lang="nob"/>')
        self.assertEqual(xml_printer.get_element_language(element, 'sme'),
                         'nob')

    def test_process_file_language_nob(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(lang='nob')
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            nob1
            <span type="quote" xml:lang="dan">
                dan1
            </span>
            nob2
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(), 'nob1 nob2 ¶\n')

    def test_process_file_language_dan(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(lang='dan')
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            nob1
            <span type="quote" xml:lang="dan">
                dan1
            </span>
            nob2
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(), 'dan1 ¶\n')

    def test_process_two_paragraphs(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            nob1
        </p>
        <p>
            nob2
        </p>
    </body>
</document>'''))


        buffer = xml_printer.process_file('barabbas/p.xml')
        self.assertEqual(buffer.getvalue(), 'nob1 ¶\nnob2 ¶\n')

    def test_process_minus_l_sme(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(lang='sme')
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p type="text">
            men
            <errormorphsyn cat="x" const="spred"
            correct="skoledagene er så vanskelige" errtype="agr" orig="x"
            pos="adj">
                skoledagene er så
                <errorort correct="vanskelig" errtype="nosilent" pos="adj">
                    vanskerlig
                </errorort>
            </errormorphsyn>
            å komme igjennom,
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(), '')

    def test_foreign(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(errorlang=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            Vijmak bierjjedak!
            <errorlang correct="nor">
                Pjuh
            </errorlang>
            vijmak de bierjjedak
            <errorort correct="sjattaj" errorinfo="vowlat,á-a">
                sjattáj
            </errorort>
            .
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(),
                         'Vijmak bierjjedak! nor vijmak de bierjjedak sjattáj \
. ¶\n')

    def test_no_foreign(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(noforeign=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            Vijmak bierjjedak!
            <errorlang correct="nor">
                Pjuh
            </errorlang>
            vijmak de bierjjedak
            <errorort correct="sjattaj" errorinfo="vowlat,á-a">
                sjattáj
            </errorort>
            .
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(),
                         'Vijmak bierjjedak! vijmak de bierjjedak sjattáj . \
¶\n')

    def test_no_foreign_typos(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(noforeign=True, typos=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            Vijmak bierjjedak!
            <errorlang correct="nor">
                Pjuh
            </errorlang>
            vijmak de bierjjedak
            <errorort correct="sjattaj" errorinfo="vowlat,á-a">
                sjattáj
            </errorort>.
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(), '')

    def test_typos_errordepth3(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(typos=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            <errormorphsyn cat="genpl" const="obj"
            correct="čoggen ollu joŋaid ja sarridiid" errtype="case"
            orig="nompl" pos="noun">
                <errormorphsyn cat="genpl" const="obj"
                correct="čoggen ollu joŋaid" errtype="case"
                orig="nompl" pos="noun">
                    <errorort correct="čoggen" errtype="mono" pos="verb">
                        čoaggen
                    </errorort>
                    ollu jokŋat
                </errormorphsyn>
                ja sarridat
            </errormorphsyn>
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(),
                         'čoggen ollu joŋaid ja sarridat\t\
čoggen ollu joŋaid ja sarridiid\t\
#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n\
čoggen ollu jokŋat\tčoggen ollu joŋaid\t\
#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n\
čoaggen\tčoggen\t#errtype=mono,pos=verb\n')

    def test_typos_errormorphsyn_twice(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter(typos=True, errormorphsyn=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <p>
            <errormorphsyn cat="sg3prs" const="v" correct="lea okta mánná"
            errtype="agr" orig="pl3prs" pos="v">
                leat
                <errormorphsyn cat="nomsg" const="spred" correct="okta mánná"
                errtype="case" orig="gensg" pos="n">
                    okta máná
                </errormorphsyn>
            </errormorphsyn>
        </p>
    </body>
</document>'''))

        buffer = xml_printer.process_file('barabbas/p.xml')

        self.assertEqual(buffer.getvalue(),
'''leat okta mánná\tlea okta mánná\t\
#cat=sg3prs,const=v,errtype=agr,orig=pl3prs,pos=v
okta máná\tokta mánná\t#cat=nomsg,const=spred,errtype=case,orig=gensg,pos=n
''')

    def test_set_outfile_string(self):
        '''
        '''
        xml_printer = ccat.XMLPrinter()
        xml_printer.set_outfile('abc.xml')

        self.assertTrue(os.path.exists('abc.xml'))
        os.remove('abc.xml')
