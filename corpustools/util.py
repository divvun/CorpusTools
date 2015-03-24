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
#   Copyright 2014 Kevin Brubeck Unhammer <unhammer@fsfe.org>
#   Copyright 2014 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import unicode_literals

import os
import operator
import inspect
import platform


class SetupException(Exception):
    pass


class ExecutableMissingException(Exception):
    pass


class ArgumentError(Exception):
    pass


def basename_noext(fname, ext):
    return os.path.basename(fname)[:-len(ext)]


def sort_by_value(table, **args):
    return sorted(table.iteritems(),
                  key=operator.itemgetter(1),
                  **args)


def replace_all(replacements, string):
    return reduce(lambda a, kv: a.replace(*kv),
                  replacements,
                  string)

def split_path(path):
    """
    Split an absolute path into useful components:
    (root, module, lang, genre, subdirs, basename)
    """
    def split_on_module(p):
        for module in ["orig", "converted", "prestable", "stable"]: # toktmx?
            d = "/"+module+"/"
            if d in p:
                root, rest = p.split(d)
                return root, module, rest
    # Ensure we have at least one / before module, for safer splitting:
    abspath = os.path.normpath(os.path.abspath(path))
    root, module, lang_etc = split_on_module(abspath)
    l = lang_etc.split("/")
    lang, genre, subdirs, basename = l[0], l[1], l[2:-1], l[-1]
    return root, module, lang, genre, "/".join(subdirs), basename




def is_executable(fullpath):
    return os.path.isfile(fullpath) and os.access(fullpath, os.X_OK)


def path_possibilities(program):
    return (os.path.join(path.strip('"'),
                         program)
            for path
            in os.environ["PATH"].split(os.pathsep))


def executable_in_path(program):
    fpath, _ = os.path.split(program)
    if fpath:
        return is_executable(program)
    else:
        return any(is_executable(possible_path)
                   for possible_path in
                   path_possibilities(program))


def sanity_check(program_list):
    """Look for programs and files that are needed to do the analysis.
    If they don't exist, raise an exception.
    """
    if 'GTHOME' not in os.environ:
        raise SetupException("You have to set the environment variable GTHOME "
                             "to your checkout of langtech/trunk!")
    for program in program_list:
        if executable_in_path(program) is False:
            raise ExecutableMissingException(
                "Couldn't find %s in $PATH or it is not executable." % (
                    program.encode('utf-8'),))


def get_lang_resource(lang, resource, fallback=None):
    path = os.path.join(os.environ['GTHOME'], 'langs', lang, resource)
    if os.path.exists(path):
        return path
    else:
        return fallback


def get_preprocess_command(lang):
    preprocess_script = os.path.join(os.environ['GTHOME'],
                                     'gt/script/preprocess')
    sanity_check([preprocess_script])
    abbr_fb = get_lang_resource("sme", 'tools/preprocess/abbr.txt')
    abbr = get_lang_resource(lang, 'tools/preprocess/abbr.txt', abbr_fb)
    return [preprocess_script,
            "--xml",
            "--abbr={}".format(abbr)]

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def print_element(element, level, indent, out):
    '''Format an html document

    This function formats html documents for readability, to see
    the structure of the given document. It ruins white space in
    text parts.

    element is a lxml.etree element
    level is an integer indicating at what level this element is
    indent is an integer indicating how many spaces this element should
    be indented
    out is a file like buffer, e.g. an opened file
    '''
    tag = element.tag.replace('{http://www.w3.org/1999/xhtml}', 'html:')

    out.write(' ' * (level * indent))
    out.write('<{}'.format(tag))

    for k, v in element.attrib.items():
        out.write(' ')
        if isinstance(k, unicode):
            out.write(k.encode('utf8'))
        else:
            out.write(k)
        out.write('="')
        if isinstance(v, unicode):
            out.write(v.encode('utf8'))
        else:
            out.write(v)
        out.write('"')
    out.write('>\n')

    if element.text is not None and element.text.strip() != '':
        out.write(' ' * ((level + 1) * indent))
        if isinstance(element.text, unicode):
            out.write(element.text.strip().encode('utf8'))
        else:
            out.write(element.text.strip())
        out.write('\n')

    for child in element:
        print_element(child, level + 1, indent, out)

    out.write(' ' * (level * indent))
    out.write('</{}>\n'.format(tag))

    if level > 0 and element.tail is not None and element.tail.strip() != '':
        for _ in range(0, (level - 1) * indent):
            out.write(' ')
        out.write('{}\n'.format(element.tail.strip().encode('utf8')))


def name_to_unicode(filename):
    if platform.system() == 'Windows':
        return filename
    else:
        return filename.decode('utf-8')


