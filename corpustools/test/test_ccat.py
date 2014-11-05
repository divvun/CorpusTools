# -*- coding:utf-8 -*-

from corpustools import ccat
import unittest
from lxml import etree
import io
import cStringIO


class TestCcatHyph(unittest.TestCase):
    '''Test how ccat handles hyph
    '''
    def test_hyph1(self):
        '''Test the default treatment of hyph tags
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()
        xml_printer.etree = etree.parse(io.BytesIO(
'''<document id="no_id" xml:lang="nob"><body>
<p>mellom<hyph/>krigs<hyph/>tiden</p>
</body></document>'''))

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'mellomkrigstiden ¶\n')

    def test_hyph2(self):
        '''Test the treatment of hyph tags when hyph_replacement is
        set to "xml"
        '''
        xml_printer = ccat.XMLPrinter(hyph_replacement='xml')
        buffer = cStringIO.StringIO()
        xml_printer.etree = etree.parse(io.BytesIO(
'''<document id="no_id" xml:lang="nob"><body>
<p>mellom<hyph/>krigs<hyph/>tiden</p>
</body></document>'''))

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'mellom<hyph/>krigs<hyph/>tiden ¶\n')

    def test_hyph3(self):
        '''Test the treatment of hyph tags when hyph_replacement is
        set to "-"
        '''
        xml_printer = ccat.XMLPrinter(hyph_replacement='-')
        buffer = cStringIO.StringIO()
        xml_printer.etree = etree.parse(io.BytesIO(
'''<document id="no_id" xml:lang="nob"><body>
<p>mellom<hyph/>krigs<hyph/>tiden</p>
</body></document>'''))

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'mellom-krigs-tiden ¶\n')

    def test_hyph4(self):
        '''Test the treatment of two hyph tags in a row"
        '''
        xml_printer = ccat.XMLPrinter(hyph_replacement='-')
        buffer = cStringIO.StringIO()

        xml_printer.etree = etree.parse(io.BytesIO(
'''<document id="no_id" xml:lang="nob"><body>
<p>mellom<hyph/><hyph/>tiden</p>
</body></document>'''))

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'mellom-tiden ¶\n')

    def test_hyph5(self):
        '''Test the treatment of hyph tags when hyph_replacement is
        set to None
        '''
        xml_printer = ccat.XMLPrinter(hyph_replacement=None)
        buffer = cStringIO.StringIO()
        xml_printer.etree = etree.parse(io.BytesIO(
'''<document id="no_id" xml:lang="nob"><body>
<p>mellom<hyph/>krigs<hyph/>tiden</p>
</body></document>'''))

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'mellom krigs tiden ¶\n')


class TestCcatErrormarkup(unittest.TestCase):
    '''Test how ccat handles errormarkup
    '''
    def test_single_error_inline(self):
        '''Plain error element, default text flow
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
        '''Plain error element, one word per line output
        '''
        xml_printer = ccat.XMLPrinter()
        input_error = etree.fromstring('''<errorortreal \
            correct="fiskeleting" errtype="nosplit" pos="noun">\
            fiske leting</errorortreal>''')

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t\
#errtype=nosplit,pos=noun')

    def test_single_error_not_inline_with_filename(self):
        '''Plain error element, one word per line output, with filename
        '''
        xml_printer = ccat.XMLPrinter(print_filename=True)
        input_error = etree.fromstring('''<errorortreal \
            correct="fiskeleting" errtype="nosplit" pos="noun">\
            fiske leting</errorortreal>''')

        xml_printer.filename = 'p.xml'

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t\
#errtype=nosplit,pos=noun, file: p.xml')

    def test_single_error_not_inline_with_filename_without_attributes(self):
        '''Plain error element, one word per line output, with filename,
        only correct attribute
        '''
        xml_printer = ccat.XMLPrinter(print_filename=True)
        input_error = etree.fromstring('''<errorortreal correct="fiskeleting">\
            fiske leting</errorortreal>''')

        xml_printer.filename = 'p.xml'

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         'fiske leting\tfiskeleting\t#file: p.xml')

    def test_multi_error_in_line(self):
        '''Nested error element, default text flow
        '''
        xml_printer = ccat.XMLPrinter()

        input_error = etree.fromstring('''<errormorphsyn cat="x" \
            const="spred" correct="skoledagene er så vanskelige" \
            errtype="agr" orig="x" pos="adj">skoledagene er så\
            <errorort correct="vanskelig" errtype="nosilent" \
            pos="adj">vanskerlig</errorort></errormorphsyn>''')
        textlist = []
        xml_printer.collect_inline_errors(input_error, textlist, 'nob')

        self.assertEqual('\n'.join(textlist),
                         u'skoledagene er så vanskelige')

    def test_multi_errormorphsyn_not_inline_with_filename(self):
        '''Nested error element, one word per line output, with filename
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
        '''Nested error element, one word per line output
        '''
        input_error = etree.fromstring('''<errorlex correct="man soga">\
            <errorort correct="makkár" errtype="á" pos="interr">makkar\
            </errorort> soga</errorlex>''')
        textlist = []

        xml_printer = ccat.XMLPrinter(typos=True)
        xml_printer.collect_not_inline_errors(input_error, textlist)

        self.assertEqual('\n'.join(textlist),
                         u'''makkár soga\tman soga
makkar\tmakkár\t#errtype=á,pos=interr''')


class TestCcat(unittest.TestCase):
    def test_p(self):
        '''Test the output of a plain p with default text flow
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
        '''Test the output of a plain p with a span element with default
        text flow
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()

        input_p = etree.fromstring('''<p>I 1864 ga han ut boka \
            <span type="quote" xml:lang="dan">"Fornuftigt Madstel"</span>.\
            </p>''')

        xml_printer.collect_text(input_p, 'nob', buffer)
        self.assertEqual(buffer.getvalue(),
                         'I 1864 ga han ut boka "Fornuftigt Madstel" . ¶\n')

    def test_p_with_error(self):
        '''Test the output of a p containing a nested error element,
        with default text flow
        '''
        xml_printer = ccat.XMLPrinter()
        buffer = cStringIO.StringIO()

        input_p = etree.fromstring('''<p><errormorphsyn cat="pl3prs" \
const="fin" correct="Bearpmehat sirrejit" errtype="agr" orig="sg3prs" \
pos="verb"><errorort correct="Bearpmehat" errtype="svow" pos="noun">\
Bearpmahat</errorort> <errorlex correct="sirre" errtype="w" origpos="v" \
pos="verb">earuha</errorlex></errormorphsyn> uskki ja loaiddu.</p>''')

        xml_printer.collect_text(input_p, 'sme', buffer)
        self.assertEqual(buffer.getvalue(),
                         "Bearpmahat earuha uskki ja loaiddu. ¶\n")

    def test_p_one_word_per_line(self):
        '''Test the output of a plain p element, one word per line
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
        '''Test the output a plain p that contains a spen element,
        one word per line
        '''
        input_p = etree.fromstring('''<p>I 1864 ga han ut boka \
            <span type="quote" xml:lang="dan">"Fornuftigt Madstel"</span>.\
            </p>''')

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
        '''Test the output of a p element containing one plain and one
        nested error element
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
        '''Test the output of a plain p element containing two error elements,
        one plain and one nested, when we want to print the corrections in the
        error elements, with default text flow
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
        '''Test the output of plain p, when we only want the correction
        from the errorlex element, with the default text flow
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
        '''Test the output of a p element containing two error elements
        that are not affected by the error filtering, with default text flow.
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
        '''Test the output of a p element with two error elements,
        where errorort filtering is on. That is the correct attributes of
        the errorort elements should be printed instead of errorort.text.
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
        '''Check that only plain p elements and p elements where the
        type attribute is text is visited
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
        '''Check that only p elements where the
        type attribute is title is visited, when the title option is True
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
        '''Check that only p elements where the
        type attribute is listitem is visited, when the listitem option is True
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
        '''Check that only p elements where the
        type attribute is tablecess is visited, when the table option is
        True
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
        '''Check that all p elements are visited when the
        all_paragraphs option is True
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
        '''Check the output of plain p elements, with default settings
        Specifically, check that only plain p gets output, whereas
        p elements with the type title, listitem and tablecell get no output.
        '''
        xml_printer = ccat.XMLPrinter()

        for types in [' type="title"',
                      ' type="listitem"',
                      ' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), '')

        for types in ['',
                      ' type="text"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_title_set(self):
        '''When the title option is True, check that only p elements with
        type=title gets output.
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

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="title"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_listitem_set(self):
        '''When the listitem option is True, check that only p elements with
        type=listitem gets output.
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

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="listitem"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_tablecell_set(self):
        '''When the table option is True, check that only p elements with
        type=title gets output.
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

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), '')

        for types in [' type="tablecell"']:
            xml_printer.etree = etree.parse(io.BytesIO(
                '''<document id="no_id" xml:lang="sme"><body><p''' +
                types +
                '''>ášŧŋđžčøåæ</p></body></document>'''))

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_allp_set(self):
        '''When the all_paragraphs option is True, check that all p elements
        get output.
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

            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), 'ášŧŋđžčøåæ ¶\n')

    def test_process_file_one_word_per_line_errorlex(self):
        '''Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line and errorlex options are True.
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

        buffer = xml_printer.process_file()
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
        '''Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line and errorort options are True
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

        buffer = xml_printer.process_file()
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
        '''Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the typos option True
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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(),
                         '''makkarge\tmakkárge\t#errtype=á,pos=adv
makkár soga\tman soga
makkar\tmakkár\t#errtype=á,pos=interr
''')

    def test_process_file_typos_errorlex(self):
        '''Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the typos and errorlex options are True
        '''
        xml_printer = ccat.XMLPrinter(typos=True, errorlex=True)

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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(),
                         'makkár soga\tman soga\n')

    def test_process_file_typos_errorort(self):
        '''Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line, typos and errorort options are True
        '''
        xml_printer = ccat.XMLPrinter(typos=True,
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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(),
                         '''makkarge\tmakkárge\t#errtype=á,pos=adv
makkar\tmakkár\t#errtype=á,pos=interr
''')

    def test_get_lang(self):
        '''Check that get_lang finds the main lang of the document
        '''
        xml_printer = ccat.XMLPrinter()
        xml_printer.etree = etree.parse(io.BytesIO(
            '''<document id="no_id" xml:lang="sme"/>'''))

        self.assertEqual(xml_printer.get_lang(),  'sme')

    def test_get_element_language_same_as_parent(self):
        '''Check that get_element_language returns the same language as the
        main lang of the document when the xml:lang is not set in the p
        element.
        '''
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring('<p/>')
        self.assertEqual(xml_printer.get_element_language(element, 'sme'),
                         'sme')

    def test_get_element_language_different_from_parent(self):
        '''Check that the value of xml:lang is returned when it is set.
        '''
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring('<p xml:lang="nob"/>')
        self.assertEqual(xml_printer.get_element_language(element, 'sme'),
                         'nob')

    def test_process_file_language_nob(self):
        '''Check that only content with the same language as the lang
        options is output
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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'nob1 nob2 ¶\n')

    def test_process_file_language_dan(self):
        '''Check that only content with the same language as the lang
        options is output
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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'dan1 ¶\n')

    def test_process_two_paragraphs(self):
        '''Check that the ¶ character is printed out when the content of
        a p is output
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

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), 'nob1 ¶\nnob2 ¶\n')

    def test_process_minus_l_sme(self):
        '''Check that nothing is output when the wanted language
        (set in the lang option) is not the same language as any of the
        content of the elements.
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(), '')

    def test_foreign(self):
        '''Check the output of a p containing an errorlang element
        when the errorlang option is True.
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         'Vijmak bierjjedak! nor vijmak de bierjjedak sjattáj \
. ¶\n')

    def test_no_foreign(self):
        '''When the noforeign option is True, neither the errorlang.text
        nor the correct attribute should be output. Check that this really
        happens.
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         'Vijmak bierjjedak! vijmak de bierjjedak sjattáj . \
¶\n')

    def test_no_foreign_typos(self):
        '''When the noforeign option is True, neither the errorlang.text
        nor the correct attribute should be output. Check that this really
        happens even when the typos option is set.
        '''
        xml_printer = ccat.XMLPrinter(typos=True, noforeign=True)
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(), 'sjattáj\tsjattaj\t#errorinfo=vowlat,á-a\n')

    def test_typos_errordepth3(self):
        '''Check the output of a p containing a nested error element of
        depth 3 when the typos option is True.
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         'čoggen ollu joŋaid ja sarridat\t\
čoggen ollu joŋaid ja sarridiid\t\
#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n\
čoggen ollu jokŋat\tčoggen ollu joŋaid\t\
#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n\
čoaggen\tčoggen\t#errtype=mono,pos=verb\n')

    def test_typos_errormorphsyn_twice(self):
        '''Check the output of a plain p containing a doubly nested
        errormorphsyn element when the typos and errormorphsyn
        options are True
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

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         '''leat okta mánná\tlea okta mánná\t\
#cat=sg3prs,const=v,errtype=agr,orig=pl3prs,pos=v
okta máná\tokta mánná\t#cat=nomsg,const=spred,errtype=case,orig=gensg,pos=n
''')


    def test_process_file1(self):
        '''Test process_file with a disambiguation element as input
        '''
        xml_printer = ccat.XMLPrinter(disambiguation=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <disambiguation>"&lt;Muhto&gt;"\n\t"muhto" CC &lt;sme&gt; @CVP\n"&lt;gaskkohagaid&gt;"\n\t"gaskkohagaid" Adv &lt;sme&gt;\n"&lt;,&gt;"\n\t"," CLB\n"&lt;ja&gt;"\n\t"ja" CC &lt;sme&gt; @CNP\n"&lt;erenoamážit&gt;"\n\t"erenoamážit" Adv &lt;sme&gt;\n"&lt;dalle_go&gt;"\n\t"dalle_go" MWE CS &lt;sme&gt; @CVP\n"&lt;lei&gt;"\n\t"leat" V &lt;sme&gt; IV Ind Prt Sg3 @+FMAINV\n"&lt;buolaš&gt;"\n\t"buolaš" Sem/Wthr N &lt;sme&gt; Sg Nom\n"&lt;,&gt;"\n\t"," CLB\n"&lt;de&gt;"\n\t"de" Adv &lt;sme&gt;\n"&lt;aggregáhta&gt;"\n\t"aggregáhta" N &lt;sme&gt; Sg Nom\n"&lt;billánii&gt;"\n\t"billánit" V &lt;sme&gt; IV Ind Prt Sg3 @+FMAINV\n"&lt;.&gt;"\n\t"." CLB\n\n"&lt;¶&gt;"\n\t"¶" CLB\n\n</disambiguation></body></document>'''))

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         '"<Muhto>"\n\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n\t"gaskkohagaid" Adv <sme>\n"<,>"\n\t"," CLB\n"<ja>"\n\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n')

    def test_process_file2(self):
        '''Test process_file with a dependency element as input
        '''
        xml_printer = ccat.XMLPrinter(dependency=True)
        xml_printer.etree = etree.parse(io.BytesIO('''
<document id="no_id" xml:lang="nob">
    <body>
        <dependency>"&lt;Muhto&gt;"\n\t"muhto" CC @CVP #1-&gt;1 \n"&lt;gaskkohagaid&gt;"\n\t"gaskkohagaid" Adv @ADVL&gt; #2-&gt;12 \n"&lt;,&gt;"\n\t"," CLB #3-&gt;4 \n"&lt;ja&gt;"\n\t"ja" CC @CNP #4-&gt;2 \n"&lt;erenoamážit&gt;"\n\t"erenoamážit" Adv @ADVL&gt; #5-&gt;12 \n"&lt;dalle_go&gt;"\n\t"dalle_go" CS @CVP #6-&gt;7 \n"&lt;lei&gt;"\n\t"leat" V IV Ind Prt Sg3 @FS-ADVL&gt; #7-&gt;12 \n"&lt;buolaš&gt;"\n\t"buolaš" N Sg Nom @&lt;SPRED #8-&gt;7 \n"&lt;,&gt;"\n\t"," CLB #9-&gt;6 \n"&lt;de&gt;"\n\t"de" Adv @ADVL&gt; #10-&gt;12 \n"&lt;aggregáhta&gt;"\n\t"aggregáhta" N Sg Nom @SUBJ&gt; #11-&gt;12 \n"&lt;billánii&gt;"\n\t"billánit" V IV Ind Prt Sg3 @FS-ADVL&gt; #12-&gt;0 \n"&lt;.&gt;"\n\t"." CLB #13-&gt;12 \n\n"&lt;¶&gt;"\n\t"¶" CLB #1-&gt;1 \n\n</dependency>
    </body>
</document>'''))

        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(),
                         '"<Muhto>"\n\t"muhto" CC @CVP #1->1 \n"<gaskkohagaid>"\n\t"gaskkohagaid" Adv @ADVL> #2->12 \n"<,>"\n\t"," CLB #3->4 \n"<ja>"\n\t"ja" CC @CNP #4->2 \n"<erenoamážit>"\n\t"erenoamážit" Adv @ADVL> #5->12 \n"<dalle_go>"\n\t"dalle_go" CS @CVP #6->7 \n"<lei>"\n\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12 \n"<buolaš>"\n\t"buolaš" N Sg Nom @<SPRED #8->7 \n"<,>"\n\t"," CLB #9->6 \n"<de>"\n\t"de" Adv @ADVL> #10->12 \n"<aggregáhta>"\n\t"aggregáhta" N Sg Nom @SUBJ> #11->12 \n"<billánii>"\n\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0 \n"<.>"\n\t"." CLB #13->12 \n\n"<¶>"\n\t"¶" CLB #1->1 \n\n')
