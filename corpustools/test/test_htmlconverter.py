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
#   Copyright © 2014-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

u"""Test conversion of html files."""

import os

from lxml import etree
from lxml.html import html5parser
import six
import testfixtures
from parameterized import parameterized

from corpustools import htmlconverter
from corpustools.test.test_htmlcontentconverter import clean_namespaces
from corpustools.test.test_xhtml2corpus import assertXmlEqual
from corpustools.test.xmltester import XMLTester


DOCUMENT_TEMPLATE = (
    '<document>'
    '  <header>'
    '   <title></title>'
    '  </header>'
    '  <body>'
    '{}'
    '  </body>'
    '</document>'
)


class TestHTMLConverter(XMLTester):
    """Test conversion of html documents."""

    @parameterized.expand([
        (
            'bare_text_after_p',
            'orig/sme/admin/ugga.html',
            '''
            <html lang="no" dir="ltr">
                <head>
                    <title>
                        Visit Stetind: Histåvrrå: Nasjonálvárre
                    </title>
                </head>
                <body>
                    <div id="bbody">
                        <div id="mframe">
                            <div class="sub" id="masterpage">
                                <div id="mpage">
                                    <h1>Gå Stáddá</h1>
                                    <div class="ingress">
                                        <font size="3">
                                            <font>
                                                Gå ÅN
                                                <span>
                                                </span>
                                            </font>
                                        </font>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            ''',
            '''
            <document>
                <header>
                    <title>Visit Stetind: Histåvrrå: Nasjonálvárre</title>
                </header>
                <body>
                    <p type="title">Gå Stáddá</p>
                    <p>Gå ÅN</p>
                    <p></p>
                </body>
            </document>
            '''
        ),
        (
            'bare_text_after_list',
            'orig/sme/admin/ugga.html',
            '''
            <html lang="no" dir="ltr">
                <body>
                    <UL>
                        <LI><A href="http://www.soff.no">www.soff.no</A>
                        <LI><A href="http://www.soff.uit.no">www.soff.uit.no</A> </LI>
                    </UL>
                    <CENTER><SMALL>
                            <a href='http://www.fmno.no'>Fylkesmannen i Nordland &copy; 2005</a>
                    </SMALL></CENTER>
                </body>
            </html>
            ''',  # nopep8
            DOCUMENT_TEMPLATE.format('''
                    <list>
                        <p type="listitem">www.soff.no</p>
                        <p type="listitem">www.soff.uit.no</p>
                    </list>
                    <p>Fylkesmannen i Nordland © 2005</p>
            ''')
        ),
        (
            'body_bare_text',
            'orig/sme/admin/ugga.html',
            '''
            <html lang="no" dir="ltr">
                <head>
                    <title>
                        Visit Stetind: Histåvrrå: Nasjonálvárre
                    </title>
                </head>
                <body>
                    <div id="bbody">
                        <div id="mframe">
                            <div class="sub" id="masterpage">
                                <div id="mpage">
                                    <div class="ingress">
                                        <font size="3">
                                            <font>
                                                Gå ÅN
                                                <span>
                                                </span>
                                            </font>
                                        </font>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            ''',
            '''
            <document>
                <header>
                    <title>Visit Stetind: Histåvrrå: Nasjonálvárre</title>
                </header>
                <body>
                    <p>Gå ÅN</p>
                    <p></p>
                </body>
            </document>
            '''
        ),
        (
            'script_with_tail',
            'orig/sme/admin/ugga.html',
            '''
            <html lang="no" dir="ltr">
                <head>
                    <title>
                        Visit Stetind: Histåvrrå: Nasjonálvárre
                    </title>
                </head>
                <body>
                    <p>abba</p>
                        <script>
                        </script>uffda
                    </p>
                </body>
            </html>
            ''',
            '''
            <document>
                <header>
                    <title>Visit Stetind: Histåvrrå: Nasjonálvárre</title>
                </header>
                <body>
                    <p>abba</p>
                </body>
            </document>
            '''
        )

    ])
    def test_convert2intermediate(self, testname, filename, content, want):
        """Check that convoluted html is correctly converted to xml."""
        with testfixtures.TempDirectory() as temp_dir:
            if six.PY3:
                content = content.encode('utf8')
            temp_dir.write(filename, content)
            got = htmlconverter.convert2intermediate(
                os.path.join(temp_dir.path, filename))
            self.assertXmlEqual(got, etree.fromstring(want))

    def test_content(self):
        """Check that content really is real utf-8."""
        content = u'''
            <!DOCTYPE html>
            <html lang="sma-NO">
                <head>
                    <meta name="viewport" content="width=device-width,
                    initial-scale=1.0">
                </head>
                <body>
                    <h1>ï å</h1>
                </body>
            </html>
        '''.encode(encoding='utf-8')
        want = html5parser.fromstring(u'''
            <html lang="sma-NO">
                <head>
                    <meta name="viewport" content="width=device-width,
                    initial-scale=1.0">
                </head>
                <body>
                    <h1>&#239; &#229;</h1>
                </body>
            </html>
        ''')
        filename = 'orig/sme/admin/ugga.html'
        with testfixtures.TempDirectory() as temp_dir:
            temp_dir.write(filename, content)
            got = htmlconverter.webpage_to_unicodehtml(
                os.path.join(temp_dir.path, filename))

            clean_namespaces([got, want])
            self.assertXmlEqual(got, want)


@parameterized([
    (
        'ul-li-a',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <a>Geahčá</a>'
            '      </li>'
            '      <li>'
            '        <a>Geahčá</a>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">'
            '               Geahčá'
            '      </p>'
            '      <p type="listitem">'
            '               Geahčá'
            '      </p>'
            '    </list>'
        ),
    ),
    (
        'blockquote-p',
        (
            '<html>'
            '  <body>'
            '  <blockquote>'
            '      <p>«at like rettigheter ikke nødvendigvis trenger'
            '  </blockquote>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>'
            '      <span type="quote">'
            '               «at like rettigheter ikke nødvendigvis trenger'
            '      </span>'
            '  </p>'
        ),
    ),
    (
        'div-a-h2',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '            <a>'
            '                <h2>'
            '                    Pressesenter'
            '                </h2>'
            '            </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '            Pressesenter'
            '    </p>'
        ),
    ),
    (
        'div-a-p',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '            <a>'
            '                <p>'
            '                    Pressesenter'
            '                </p>'
            '            </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>'
            '      Pressesenter'
            '  </p>'
        ),
    ),
    (
        'div-b-and-br',
        (
            '<html>'
            '  <body>'
            '  <div>'
            '      <b>'
            '               Ohcanáigemearri:'
            '      </b>'
            '      <br />'
            '           15.09.2006.'
            '  </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>'
            '      <em type="bold">'
            '               Ohcanáigemearri:'
            '      </em>'
            '  </p>'
            '  <p>'
            '           15.09.2006.'
            '  </p>'
        ),
    ),
    (
        'div-div-a-span',
        (
            '<html>'
            '  <body>'
            '  <div>'
            '      <div>'
            '    <a>'
            '          <span>John-Marcus Kuhmunen</span>'
            '    </a>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>'
            '           John-Marcus Kuhmunen'
            '  </p>'
        ),
    ),
    (
        'div-div-a-and-div',
        (
            '<html>'
            '  <body>'
            '  <div>'
            '      <div>'
            '    <a>Geahča buot áššebáhpáriid</a>'
            '    <div style="clear: both"></div>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>Geahča buot áššebáhpáriid</p>'
        ),
    ),
    (
        'div-font-span-font',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <font>'
            '        <span>'
            '          <font>'
            '            maajjen'
            '          </font>'
            '        </span>'
            '      </font>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      maajjen'
            '   </p>'
        ),
    ),
    (
        'div-i-font-span-font',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <i>'
            '        <font>'
            '          <span>'
            '            <font>'
            '              listeforslag,'
            '            </font>'
            '          </span>'
            '        </font>'
            '      </i>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">'
            '        listeforslag,'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'div-h1-and-a',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <h1>Terje Riis-Johansen</h1>'
            '      <a>'
            '        Taler og artikler'
            '      </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Terje Riis-Johansen'
            '    </p>'
            '    <p>'
            '      Taler og artikler'
            '    </p>'
        ),
    ),
    (
        'div-h1-and-text-and-br-and-a',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <h1>Ledige stillingar</h1>'
            '      No kan du søke jobb.<br />'
            '      &#160;<br />'
            '      Sjekk også våre rekrutteringssider'
            '      <a title="Jobb i AD">'
            '        Jobb i AD'
            '      </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Ledige stillingar'
            '    </p>'
            '    <p>'
            '      No kan du søke jobb.'
            '    </p>'
            '    <p>'
            '      Sjekk også våre rekrutteringssider'
            '    </p>'
            '    <p>'
            '      Jobb i AD'
            '    </p>'
        ),
    ),
    (
        'div-hx',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <h1>Sámedikki doarjja</h1>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">Sámedikki doarjja</p>'
        ),
    ),
    (
        'div-p-and-font',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <p>Rikspolitiske verv</p>'
            '      <font>abc</font>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>Rikspolitiske verv</p>'
            '    <p>abc</p>'
        ),
    ),
    (
        'div-p-strong-and-br-and-text',
        (
            '<html>'
            '  <body>'
            '  <div>'
            '      <p>'
            '        <strong>'
            '          Poastadreassa:'
            '        </strong>'
            '        <br />'
            '        Postboks 8036 Dep'
            '        <br />'
            '        0030 Oslo'
            '        <br />'
            '      </p>'
            '      E-poasta:'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">'
            '        Poastadreassa:'
            '      </em>'
            '      Postboks 8036 Dep'
            '      0030 Oslo'
            '    </p>'
            '    <p>'
            '      E-poasta:'
            '    </p>'
        ),
    ),
    (
        'div-span',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <span>'
            '        Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '      </span>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
        ),
    ),
    (
        'div-small-a',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <small>'
            '        <a>'
            '          Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '        </a>'
            '      </small>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '      <p>Gulaskuddanáigimearri: guovvamánu 20. b. 2010</p>'
        ),
    ),
    (
        'div-small',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <small>'
            '         Harrieth Aira'
            '      </small>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '      <p>Harrieth Aira</p>'
        ),
    ),
    (
        'div-p-small',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <p>'
            '        <small>'
            '          div-p-small'
            '        </small>'
            '      </p>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      div-p-small'
            '    </p>'
        ),
    ),
    (
        'div-em-p-em',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <em>'
            '        <p>'
            '          <em>'
            '            Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '          </em>'
            '        </p>'
            '      </em>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">'
            '        Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'div-a-div',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <a>'
            '        <div>'
            '          Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '        </div>'
            '      </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Gulaskuddanáigimearri: guovvamánu 20. b. 2010'
            '    </p>'
        ),
    ),
    (
        'div-table',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <table>'
            '        <tbody>'
            '          <tr>'
            '            <td>'
            '              abc <a>Nynorsk</a> def'
            '            </td>'
            '          </tr>'
            '        </tbody>'
            '      </table>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '      <p>'
            '        abc'
            '      </p>'
            '      <p>'
            '        Nynorsk'
            '      </p>'
            '      <p>'
            '        def'
            '      </p>'
        ),
    ),
    (
        'div-text-and-br-and-div',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      Tällä viikolla<br />'
            '      <br />'
            '      SPN:n hallitus'
            '      <br />'
            '      <div />'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Tällä viikolla'
            '    </p>'
            '    <p>'
            '      SPN:n hallitus'
            '    </p>'
        ),
    ),
    (
        'div-text-and-span',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      Laitan blogini lukijoille'
            '      <span>'
            '        Voimassa oleva'
            '      </span>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>Laitan blogini lukijoille</p>'
            '    <p>Voimassa oleva</p>'
        ),
    ),
    (
        'div-text-and-a-text',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      Almmuhan Kuhmunen, John-Marcus.'
            '      <a>Halloi!</a>'
            '      Maŋumustá rievdaduvvon 26.06.2009'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Almmuhan Kuhmunen, John-Marcus.'
            '    </p>'
            '    <p>'
            '      Halloi!'
            '    </p>'
            '    <p>'
            '      Maŋumustá rievdaduvvon 26.06.2009'
            '    </p>'
        ),
    ),
    (
        'div-ul-li-div',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <ul>'
            '        <li>'
            '          <div>'
            '            FoU'
            '          </div>'
            '         </li>'
            '      </ul>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">FoU</p>'
            '    </list>'
        ),
    ),
    (
        'div-ol-li-div',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <ol>'
            '        <li>'
            '          <div>'
            '            Teknologiaovdánahttin ja DGT (IKT)'
            '          </div>'
            '        </li>'
            '      </ol>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">Teknologiaovdánahttin ja DGT (IKT)</p>'
            '    </list>'
        ),
    ),
    (
        'div-div-div-p',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <div>'
            '        <div>'
            '          <p>Sámediggi lea juolludan doarjaga.</p>'
            '        </div>'
            '      </div>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Sámediggi lea juolludan doarjaga.'
            '    </p>'
        ),
    ),
    (
        'div-div-div-a',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <div>'
            '        <div>'
            '          <a>'
            '            <span>John-Marcus Kuhmunen</span>'
            '          </a>'
            '        </div>'
            '      </div>'
            '  </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      John-Marcus Kuhmunen'
            '    </p>'
        ),
    ),
    (
        'font-span-font-sub',
        (
            '<html>'
            '  <body>'
            '    <font>'
            '      <span>'
            '        <font>'
            '          <sub>'
            '            aa'
            '          </sub>'
            '        </font>'
            '      </span>'
            '    </font>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      aa'
            '    </p>'
        ),
    ),
    (
        'h1-6',
        (
            '<html>'
            '  <body>'
            '  <h1>header1</h1>'
            '  <h2>header2</h2>'
            '  <h3>header3</h3>'
            '  <h4>header4</h4>'
            '  <h5>header5</h5>'
            '  <h6>header6</h6>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">header1</p>'
            '    <p type="title">header2</p>'
            '    <p type="title">header3</p>'
            '    <p type="title">header4</p>'
            '    <p type="title">header5</p>'
            '    <p type="title">header6</p>'
        ),
    ),
    (
        'h1-b',
        (
            '<html>'
            '  <body>'
            '    <h1>'
            '      <b>Phone</b>'
            '    </h1>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Phone'
            '    </p>'
        ),
    ),
    (
        'note-i',
        (
            '<html>'
            '  <body>'
            '    <note>Geahča <i>Sámi skuvlahistorjá 2. -girjjis</i></note>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>Geahča</p>'
            '    <p>'
            '      <em type="italic">Sámi skuvlahistorjá 2. -girjjis</em>'
            '    </p>'
        ),
    ),
    (
        'li-a-b-font',
        (
            '<html>'
            '  <body>'
            '    <li>'
            '      <a>'
            '        <b>'
            '          <font>'
            '            Deltakerloven.'
            '          </font>'
            '        </b>'
            '      </a>'
            '    </li>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="listitem">'
            '      <em type="bold">'
            '        Deltakerloven.'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'ul-strong-li-strong-a-strong',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <strong>'
            '        <li>'
            '          <strong>'
            '            <a>'
            '              <strong>'
            '                Deltakerloven.'
            '              </strong>'
            '            </a>'
            '          </strong>'
            '        </li>'
            '      </strong>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">'
            '        Deltakerloven.'
            '      </p>'
            '    </list>'
        ),
    ),
    (
        'ul-li-div',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <div>'
            '          FoU'
            '        </div>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">FoU</p>'
            '    </list>'
        ),
    ),
    (
        'nobr-a',
        (
            '<html>'
            '  <body>'
            '    <nobr>'
            '      <a title=\'Aktuelt - Nyheiter - 2009\'>'
            '        2009'
            '      </a>'
            '    </nobr>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>2009</p>'
        ),
    ),
    (
        'p-a-note',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <a name="[1]">[1] <note>Vestertana.</note></a>'
            '      <a name="[2]">[2] <note>Fra 1918.</note></a>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>[1] Vestertana. [2] Fra 1918. </p>'
        ),
    ),
    (
        'wbr',
        (
            '<html>'
            '  <body>'
            '    <wbr/>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(''),
    ),
    (
        'i-ol-li',
        (
            '<html>'
            '  <body>'
            '    <i>'
            '      <ol>'
            '        <li>wtf ol!</li>'
            '      </ol>'
            '    </i>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">wtf ol!</p>'
            '    </list>'
        ),
    ),
    (
        'i-ul-li',
        (
            '<html>'
            '  <body>'
            '    <i>'
            '      <ul>'
            '        <li>wtf ul!</li>'
            '      </ul>'
            '    </i>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">wtf ul!</p>'
            '    </list>'
        ),
    ),
    (
        'ol-i-li',
        (
            '<html>'
            '  <body>'
            '    <ol>'
            '      <i>'
            '        <li> Lærer K. Bruflodt</li>'
            '      </i>'
            '    </ol>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">Lærer K. Bruflodt </p>'
            '    </list>'
        ),
    ),
    (
        'ol-li-ol-li',
        (
            '<html>'
            '  <body>'
            '    <ol type="1" start="1">'
            '      <li>1</li>'
            '      <li>2'
            '        <ol>'
            '          <li>2.1</li>'
            '          <li>2.2</li>'
            '          <li>2.3</li>'
            '        </ol>'
            '      </li>'
            '      <li>3</li>'
            '      <li>4</li>'
            '      <li>5</li>'
            '    </ol>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">1</p>'
            '      <p type="listitem">'
            '        2'
            '        <list>'
            '          <p type="listitem">2.1</p>'
            '          <p type="listitem">2.2</p>'
            '          <p type="listitem">2.3</p>'
            '        </list>'
            '      </p>'
            '      <p type="listitem">3</p>'
            '      <p type="listitem">4</p>'
            '      <p type="listitem">5</p>'
            '    </list>'
        ),
    ),
    (
        'ul-li-ul-li',
        (
            '<html>'
            '  <body>'
            '    <ul type="1" start="1">'
            '      <li>1</li>'
            '      <li>2'
            '        <ul>'
            '          <li>2.1</li>'
            '          <li>2.2</li>'
            '          <li>2.3</li>'
            '        </ul>'
            '      </li>'
            '      <li>3</li>'
            '      <li>4</li>'
            '      <li>5</li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">1</p>'
            '      <p type="listitem">'
            '        2'
            '        <list>'
            '          <p type="listitem">2.1</p>'
            '          <p type="listitem">2.2</p>'
            '          <p type="listitem">2.3</p>'
            '        </list>'
            '      </p>'
            '      <p type="listitem">3</p>'
            '      <p type="listitem">4</p>'
            '      <p type="listitem">5</p>'
            '    </list>'
        ),
    ),
    (
        'p-a-b',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <a name="hov8.noteref1">'
            '        <b>'
            '          [1]'
            '        </b>'
            '      </a>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        [1]'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'p-b-span',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <b>'
            '        <span>'
            '          Sámi oahpponeavvojahki – Sámi máhttolokten'
            '        </span>'
            '      </b>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        Sámi oahpponeavvojahki – Sámi máhttolokten'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'p-font-font-b-span',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <font>'
            '        <font>'
            '          <b>'
            '            <span>'
            '              Bargit'
            '            </span>'
            '          </b>'
            '          <span>'
            '            fertejit dahkat.'
            '          </span>'
            '        </font>'
            '      </font>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">Bargit</em> fertejit dahkat.'
            '    </p>'
        ),
    ),
    (
        'div-font-font-p',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <font>'
            '        <font>'
            '          <p>'
            '            Voksenopplæring'
            '          </p>'
            '        </font>'
            '      </font>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Voksenopplæring'
            '    </p>'
        ),
    ),
    (
        'div-font-p',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <font>'
            '          <p>'
            '            Aerpievuekien daajroe'
            '          </p>'
            '      </font>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Aerpievuekien daajroe'
            '    </p>'
        ),
    ),
    (
        'p-span-b',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <span>'
            '        <b>'
            '          sámi guovddáža viidideapmi stáhtabušehttii'
            '        </b>'
            '      </span>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        sámi guovddáža viidideapmi stáhtabušehttii'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'p-to-p-listitem',
        (
            '<html>'
            '  <body>'
            '    <p>• mearridit gielddaid <br />'
            '• ovddidit servodatsihkkarvuođa</p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="listitem">mearridit gielddaid </p>'
            '    <p type="listitem">ovddidit servodatsihkkarvuođa</p>'
        ),
    ),
    (
        'h3-pb',
        (
            '<html>'
            '  <body>'
            '    <h3><pb>Kapittel</pb></h3>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">Kapittel</p>'
        ),
    ),
    (
        'p-pb',
        (
            '<html>'
            '  <body>'
            '    <p><pb><b>&#167; 1-1.</b></pb></p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p><em type="bold">&#167; 1-1.</em></p>'
        ),
    ),
    (
        'ul-li-span-a-span-font',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <span>'
            '          <a>'
            '            <span>'
            '              <font>Energiija(EV)</font>'
            '            </span>'
            '          </a>'
            '          <a>'
            '            <font>'
            '              <span>(goallostat)</span>'
            '            </font>'
            '          </a>'
            '        </span>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">Energiija(EV) (goallostat)</p>'
            '    </list>'
        ),
    ),
    (
        'ul-li-span-a-font-span',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <span>'
            '          <a>'
            '            <font>'
            '              <span>Oljo </span>'
            '              <span>(goallostat)</span>'
            '            </font>'
            '          </a>'
            '        </span>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">Oljo (goallostat)</p>'
            '    </list>'
        ),
    ),
    (
        'p-span-with-a-span-font-and-a-font-span',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <span>'
            '        <a>'
            '          <span>'
            '            <font>Energiija</font>'
            '          </span>'
            '        </a>'
            '        <a>'
            '          <font>'
            '            <span>(goallostat)</span>'
            '          </font>'
            '        </a>'
            '      </span>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '           Energiija (goallostat)'
            '    </p>'
        ),
    ),
    (
        'ul-li-sup',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>km<sup>2</sup></li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '            <p type="listitem">km 2</p>'
            '    </list>'
        ),
    ),
    (
        'p-sup-a-sup',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      bla bla'
            '      <sup>'
            '        <a>'
            '          <sup>2</sup>'
            '        </a>'
            '      </sup>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      bla bla 2'
            '    </p>'
        ),
    ),
    (
        'td-a-b',
        (
            '<html>'
            '  <body>'
            '    <td>&#160;'
            '      <a>'
            '        <b>'
            '          Innholdsfortegnelse'
            '        </b>'
            '      </a>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        Innholdsfortegnelse'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'td-a-div',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <a>'
            '        <div>'
            '          Klara'
            '        </div>'
            '      </a>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Klara'
            '    </p>'
        ),
    ),
    (
        'table-tr-td-a-p',
        (
            '<html>'
            '  <body>'
            '    <table>'
            '      <tr>'
            '        <td>'
            '          <a>'
            '            <p>'
            '              Pressesenter'
            '            </p>'
            '          </a>'
            '        </td>'
            '      </tr>'
            '     </table>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '   <p>'
            '     Pressesenter'
            '   </p>'
        ),
    ),
    (
        'td-a',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <a>22 24 91 03</a>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      22 24 91 03'
            '    </p>'
        ),
    ),
    (
        'td-b-and-text',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <b>'
            '        Ålkine'
            '      </b>'
            '      <br />'
            '      (Guvvie: Grete Austad)'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        Ålkine'
            '      </em>'
            '    </p>'
            '    <p>'
            '      (Guvvie: Grete Austad)'
            '    </p>'
        ),
    ),
    (
        'td-b',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <b>'
            '        Albert'
            '      </b>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        Albert'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'table-tr-td-div',
        (
            '<html>'
            '  <body>'
            '    <table>'
            '      <tr>'
            '        <td>'
            '          <div>'
            '            <a></a>'
            '            <h1>Láhka</h1>'
            '            <p>Lága</p>'
            '            <blockquote>'
            '              <p>Gč. lága suoidnemánu</p>'
            '            </blockquote>'
            '            <a></a>'
            '            <a></a>'
            '          </div>'
            '        </td>'
            '      </tr>'
            '    </table>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p></p>'
            '    <p type="title">Láhka</p>'
            '    <p>Lága</p>'
            '    <p>'
            '      <span type="quote">Gč. lága suoidnemánu</span>'
            '    </p>'
            '    <p></p>'
            '    <p></p>'
        ),
    ),
    (
        'td-font-span-span-span',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font>'
            '        <span>'
            '          <span>'
            '            <span>'
            '              Møre og Romsdal Fylkkadiggemiellahttu'
            '            </span>'
            '          </span>'
            '        </span>'
            '      </font>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <p>'
            '           Møre og Romsdal Fylkkadiggemiellahttu'
            '  </p>'
        ),
    ),
    (
        'td-font-span-strong',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font>'
            '        <span>'
            '          <strong>Politihkalaš doaimmat</strong>'
            '        </span>'
            '      </font>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">'
            '        Politihkalaš doaimmat'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'td-font-span',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font>'
            '        <span>'
            '          Stáhtačálli, Eanandoallo- ja biebmodepartemeanta'
            '        </span>'
            '      </font>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Stáhtačálli, Eanandoallo- ja biebmodepartemeanta'
            '    </p>'
        ),
    ),
    (
        'td-font',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <font>Kvirrevitt</font>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '           Kvirrevitt'
            '    </p>'
        ),
    ),
    (
        'td-h2-and-text-and-p',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <h2>'
            '        Departementet ber skoledirektøren om hjelp'
            '      </h2>'
            '      For å kunne '
            '      <p>'
            '        Kirkedepartementet'
            '      </p>'
            '  </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Departementet ber skoledirektøren om hjelp'
            '    </p>'
            '   <p>'
            '     For å kunne '
            '   </p>'
            '   <p>'
            '     Kirkedepartementet'
            '   </p>'
        ),
    ),
    (
        'td-h3-span',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <h3>'
            '      <span>'
            '        <a></a>'
            '        Gulaskuddanásahusat</span>'
            '       </h3>'
            '     </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Gulaskuddanásahusat'
            '    </p>'
        ),
    ),
    (
        'td-p-and-b',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <p>'
            '        <b>'
            '          er født i 1937'
            '        </b>'
            '      </p>'
            '      <b>'
            '        arbeidd innafor mange yrke'
            '      </b>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">'
            '        er født i 1937'
            '      </em>'
            '    </p>'
            '    <p>'
            '      <em type="bold">'
            '        arbeidd innafor mange yrke'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'td-p-span-span-span',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <p>'
            '        <span>'
            '          <span>'
            '            <span>'
            '              link'
            '            </span>'
            '            <span>'
            '              int'
            '            </span>'
            '            <span>'
            '              høringsinstanser'
            '            </span>'
            '          </span>'
            '          <span>'
            '            Gulaskuddanásahusat'
            '          </span>'
            '        </span>'
            '      </p>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      link'
            '      int'
            '      høringsinstanser'
            '      Gulaskuddanásahusat'
            '    </p>'
        ),
    ),
    (
        'table-tr-td-with-span-font-and-b-and-p-span',
        (
            '<html>'
            '  <body>'
            '    <table>'
            '      <tr>'
            '        <td>'
            '          <span>'
            '            <font>Riikkačoahkkincealkámušat 2006</font>'
            '          </span>'
            '          <b>NSR 38. Riikkačoahkkin</b>'
            '          <p>'
            '            <span>'
            '              Norgga Sámiid Riikkasearvvi '
            '            </span>'
            '            2006'
            '          </p>'
            '        </td>'
            '      </tr>'
            '    </table>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>Riikkačoahkkincealkámušat 2006</p>'
            '    <p>'
            '      <em type="bold">'
            '        NSR 38. Riikkačoahkkin'
            '      </em>'
            '    </p>'
            '    <p>'
            '      Norgga Sámiid Riikkasearvvi  2006'
            '    </p>'
        ),
    ),
    (
        'td-with-span-font-and-b',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <span>'
            '        <font>'
            '          Riikkačoahkkincealkámušat 2006'
            '         </font>'
            '      </span>'
            '      <b>NSR 38.</b>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Riikkačoahkkincealkámušat 2006'
            '    </p>'
            '    <p>'
            '      <em type="bold">'
            '        NSR 38.'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'td-span',
        (
            '<html>'
            '  <body>'
            '    <td><span>Náitalan, 3 máná</span></td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>Náitalan, 3 máná</p>'
        ),
    ),
    (
        'td-strong',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <strong>Gaskavahkku</strong>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">Gaskavahkku</em>'
            '    </p>'
        ),
    ),
    (
        'td-table-tr-td',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <table>'
            '        <tr>'
            '          <td>Kvirrevitt</td>'
            '        </tr>'
            '      </table>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Kvirrevitt'
            '    </p>'
        ),
    ),
    (
        'td-text-and-i-and-p',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      Nuohta:'
            '      <i>'
            '        Jeg går og rusler på Ringerike'
            '      </i>'
            '      <p>'
            '        Mii læt dal čoagganan manga guovllos'
            '      </p>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Nuohta:'
            '    </p>'
            '    <p>'
            '      <em type="italic">'
            '        Jeg går og rusler på Ringerike'
            '      </em>'
            '    </p>'
            '    <p>'
            '      Mii læt dal čoagganan manga guovllos'
            '    </p>'
        ),
    ),
    (
        'td-u',
        (
            '<html>'
            '  <body>'
            '    <td>'
            '      <u>Ášši nr. 54/60:</u>'
            '    </td>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">Ášši nr. 54/60:</em>'
            '    </p>'
        ),
    ),
    (
        'p-span-u-b',
        (
            '<html>'
            '  <body>'
            '    <p>'
            '      <span>'
            '        <u>'
            '          <b>'
            '            Tysfjord turistsenter'
            '          </b>'
            '        </u>'
            '      </span>'
            '    </p>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">Tysfjord turistsenter</em>'
            '    </p>'
        ),
    ),
    (
        'th-b',
        (
            '<html>'
            '  <body>'
            '    <th>'
            '      <b>Språktilbudet</b>'
            '    </th>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">Språktilbudet</em>'
            '    </p>'
        ),
    ),
    (
        'th-div',
        (
            '<html>'
            '  <body>'
            '    <th>'
            '      <div>'
            '        Jan'
            '      </div>'
            '    </th>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Jan'
            '    </p>'
        ),
    ),
    (
        'th-p',
        (
            '<html>'
            '  <body>'
            '    <th>'
            '      <p>Kap. Poasta</p>'
            '    </th>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Kap. Poasta'
            '    </p>'
        ),
    ),
    (
        'thead',
        (
            '<html>'
            '  <body>'
            '    <thead>'
            '    </thead>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(''),
    ),
    (
        'tr-td-em',
        (
            '<html>'
            '  <body>'
            '    <tr>'
            '      <td>'
            '        <em>'
            '          Kapittel 1'
            '        </em>'
            '      </td>'
            '    </tr>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="italic">'
            '        Kapittel 1'
            '      </em>'
            '    </p>'
        ),
    ),
    (
        'ul-li-div-p',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <div>'
            '          <p>'
            '            Friskt'
            '          </p>'
            '        </div>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p type="listitem">'
            '        Friskt'
            '      </p>'
            '    </list>'
        ),
    ),
    (
        'ul-li-p-i',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <li>'
            '        <i>'
            '          4. Slik språkforholdene'
            '        </i>'
            '        <p>'
            '          <i>'
            '            Som alle andre'
            '          </i>'
            '        </p>'
            '        <p>'
            '          <i>'
            '            Vi erklærer'
            '          </i>'
            '         </p>'
            '      </li>'
            '    </ul>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '  <list>'
            '      <p type="listitem">'
            '    <em>'
            '                   4. Slik språkforholdene'
            '    </em>'
            '    <em>'
            '                   Som alle andre'
            '    </em>'
            '    <em>'
            '                   Vi erklærer'
            '    </em>'
            '      </p>'
            '  </list>'
        ),
    ),
    (
        'ul-strong',
        (
            '<html>'
            '  <body>'
            '    <ul>'
            '      <strong>'
            '        Pressesenter'
            '      </strong>'
            '    </li>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <list>'
            '      <p>'
            '        Pressesenter'
            '      </p>'
            '    </list>'
        ),
    ),
    (
        'div-div-abbr',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <div>'
            '        <abbr>'
            '           Kl.'
            '        </abbr>'
            '        11.00'
            '      </div>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      Kl.'
            '    </p>'
            '    <p>'
            '      11.00'
            '    </p>'
        ),
    ),
    (
        'hm',
        (
            '<html>'
            '  <body>'
            '<span>'
            '<div>'
            '<table>'
            '<tbody>'
            '    <tr>'
            '      <td>'
            '        <h2>'
            '           Kl.'
            '        </h2>'
            '        <p>11.00</p>'
            '      </td>'
            '    </tr>'
            '</tbody>'
            '</table>'
            '</div>'
            '</span>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p type="title">'
            '      Kl.'
            '    </p>'
            '    <p>'
            '      11.00'
            '    </p>'
        ),
    ),
    (
        'div-a-b',
        (
            '<html>'
            '  <body>'
            '    <div>'
            '      <a href="http://www.ovdamearka.no">'
            '        <b>'
            '          ovdamearka'
            '        </b>'
            '      </a>'
            '    </div>'
            '  </body>'
            '</html>'
        ),
        DOCUMENT_TEMPLATE.format(
            '    <p>'
            '      <em type="bold">ovdamearka</em>'
            '    </p>'
        ),
    ),
])
def test_conversion(testname, html, xml):
    """Check that the tidied html is correctly converted to corpus xml."""
    with testfixtures.TempDirectory() as temp_dir:
        filepath = os.path.join('orig/sme/admin/sd', testname)
        if six.PY3:
            html = html.encode('utf8')
        temp_dir.write(filepath, html)
        got = htmlconverter.convert2intermediate(
            os.path.join(temp_dir.path, filepath))
        want = etree.fromstring(xml)

        assertXmlEqual(got, want)
