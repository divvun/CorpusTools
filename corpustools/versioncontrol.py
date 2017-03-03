# -*- coding:utf-8 -*-

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
#   Copyright © 2013-2017 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Classes and functions to change names of corpus files."""


from __future__ import absolute_import, print_function

import getpass
import os
import pwd

import git
import pysvn


class VersionControlError(Exception):
    """Raise this exception when errors arise in this module."""

    pass


class VersionController(object):
    """A very basic version control class."""

    def __init__(self):
        """Initialise the VersionController class."""
        # non-repo config to get at global values
        self.config = git.GitConfigParser(
            [os.path.normpath(os.path.expanduser("~/.gitconfig"))],
            read_only=True)

    def add(self, path):
        """Meta function."""
        raise NotImplementedError(
            "You have to subclass and override add")

    def move(self, oldpath, newpath):
        """Meta function."""
        raise NotImplementedError(
            "You have to subclass and override move")

    def remove(self, path):
        """Meta function."""
        raise NotImplementedError(
            "You have to subclass and override remove")

    def user_name(self):
        """Try to get a username."""
        if self.config.has_option("user", "name"):
            return self.config.get("user", "name")
        else:
            pwnam = pwd.getpwnam(getpass.getuser()).pw_gecos
            if pwnam is not None:
                return pwnam
            else:
                return ""

    def user_email(self):
        """Try to get the users email."""
        if self.config.has_option("user", "email"):
            return self.config.get("user", "email")
        else:
            return ""


class SVN(VersionController):
    """Implement basic svn functionality."""

    def __init__(self, svnclient):
        """Initialise the SVN class.

        svnclient is a pysvn.Client
        """
        super(SVN, self).__init__()
        self.client = svnclient

    def add(self, path):
        """Add a file to the working copy."""
        if self.client.info(path) is None:
            self.client.add(path)

    def move(self, oldpath, newpath):
        """Move file in the working copy."""
        if self.client.info(oldpath) is not None:
            self.client.move(oldpath, newpath)

    def remove(self, path):
        """Remove a file from the working copy."""
        if self.client.info(path) is not None:
            self.client.remove(path)


class GIT(VersionController):
    """Implement basic git functionality."""

    def __init__(self, gitrepo):
        super(GIT, self).__init__()
        self.gitrepo = gitrepo
        self.config = self.gitrepo.config_reader()

    def add(self, path):
        self.gitrepo.git.add(path)

    def move(self, oldpath, newpath):
        self.gitrepo.git.mv(oldpath, newpath)

    def remove(self, path):
        self.gitrepo.git.rm(path)


def vcs(directory):
    """Make a version control client.

    Arguments:
        directory (str): the directory where the working copy is found.

    Returns:
        Either the SVN or the GIT class.
    """
    try:
        svn_client = pysvn.Client()
        svn_client.info(directory)
        return SVN(svn_client)
    except pysvn.ClientError:
        try:
            git_repo = git.Repo(directory)
            return GIT(git_repo)
        except git.exc.InvalidGitRepositoryError:
            raise VersionControlError(
                '{} is neither a SVN working repository or a Git repo. '
                'Files can only be added to a version controlled '
                'directory.'.format(directory))
