# -*- coding: utf-8 -*-

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
#   Copyright © 2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert bible usx xml files to giella xml format."""

from lxml import etree


def para_p2text(paragraph):
    return [
        child.tail.strip()
        for child in paragraph
        if child.tail and child.tail is not None and child.tail.strip()
    ]


def extract_text(paragraph):
    if len(paragraph):
        return ' '.join(para_p2text(paragraph))

    return paragraph.text


def convert2intermediate(filename):
    """Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    """
    usx_doc = etree.parse(filename).getroot()
    document = etree.Element('document')
    body = etree.SubElement(document, 'body')
    body.text = '\n'

    print(filename)
    for child in usx_doc:
        if child.tag == 'chapter':
            section = etree.SubElement(body, 'section')
            section.text = '\n'
            section.tail = '\n'
        elif child.tag == 'para':
            if child.get('style') in ['s', 'p', 'nb']:
                try:
                    paragraph = etree.SubElement(section, 'p')
                except UnboundLocalError:
                    section = etree.SubElement(body, 'section')
                    section.text = '\n'
                    section.tail = '\n'
                    paragraph = etree.SubElement(section, 'p')

                if child.get('style') == 's':
                    paragraph.set('type', 'title')
                paragraph.text = extract_text(child)
            elif child.get('style') in ['m', 'q1']:
                if paragraph.get('type') == 'title':
                    paragraph = etree.SubElement(section, 'p')
                    paragraph.text = ''
                paragraph.text = f'{paragraph.text} {extract_text(child)}'
            elif child.get('style') in ['b']:
                pass
            elif child.get('style') in ['rem', 'toc1', 'toc2', 'toc3', 'h', 'mt']:
                # Should possibly handled further
                pass
            else:
                print(etree.tostring(child, encoding='unicode'))
        elif child.tag == 'book':
            pass
        else:
            print(etree.tostring(child, encoding='unicode'))

    return document
