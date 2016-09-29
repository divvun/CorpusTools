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
#   Copyright © 2012-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains classes to handle corpus filenames."""


from __future__ import absolute_import, print_function

import os

from corpustools import util, xslsetter


class CorpusPath(object):
    """Map filenames in a corpus.

    Args:
        path: path to a corpus file
    """

    def __init__(self, path):
        """Initialise the CorpusPath class."""
        self.pathcomponents = self.split_path(path)
        self.md = xslsetter.MetadataHandler(self.xsl, create=True)

    def split_path(self, path):
        """Map path to the original file.

        Args:
            path: a path to a corpus file

        Returns:
            A PathComponents namedtuple containing the components of the
            original file

        Raises:
            ValueError: the path is not part of a corpus.
        """
        def split_on_module(p):
            for module in [u'goldstandard/orig', u'prestable/converted',
                           u'prestable/toktmx', u'prestable/tmx', u'orig',
                           u'converted', u'stable', u'toktmx', u'tmx']:
                d = u'/' + module + u'/'
                if d in p:
                    root, rest = p.split(d)
                    return root, module, rest

            raise ValueError('File is not part of a corpus: {}'.format(path))

        # Ensure we have at least one / before module, for safer splitting:
        abspath = os.path.normpath(os.path.abspath(path))
        root, module, lang_etc = split_on_module(abspath)

        l = lang_etc.split('/')
        lang, genre, subdirs, basename = l[0], l[1], l[2:-1], l[-1]

        if 'orig' in module:
            if basename.endswith('.xsl'):
                basename = util.basename_noext(basename, '.xsl')
            elif basename.endswith('.log'):
                basename = util.basename_noext(basename, '.log')
        elif 'converted' in module or 'analysed' in module:
            basename = util.basename_noext(basename, '.xml')
        elif 'toktmx' in module:
            basename = util.basename_noext(basename, '.toktmx')
        elif 'tmx' in module:
            basename = util.basename_noext(basename, '.tmx')

        return util.PathComponents(root, 'orig', lang, genre,
                                   '/'.join(subdirs), basename)

    @property
    def orig(self):
        """Return the path of the original file."""
        return os.path.join(*list(self.pathcomponents))

    @property
    def xsl(self):
        """Return the path of the metadata file."""
        return self.orig + '.xsl'

    @property
    def log(self):
        """Return the path of the log file."""
        return self.orig + '.log'

    def name(self, module, extension):
        """Return a path based on the module and extension.

        Arguments:
            module: string containing some corpus module
            extension: string containing a file extension
        """
        return os.path.join(self.pathcomponents.root,
                            module,
                            self.pathcomponents.lang,
                            self.pathcomponents.genre,
                            self.pathcomponents.subdirs,
                            self.pathcomponents.basename + extension)

    @property
    def converted(self):
        """Return the path to the converted file."""
        module = 'converted'
        if self.md.get_variable('conversion_status') == 'correct':
            module = 'goldstandard/converted'

        return self.name(module, '.xml')

    @property
    def prestable_converted(self):
        """Return the path to the prestable/converted file."""
        module = 'prestable/converted'
        if self.md.get_variable('conversion_status') == 'correct':
            module = 'prestable/goldstandard/converted'

        return self.name(module, '.xml')

    @property
    def analysed(self):
        """Return the path to analysed file."""
        return self.name('analysed', '.xml')
