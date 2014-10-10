# -*- coding:utf-8 -*-

#
#   This file contains routines to change names of corpus files
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
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys

import pysvn
import git


class VersionController(object):
    def __init__(self):
        pass

    def add(self, filename):
        pass


class SVN(VersionController):
    def __init__(self, svnclient):
        self.client = svnclient

    def add(self, filename):
        try:
            self.client.add(filename)
        except pysvn.ClientError:
            self.add_directory(os.path.dirname(filename))

    def add_directory(self, directory):
        try:
            self.client.status(directory)
        except pysvn.ClientError:
            self.add_directory(os.path.dirname(directory))
            self.client.add(os.path.dirname(directory))


class GIT(VersionController):
    def __init__(self, gitrepo):
        self.gitrepo = gitrepo

    def add(self, filename):
        self.gitrepo.git.add(filename)


class VersionControlFactory(object):
    def vcs(self, directory):
        try:
            s = pysvn.Client()
            s.status(directory)
            return SVN(s)
        except pysvn.ClientError:
            try:
                r = git.Repo(directory)
                return GIT(r)
            except git.exc.InvalidGitRepositoryError:
                print >>sys.stderr, directory, 'is not a SVN working \
repository or a Git repo. Files can only be added to a \
version controlled directory.'
                raise UserWarning
