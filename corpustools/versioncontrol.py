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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to change names of corpus files."""


import getpass
import os
import pwd

import git


class VersionControlError(Exception):
    """Raise this exception when errors arise in this module."""


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
            path (src): path of the file that should be removed.
        """
        self.gitrepo.git.rm(path)


def vcs(directory):
    """Make a version control client.

    Args:
        directory (str): the directory where the working copy is found.

    Returns:
        (GIT): A GIT class instance.

    Raises:
        VersionControlError: If the given directory is not a git repository
    """
    try:
        git_repo = git.Repo(directory)
        return GIT(git_repo)
    except git.exc.InvalidGitRepositoryError:
        raise VersionControlError(
            f"{directory} is not a Git repo. Files can only be added to a git repo."
        )
