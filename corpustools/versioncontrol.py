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
import pwd
import getpass


class VersionController(object):
    def __init__(self):
        # non-repo config to get at global values
        self.config = git.GitConfigParser([os.path.normpath(os.path.expanduser("~/.gitconfig"))], read_only=True)

    def add(self, filename):
        pass

    def user_name(self):
        if self.config.has_option("user", "name"):
            return self.config.get("user", "name")
        else:
            pwnam = pwd.getpwnam(getpass.getuser()).pw_gecos
            if pwnam is not None:
                return pwnam
            else:
                return ""

    def user_email(self):
        if self.config.has_option("user", "email"):
            return self.config.get("user", "email")
        else:
            return ""

class SVN(VersionController):
    def __init__(self, svnclient):
        '''svnclient is a pysvn.Client
        '''
        super(SVN, self).__init__()
        self.client = svnclient

    def add(self, filename):
        try:
            self.client.add(filename)
            if filename.endswith('.xsl'):
                self.client.propset('svn:mime-type', 'text/plain', filename)
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
        super(GIT, self).__init__()
        self.gitrepo = gitrepo
        self.config = self.gitrepo.config_reader()

    def add(self, filename):
        if os.path.exists(filename):
            self.gitrepo.git.add(filename)
        else:
            print >>sys.stderr, 'File does not exist %s' % filename
            raise UserWarning


class VersionControlFactory(object):
    def vcs(self, directory):
        try:
            s = pysvn.Client()
            s.info(directory)
            return SVN(s)
        except pysvn.ClientError:
            try:
                r = git.Repo(directory)
                return GIT(r)
            except git.exc.InvalidGitRepositoryError:
                print >>sys.stderr, ' %s is not a SVN working \
repository or a Git repo. Files can only be added to a \
version controlled directory.' % directory
                raise UserWarning
