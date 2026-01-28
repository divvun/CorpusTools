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
#   Copyright © 2014-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Utility functions and classes used by other modules in CorpusTools."""

import concurrent.futures
import concurrent.futures.process
import datetime
import hashlib
import inspect
import operator
import os
import os.path
import platform
import subprocess
import sys
import time
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from lxml import etree

if TYPE_CHECKING:
    from corpustools.corpuspath import CorpusPath


class SetupError(Exception):
    """This exception is raised when setup is faulty."""


class ExecutableMissingError(Exception):
    """This exception is raised when wanted executables are missing."""


class ArgumentError(Exception):
    """This exception is raised when argument errors occur."""


class ConversionError(Exception):
    """Raise this exception when conversions error occur."""


def print_frame(debug="", *args):
    """Print debug output."""
    # 0 represents this line, 1 represents line at caller
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    print(info.lineno, info.function, debug, file=sys.stderr, end=" ")
    for arg in args:
        print(arg, file=sys.stderr, end=" ")
    print(file=sys.stderr)


def basename_noext(fname, ext):
    """Get the basename without the extension.

    Args:
        fname (str): path to the file.
        ext (str): the extension that should be removed.

    Returns:
        (str): fname without the extension.
    """
    return os.path.basename(fname)[: -len(ext)]


def sort_by_value(table, reverse=False):
    """Sort the table by value.

    Args:
        table (dict): the dictionary that should be sorted.
        reverse (bool): whether or not to sort in reverse

    Returns:
        (dict): sorted by value.
    """
    return sorted(table.items(), key=operator.itemgetter(1), reverse=reverse)


def replace_all(replacements, string):
    """Replace unwanted strings with wanted strings.

    Args:
        replacements (list of tuple): unwanted:wanted string pairs.
        string (str): the string where replacements should be done.

    Returns:
        (str): string with replaced strings.
    """
    for unwanted, wanted in replacements:
        string = string.replace(unwanted, wanted)

    return string


def is_executable(fullpath):
    """Check if the program in fullpath is executable.

    Args:
        fullpath (str): the path to the program or script.

    Returns:
        (bool): True if fullpath contains a executable, False otherwise.
    """
    return os.path.isfile(fullpath) and os.access(fullpath, os.X_OK)


def path_possibilities(program):
    """Check if program is found in $PATH.

    Args:
        program (str): name of program of script.

    Yields:
        (str): possible fullpath to the program
    """
    return (
        os.path.join(path.strip('"'), program)
        for path in os.environ["PATH"].split(os.pathsep)
    )


def executable_in_path(program):
    """Check if program is in path.

    Args:
        program (str): name of the program

    Returns:
        (bool): True if program is found, False otherwise.
    """
    fpath, _ = os.path.split(program)
    if fpath:
        return is_executable(program)
    else:
        return any(
            is_executable(possible_path)
            for possible_path in path_possibilities(program)
        )


def sanity_check(program_list):
    """Look for programs and files that are needed to do the analysis.

    If they don't exist, raise an exception.
    """
    if "GTHOME" not in os.environ:
        raise SetupError(
            "You have to set the environment variable GTHOME "
            "to your checkout of langtech/trunk!"
        )
    for program in program_list:
        if executable_in_path(program) is False:
            raise ExecutableMissingError(
                f"Please install {program}, can not continue without it."
            )


def get_lang_resource(lang, resource, fallback=None):
    """Get a language resource.

    Args:
        lang (str): the language of the resource.
        resource (str): the resource that is needed.
        fallback (str or None): the fallback resource. Default is None.

    Returns:
        (str): path to the resource or fallback.
    """
    path = os.path.join(os.environ["GTHOME"], "langs", lang, resource)
    if os.path.exists(path):
        return path
    else:
        return fallback


def get_preprocess_command(lang):
    """Get the complete proprocess command for lang.

    Args:
        lang (str): the language

    Returns:
        (list[str]): the complete preprocess command.
    """
    preprocess_script = os.path.join(os.environ["GTHOME"], "gt/script/preprocess")
    sanity_check([preprocess_script])
    abbr_fb = get_lang_resource("sme", "tools/preprocess/abbr.txt")
    abbr = get_lang_resource(lang, "tools/preprocess/abbr.txt", abbr_fb)
    return [preprocess_script, f"--abbr={abbr}"]


def lineno():
    """Return the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def print_element(element: etree.Element, level: int, indent: int) -> list[str]:
    """Format an html document.

    This function formats html documents for readability, to see
    the structure of the given document. It ruins white space in
    text parts.

    Args:
        element: the element to format.
        level: indicate at what level this element is.
        indent: indicate how many spaces this element should be indented
    Returns:
        formatted element as list of strings.
    """
    tag = element.tag.replace("{http://www.w3.org/1999/xhtml}", "")

    strings:list[str] = []
    strings.append(" " * (level * indent))
    strings.append(f"<{tag}")

    for k, v in element.attrib.items():
        strings.append(" ")
        if isinstance(k, str):
            strings.append(k)
        else:
            strings.append(k)
        strings.append('="')
        if isinstance(v, str):
            strings.append(v)
        else:
            strings.append(v)
        strings.append('"')
    strings.append(">\n")

    if element.text is not None and element.text.strip() != "":
        strings.append(" " * ((level + 1) * indent))
        strings.append(element.text.strip())
        strings.append("\n")

    for child in element:
        print_element(child, level + 1, indent, out)

    strings.append(" " * (level * indent))
    strings.append(f"</{tag}>\n")

    if level > 0 and element.tail is not None and element.tail.strip() != "":
        for _ in range(0, (level - 1) * indent):
            strings.append(" ")
        strings.append(element.tail.strip())
        strings.append("\n")

    return strings

def name_to_unicode(filename):
    """Turn a filename to a unicode string.

    Args:
        filename (str): name of the file

    Returns:
        (str): A unicode string.
    """
    if platform.system() == "Windows":
        return filename
    else:
        return filename.decode("utf-8")


def note(msg):
    """Print msg to stderr.

    Args:
        msg (str): the message
    """
    print(msg, file=sys.stderr)


@contextmanager
def ignored(*exceptions):
    """Ignore exceptions."""
    try:
        yield
    except exceptions:
        pass


class ExternalCommandRunner:
    """Class to run external command through subprocess.

    Attributes:
        stdout: save the stdout of the command here.
        stderr: save the stderr of the command here.
        returncode: save the returncode of the command here.
    """

    def __init__(self):
        """Initialise the ExternalCommandRunner class."""
        self.stdout = None
        self.stderr = None
        self.returncode = None

    def run(self, command, cwd=None, to_stdin=None):
        """Run the command, save the result."""
        try:
            subp = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
            )
        except OSError:
            raise ExecutableMissingError(
                f"Please install {command[0]}, can not continue without it."
            ) from None

        (self.stdout, self.stderr) = subp.communicate(to_stdin)
        self.returncode = subp.returncode


def human_readable_filesize(num, suffix="B"):
    """Returns human readable filesize"""
    # https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def human_readable_timespan(seconds):
    return str(datetime.timedelta(seconds=seconds))


_PARA_DEFAULT_MSG_FORMAT = (
    "[{file_number} / {nfiles} files processed "
    "({bytes_processed} / {bytes_total}, {processing_speed}/s)"
    " - est. time left: {timeleft}]\n"
    "  {status}: {filename}"
)


# TODO use real types, not strings. but there is a circuar import
def run_in_parallel(
    function: Callable[["CorpusPath"], None],
    max_workers: int,
    file_list: list["CorpusPath"],
    file_sizes: list[int],
    msg_format: str = _PARA_DEFAULT_MSG_FORMAT,
    *args: list[Any],
    **kwargs: dict[str, Any],
):
    """Run function as many times as there are files in the `file_list`,
    in parallel. Each invocation gets one element of the `file_list`.

    Conceptually, it's like `function(file) for file in file_list`, but
    in parallel. Uses a ProcessPoolExecutor with `max_workers`.

    Any additional arguments (positional or keyword) given to
    `run_in_parallel`, will be passed along to the `function`.

    Args:
        function (Callable): The function to call. The first argument to
            the function is the file path.
        max_workers (int): How many worker processes to use
        file_list (list[str]): The list of files (full paths)
    """
    total_size = sum(file_sizes)
    nfiles = len(file_list)
    n_failed = 0
    t0 = time.monotonic_ns()
    print(
        f"Processing {nfiles} files ({human_readable_filesize(total_size)}) "
        f"in parallel using {max_workers} workers"
    )

    futures = {}  # future -> (filepath, filesize)

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
            for file, filesize in zip(file_list, file_sizes, strict=False):
                fut = pool.submit(function, file, *args, **kwargs)
                futures[fut] = (file, filesize)

            completed_bytes = 0

            completed = concurrent.futures.as_completed(futures)
            for i, future in enumerate(completed, start=1):
                (filename, filesize) = futures.pop(future)
                completed_bytes += filesize
                bytes_remaining = total_size - completed_bytes
                secs_passed = (time.monotonic_ns() - t0) / 1_000_000_000
                bytes_processed_per_sec = completed_bytes / secs_passed

                # anders: this is so crude as to almost be pointless
                # but -- due to the way it works, it at least gives more of
                # an upper bound than a lower bound quite quickly into the
                # processing, which at least is something
                # -> because in the beginning, bytes_processed_per_sec doesn't
                # take into account that there are other processes also
                # working, which means bytes_completed is an underestimate on
                # how many bytes of processing has been done in total
                # -> but the more files are completed, the better the estimate
                # is going to be
                est_remaining_seconds = int(bytes_remaining / bytes_processed_per_sec)

                exc = future.exception()
                if exc is None:
                    status = "done"
                else:
                    status = "FAILED"
                    n_failed += 1

                msg = msg_format.format(
                    filename=filename,
                    file_number=i,
                    nfiles=nfiles,
                    bytes_processed=human_readable_filesize(completed_bytes),
                    bytes_total=human_readable_filesize(total_size),
                    processing_speed=human_readable_filesize(bytes_processed_per_sec),
                    timeleft=human_readable_timespan(est_remaining_seconds),
                    status=status,
                )
                print(msg)
                if exc is not None:
                    print(exc)
                    print(traceback.format_exc())
    except concurrent.futures.process.BrokenProcessPool:
        n_remaining = len(futures)
        n_done = nfiles - n_remaining - n_failed
        print("error: Processing was terminated unexpectedly!")
        print(f"{n_done} files were completed, {n_failed} files failed, and ")
        print(f"{n_remaining} didn't start processing, and still remains")
    except KeyboardInterrupt:
        n_remaining = len(futures)
        n_done = nfiles - n_remaining - n_failed
        print("Cancelled by user")
        print(f"{n_done} files were completed, {n_failed} files failed, and ")
        print(f"{n_remaining} didn't start processing, and still remains")
    else:
        n_ok = nfiles - n_failed
        print(f"all done. {n_ok} files ok, {n_failed} failed")


def make_digest(bytestring: bytes) -> str:
    """Make a md5 hash to identify possible dupes."""
    hasher = hashlib.md5()
    hasher.update(bytestring)
    return hasher.hexdigest()


def lang_resource_dirs(lang: str) -> list[Path]:
    """Get the path to the language resources.

    Args:
        lang: the language that modes is asked to serve.

    Returns:
        A path to the zpipe file.
    """
    return [
        prefix / "share" / "giella" / lang
        for prefix in [
            Path().home() / ".local",
            Path("/usr/local"),
            Path("/usr"),
        ]
    ]


def run_external_command(command: list[str], instring: str) -> str:
    """Run the command with input using subprocess.

    Args:
        command: a subprocess compatible command.
        instring: the input to the command.

    Returns:
        Analysed text.

    Raises:
        UserWarning: if the command fails.
    """
    runner = ExternalCommandRunner()
    runner.run(command, to_stdin=instring.encode("utf8"))

    if runner.stderr:
        raise UserWarning(f"{' '.join(command)} failed:\n{runner.stderr}")

    return runner.stdout.decode("utf8")
