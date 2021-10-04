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
#   Copyright © 2013-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to change names of corpus files."""


import getpass
import os
import pwd

import git
import pysvn


class VersionControlError(Exception):
    """Raise this exception when errors arise in this module."""

    pass


class VersionController:
    """A very basic version control class."""

    def __init__(self):
        """Initialise the VersionController class."""
        # non-repo config to get at global values
        self.config = git.GitConfigParser(
            [os.path.normpath(os.path.expanduser("~/.gitconfig"))], read_only=True
        )

    def add(self, path):
        """Meta function."""
        raise NotImplementedError("You have to subclass and override add")

    def move(self, oldpath, newpath):
        """Meta function."""
        raise NotImplementedError("You have to subclass and override move")

    def remove(self, path):
        """Meta function."""
        raise NotImplementedError("You have to subclass and override remove")

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

        Args:
            svnclient (pysvn.Client): an svn client to control the
                working copy.
        """
        super().__init__()
        self.client = svnclient

    def add_path(self, path):
        """Add a single path to the working copy.

        Args:
            path (str): path to a file or directory
        """
        valid_path = self.valid_svn_path(path)
        self.client.add(valid_path, recurse=True, force=True)
        if valid_path.endswith(".xsl"):
            self.client.propset("svn:mime-type", "text/xml", valid_path)

    def valid_svn_path(self, path):
        """Find the part of the path that is under version control.

        Args:
            path (str): path that should be added to the working copy

        Returns:
            str: path to the first unversioned part of the path
        """
        child = os.path.basename(path)
        parent = os.path.dirname(path)
        while not self.under_version_control(parent):
            child = os.path.basename(parent)
            parent = os.path.dirname(parent)

        return os.path.join(parent, child)

    def under_version_control(self, path):
        """Check if path is under version control.

        Args:
            path (str): path that should be checked.

        Returns:
            bool: True if under version control, False otherwise
        """
        try:
            status = self.client.status(path)[0].text_status
        except pysvn.ClientError:
            return False
        else:
            return status not in (
                pysvn.wc_status_kind.added,
                pysvn.wc_status_kind.unversioned,
                pysvn.wc_status_kind.ignored,
            )

    def add(self, path):
        """Add path to the working copy.

        Args:
            path (str or list of str): path may be a list of paths or a
                single path
        """
        if isinstance(path, list):
            for p in path:
                self.add_path(p)
        else:
            self.add_path(path)

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
        """Initialise the GIT class.

        Args:
            gitrepo (git.Repo): client to control the git repo
        """
        super().__init__()
        self.gitrepo = gitrepo
        self.config = self.gitrepo.config_reader()

    def add(self, path):
        """Add path to the repo.

        Args:
            path (str): path that should be added to the git repo.
        """
        self.gitrepo.git.add(path)

    def move(self, oldpath, newpath):
        """Move a file within the repo.

        Args:
            oldpath (src): path of the file that should be moved
            newpath (scr): new path of the file to be moved
        """
        self.gitrepo.git.mv(oldpath, newpath)

    def remove(self, path):
        """Remove a file from the repo.

        Args:
            path (src); path of the file that should be removed.
        """
        self.gitrepo.git.rm(path)


def vcs(directory):
    """Make a version control client.

    Args:
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
                "{} is neither a SVN working repository or a Git repo. "
                "Files can only be added to a version controlled "
                "directory.".format(directory)
            )
