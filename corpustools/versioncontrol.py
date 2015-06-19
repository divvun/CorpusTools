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
#   Copyright 2013-2015 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import print_function

import os
import sys

import getpass
import git
import pwd
import pysvn


class VersionController(object):
    def __init__(self):
        # non-repo config to get at global values
        self.config = git.GitConfigParser(
            [os.path.normpath(os.path.expanduser("~/.gitconfig"))],
            read_only=True)

    def add(self, path):
        raise NotImplementedError(
            "You have to subclass and override add")

    def move(self, oldpath, newpath):
        raise NotImplementedError(
            "You have to subclass and override move")

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
        '''svnclient is a pysvn.Client'''
        super(SVN, self).__init__()
        self.client = svnclient

    def add(self, path):
        self.client.add(path)

    def move(self, oldpath, newpath):
        self.client.move(oldpath, newpath)


class GIT(VersionController):
    def __init__(self, gitrepo):
        super(GIT, self).__init__()
        self.gitrepo = gitrepo
        self.config = self.gitrepo.config_reader()

    def add(self, path):
        self.gitrepo.git.add(path)

    def move(self, oldpath, newpath):
        self.gitrepo.git.mv(oldpath, newpath)


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
                print(
                    '{} is not a SVN working repository or a Git repo. '
                    'Files can only be added to a version controlled '
                    'directory.'.format(directory), file=sys.stderr)
                raise UserWarning
