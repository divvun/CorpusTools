# -*- coding: utf-8 -*-
import io
import lxml.doctestcompare
import lxml.etree
import doctest

from corpustools import converter


tests = {
    'book_chapter_section_verse': {
        'orig': (
            u'<document>'
            u'  <head/>'
            u'  <body>'
            u'    <book title="Book title">'
            u'      <chapter title="Kapittel 1">'
            u'        <section title="Section 1">'
            u'          <verse number="1">Vearsa 1 </verse>'
            u'          <verse number="2">Vearsa 2 </verse>'
            u'        </section>'
            u'      </chapter>'
            u'    </book>'
            u'  </body>'
            u'</document>'
            ),
        'converted': (
            '<document>'
            '  <body>'
            '    <section>'
            '      <p type="title">Book title</p>'
            '      <section>'
            '        <p type="title">Kapittel 1</p>'
            '        <section>'
            '          <p type="title">Section 1</p>'
            '          <p>Vearsa 1 Vearsa 2 </p>'
            '        </section>'
            '      </section>'
            '    </section>'
            '  </body>'
            '</document>'
            ),
        },
    'book_chapter_verse': {
        'orig': (
            u'<document>'
            u'  <header>'
            u'    <title>1</title>'
            u'  </header>'
            u'  <body>'
            u'    <book title="1 Sálmmaid girji ">'
            u'      <chapter number="1">'
            u'        <verse number="1">Vearsa1, </verse>'
            u'        <verse number="2">vearsa2. </verse>'
            u'      </chapter>'
            u'    </book>'
            u'  </body>'
            u'</document>'
            ),
        'converted': (
            '<document>'
            '  <body>'
            '    <section>'
            '      <p type="title">1 Sálmmaid girji</p>'
            '      <section>'
            '        <p type="title">1</p>'
            '        <p>Vearsa1, </p>'
            '        <p>vearsa2. </p>'
            '      </section>'
            '    </section>'
            '  </body>'
            '</document>'
            ),
        },
    'book_chapter_section_p': {
        'orig': (
            u'<document>'
            u'  <header>'
            u'    <title>1</title>'
            u'  </header>'
            u'  <body>'
            u'    <book title="1 Sálmmaid girji ">'
            u'      <chapter number="1">'
            u'        <section title="Section title">'
            u'          <verse number="1">Vearsa1 </verse>'
            u'          <p>'
            u'            <verse number="2">Vearsa2, </verse>'
            u'            <verse number="3">vearsa3. </verse>'
            u'          </p>'
            u'          <verse number="4">Vearsa 4.</verse>'
            u'        </section>'
            u'      </chapter>'
            u'    </book>'
            u'  </body>'
            u'</document>'
            ),
        'converted': (
            '<document>'
            '  <body>'
            '    <section>'
            '      <p type="title">1 Sálmmaid girji</p>'
            '      <section>'
            '        <p type="title">1</p>'
            '        <section>'
            '          <p type="title">Section title</p>'
            '          <p>Vearsa1 </p>'
            '          <p>Vearsa2, vearsa3.</p>'
            '          <p>Vearsa 4.</p>'
            '        </section>'
            '      </section>'
            '    </section>'
            '  </body>'
            '</document>'
            ),
        },
    }


def assertXmlEqual(got, want):
    """Check if two xml snippets are equal
    """
    got = lxml.etree.tostring(got)
    want = lxml.etree.tostring(want)
    checker = lxml.doctestcompare.LXMLOutputChecker()
    if not checker.check_output(want, got, 0):
        message = checker.output_difference(
            doctest.Example("", want), got, 0).encode('utf-8')
        raise AssertionError(message)


def test_conversion():
    for testname, bible_xml in tests.iteritems():
        yield check_conversion, testname, bible_xml


def check_conversion(testname, bible_xml):
    '''Check that the tidied html is correctly converted
    to corpus xml via the xhtml2corpus.xsl style sheet
    '''
    bc = converter.BiblexmlConverter('bogus.bible.xml')
    bc.orig = io.StringIO(bible_xml['orig'])
    got = bc.convert2intermediate()
    want = lxml.etree.fromstring(bible_xml['converted'])
    assertXmlEqual(got, want)
