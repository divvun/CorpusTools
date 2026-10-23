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
#   Copyright © 2013-2026 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to change names of corpus files."""

from pathlib import Path

import git


class VersionControlError(Exception):
    """Raise this exception when errors arise in this module."""


class VersionController:
    """Implement basic git functionality."""

    def __init__(self, directory: Path):
        """Initialize the VersionController.

        Args:
            directory: client to control the git repo
        """
        self.gitrepo = git.Repo(directory)

    def add(self, path: Path | list[Path]):
        """Add path to the repo.

        Args:
            path: path that should be added to the git repo.
        """
        if isinstance(path, list):
            path_len = len(path)
            start = 0
            end = 200
            self.gitrepo.git.add(path[:end])
            while path_len > end:
                start = end
                end += 200
                self.gitrepo.git.add(path[start:end])
        else:
            self.gitrepo.git.add(path)

    def move(self, oldpath: Path, newpath: Path):
        """Move a file within the repo.

        Args:
            oldpath: path of the file that should be moved
            newpath: new path of the file to be moved
        """
        self.gitrepo.git.mv(oldpath, newpath)

    def remove(self, path: Path) -> None:
        """Remove a file from the repo.

        Args:
            path: path of the file that should be removed.
        """
        self.gitrepo.git.rm(path)


def vcs(directory: Path) -> VersionController:
    """Make a version control  client.

    Args:
        directory: the directory where the working copy is found.

    Returns:
        A VersionController instance.

    Raises:
        VersionControlError: If the given directory is not a git repository
    """
    try:
        return VersionController(directory)
    except git.InvalidGitRepositoryError as err:
        raise VersionControlError(
            f"{directory} is not a Git repo. Files can only be added to a git repo."
        ) from err
