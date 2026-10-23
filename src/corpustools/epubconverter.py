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
#   Copyright © 2012-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert epub documents to the Giella xml format.

Epub files are zip files that contain text in xhtml files. This class reads
all xhtml files found in this archive. The body element of these files are
converted to div elements, and appended inside a new body element.

It is possible to filter away ranges of elements from this new xhtml file.
These ranges consist pairs of xpath paths, specified inside the metadata
file that belongs to this epub file.
"""

from pathlib import Path
from typing import Iterator

from epub import Book, BookChapter, open_epub  # type: ignore
from lxml import etree

from corpustools.util import ConversionError
from corpustools.xslsetter import MetadataHandler


def read_chapter(chapter: BookChapter) -> etree._Element:
    """Read the contents of a epub_file chapter.

    Args:
        chapter: the chapter of an epub file

    Returns:
        The contents of a chapter

    Raises:
        util.ConversionException: on conversion error
    """
    try:
        return etree.fromstring(chapter.read())
    except KeyError as error:
        raise ConversionError(error) from error


def chapters(book: Book, metadata: MetadataHandler) -> Iterator[etree._Element]:
    """Get the all linear chapters of the epub book.

    Args:
        book: The epub book element

    Yields:
        The body of an xhtml file found in the epub file.
    """
    excluded = metadata.epub_excluded_chapters
    for index, chapter in enumerate(book.chapters):
        if index not in excluded:
            chapterbody = read_chapter(chapter).find(
                "{http://www.w3.org/1999/xhtml}body"
            )
            if chapterbody is not None:
                chapterbody.tag = "{http://www.w3.org/1999/xhtml}div"
                yield chapterbody


def extract_content(filename: Path, metadata: MetadataHandler) -> etree._Element:
    """Extract content from the epub file.

    Args:
        filename: path to the document

    Returns:
        The content of the epub file wrapped in html element
    """
    mainbody = etree.Element("{http://www.w3.org/1999/xhtml}body")
    html = etree.Element("{http://www.w3.org/1999/xhtml}html")
    html.append(etree.Element("{http://www.w3.org/1999/xhtml}head"))
    html.append(mainbody)

    book = Book(open_epub(filename))

    for chapterbody in chapters(book, metadata):
        mainbody.append(chapterbody)

    return html


def remove_ranges(metadata: MetadataHandler, html: etree._Element) -> None:
    """Remove ranges of html elements."""
    if metadata.skip_elements:
        for pairs in metadata.skip_elements:
            remove_range(pairs[0], pairs[1], html)


def to_html_elt(filename: Path) -> etree._Element:
    """Append all chapter bodies as divs to an html file.

    Returns:
        An etree.Element containing the content of all xhtml files found in
        the epub file as one xhtml document.
    """
    filename = filename.with_suffix(filename.suffix + ".xsl")
    metadata = MetadataHandler(filename, create=True)
    html = extract_content(filename, metadata)
    try:
        remove_ranges(metadata, html)
    except AttributeError as error:
        raise ConversionError(
            "Check that skip_elements in the metadata file has the correct format"
        ) from error

    return html


def remove_siblings_shorten_path(
    parts: list[str], content: etree._Element, preceding: bool = False
) -> list[str]:
    """Remove all siblings before or after an element.

    Args:
        parts: a xpath path split on /
        content: an xhtml document
        preceding: When True, iterate through the preceding siblings
            of the found element, otherwise iterate throughe the following
            siblings.

    Returns:
        The path to the parent of parts.
    """
    path = "/".join(parts)
    found = content.find(path, namespaces={"html": "http://www.w3.org/1999/xhtml"})
    if found is not None:
        parent = found.getparent()
        if parent is not None:
            for sibling in found.itersiblings(preceding=preceding):
                parent.remove(sibling)

    return parts[:-1]


def shorten_longest_path(
    path1: str, path2: str, content: etree._Element
) -> tuple[list[str], list[str]]:
    """Remove elements from the longest path.

    If starts is longer than ends, remove the siblings following starts,
    shorten starts with one step (going to the parent). If starts still is
    longer than ends, remove the siblings following the parent. This is
    done untill starts and ends are of equal length.

    If on the other hand ends is longer than starts, remove the siblings
    preceding ends, then shorten ends (going to its parent).

    Args:
        path1: path to first element
        path2: path to second element
        content: xhtml document, where elements are removed.

    Returns:
        Paths to the new start and end element, now with the same length.
    """
    starts, ends = path1.split("/"), path2.split("/")

    while len(starts) > len(ends):
        starts = remove_siblings_shorten_path(starts, content)

    while len(ends) > len(starts):
        ends = remove_siblings_shorten_path(ends, content, preceding=True)

    return starts, ends


def remove_trees_1(
    path1: str, path2: str, content: etree._Element
) -> tuple[list[str], list[str]]:
    """Remove tree nodes that do not have the same parents.

    While the parents in starts and ends are unequal (that means that
    starts and ends belong in different trees), remove elements
    following starts and preceding ends. Shorten the path to the parents
    of starts and ends and remove more elements if needed. starts and
    ends are of equal length.

    Args:
        path1: path to first element
        path2: path to second element
        content: xhtml document, where elements are removed.

    Returns:
        Paths to the new start and end element.
    """
    starts, ends = shorten_longest_path(path1, path2, content)

    while starts[:-1] != ends[:-1]:
        starts = remove_siblings_shorten_path(starts, content)
        ends = remove_siblings_shorten_path(ends, content, preceding=True)

    return starts, ends


def remove_trees_2(starts: list[str], ends: list[str], content: etree._Element) -> None:
    """Remove tree nodes that have the same parents.

    Now that the parents of starts and ends are equal, remove the last
    trees of nodes between starts and ends (if necessary).

    Args:
        starts: path to first element
        ends: path to second element
        content: xhtml document, where elements are removed.
    """
    deepest_start = content.find(
        "/".join(starts), namespaces={"html": "http://www.w3.org/1999/xhtml"}
    )
    deepest_end = content.find(
        "/".join(ends), namespaces={"html": "http://www.w3.org/1999/xhtml"}
    )
    if deepest_start is not None:
        parent = deepest_start.getparent()
        for sibling in deepest_start.itersiblings():
            if sibling == deepest_end:
                break
            elif parent is not None:
                parent.remove(sibling)


def remove_first_element(path1: str, content: etree._Element) -> None:
    """Remove the first element in the range.

    Args:
        path1: path to the first element to remove.
        content: the xhtml document that should be altered.
    """
    first_start = content.find(
        path1, namespaces={"html": "http://www.w3.org/1999/xhtml"}
    )
    if first_start is not None:
        parent = first_start.getparent()
        if parent is not None:
            parent.remove(first_start)


def remove_range(path1: str, path2: str, content: etree._Element) -> None:
    """Remove a range of elements from an xhtml document.

    Args:
        path1: path to first element
        path2: path to second element
        content: xhtml document
    """
    if path2:
        starts, ends = remove_trees_1(path1, path2, content)
        remove_trees_2(starts, ends, content)
        remove_first_element(path1, content)
    else:
        found = content.find(path1, namespaces={"html": "http://www.w3.org/1999/xhtml"})
        if found is not None:
            parent = found.getparent()
            if parent is not None:
                parent.remove(found)
