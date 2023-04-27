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
#   Copyright © 2013-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Navneskifte

orig = CorpusPath(orig)
ø1 = CorpusPath(ønsket navn)
ø2 = normaliser(ø1) -> endret basename
ø3 = nyttnavnhvisikkeduplikat(ø2) -> endret basename

"""

import os
import unittest

import git
import pytest

from corpustools import corpuspath, namechanger, xslsetter
from pathlib import Path

here = os.path.dirname(__file__)


@pytest.mark.parametrize(
    "orig, expected",
    [
        ("ášŧŋđžčåøæöäï+", "astngdzcaoaeoai_"),
        ("ÁŠŦŊĐŽČÅØÆÖÄÏ+", "astngdzcaoaeoai_"),
        ("ášŧŋđŽČÅØÆÖÄï+", "astngdzcaoaeoai_"),
        ("YoullNeverWalkAlone", "youllneverwalkalone"),
        ("Youll Never Walk Alone", "youll_never_walk_alone"),
        ("You'll Never Walk Alone", "you_ll_never_walk_alone"),
        ("Šaddágo beaivi vai idja", "saddago_beaivi_vai_idja"),
        ('aba".txt', "aba_.txt"),
        ("aba<.txt", "aba_.txt"),
        ("aba>.txt", "aba_.txt"),
        ("__aba.txt", "aba.txt"),
        ("--aba.txt", "aba.txt"),
        ("--__aba.txt", "aba.txt"),
        (
            (
                "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦ‌​ЧШЩЪЫЬЭЮЯ.txt"
            ),
            (
                "abvgdeiozhziiklmnoprstufkhtschshshch_y_eiuia"
                "abvgdeiozhziiklmnoprstufkhts_chshshch_y_eiuia.txt"
            ),
        ),
    ],
)
def test_filename_to_ascii(orig, expected):
    """Check that non ascii filenames are converted to ascii only ones."""
    assert namechanger.normalise_filename(orig) == expected


def test_own_name_with_complete_path():
    with pytest.raises(namechanger.NamechangerError):
        namechanger.normalise_filename("j/a/b/c/aba>.txt")


@pytest.fixture(scope="session")
def dupe_setup(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("data")
    files = (
        tmpdir.with_name("old_dupe.txt"),
        tmpdir.with_name("new_dupe.txt"),
        tmpdir.with_name("none_dupe.txt"),
    )
    files[0].write_text("a")
    files[1].write_text("a")
    files[2].write_text("b")

    return files


def test_are_duplicate_nonexisting_file():
    """If one or none of the files do not exist, return False"""
    assert namechanger.are_duplicates("old.txt", "new.txt") == False


def test_are_duplicate_equal_files(dupe_setup):
    """Both files exist, with same content, return True"""
    assert (
        dupe_setup[0].exists()
        and dupe_setup[1].exists()
        and namechanger.are_duplicates(dupe_setup[0], dupe_setup[1]) == True
    )


def test_are_duplicate_unequal_files(dupe_setup):
    """Both files exist, not same content, return False"""
    assert (
        dupe_setup[0].exists()
        and dupe_setup[2].exists()
        and namechanger.are_duplicates(
            dupe_setup[0],
            dupe_setup[2],
        )
        == False
    )


@pytest.fixture(scope="session")
def newbasename(tmp_path_factory):
    corpus_dir = tmp_path_factory.mktemp("corpus-sme-orig")
    files = (
        Path(corpus_dir / "admin").with_name("old_dupe.txt"),
        Path(corpus_dir / "admin").with_name("new_dupe.txt"),
        Path(corpus_dir / "admin").with_name("new_none_dupe.txt"),
        Path(corpus_dir / "admin").with_name("new_none_düpe.txt"),
    )
    files[0].write_text("a")
    files[1].write_text("a")
    files[2].write_text("b")
    files[3].write_text("b")

    return files


def test_compute_new_basename_duplicates(tmp_path):
    """What happens when the wanted name is taken, and a duplicate"""
    d = tmp_path / "corpus-sme-orig"
    d.mkdir()
    file1 = d / "old.txt"
    file2 = d / "new.txt"
    file1.write_text("a")
    file2.write_text("a")
    with pytest.raises(UserWarning):
        namechanger.compute_new_basename(
            oldpath=file1,
            wanted_path=file2,
        )


def test_compute_new_basename_same_name(tmp_path):
    """What happens when the suggested name is taken, but not duplicate"""
    corpus_dir = tmp_path / "corpus-sme-orig"
    corpus_dir.mkdir()
    file1 = corpus_dir / "old.txt"
    file2 = corpus_dir / "øld.txt"
    file1.write_text("a")
    file2.write_text("b")

    assert (
        namechanger.compute_new_basename(oldpath=file2, wanted_path=file1)
        == file1.with_name("old_1.txt").as_posix()
    )


def test_compute_movepairs_1(tmp_path):
    """newpath does not exist, no parallels"""
    corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    corpus_dir.mkdir(parents=True)

    mc = namechanger.MovepairComputer()

    file1 = corpus_dir.joinpath("a.txt")
    mc.compute_all_movepairs(
        oldpath=file1.as_posix(),
        newpath=file1.with_stem("b").as_posix(),
    )

    assert mc.filepairs == [
        namechanger.PathPair(
            oldpath=file1.as_posix(),
            newpath=file1.with_stem("b").as_posix(),
        )
    ]


def test_compute_movepairs_2(tmp_path):
    """newpath does not exist, needs normalisation, no parallels"""
    corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    corpus_dir.mkdir(parents=True)

    mc = namechanger.MovepairComputer()
    file1 = corpus_dir.joinpath("æ.txt")
    mc.compute_all_movepairs(
        oldpath=file1.as_posix(),
        newpath=file1.as_posix(),
    )

    assert mc.filepairs == [
        namechanger.PathPair(
            oldpath=file1.as_posix(),
            newpath=file1.with_stem("ae").as_posix(),
        )
    ]


def test_compute_movepairs_3(tmp_path):
    """newpath exists, not duplicate, no parallels"""
    corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    corpus_dir.mkdir(parents=True)
    file1 = corpus_dir.joinpath("a.txt")
    file1.write_text("file1")
    file2 = file1.with_stem("b")
    file2.write_text("file2")

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=file1.as_posix(),
        newpath=file2.as_posix(),
    )

    assert mc.filepairs == [
        namechanger.PathPair(
            oldpath=file1.as_posix(),
            newpath=file1.with_stem("b_1").as_posix(),
        )
    ]


def test_compute_movepairs_4(tmp_path):
    """newpath exists, duplicate, no parallels"""
    corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    corpus_dir.mkdir(parents=True)
    file1 = corpus_dir.joinpath("a.txt")
    file1.write_text("file1")
    file2 = file1.with_stem("b")
    file2.write_text("file1")

    mc = namechanger.MovepairComputer()

    with pytest.raises(UserWarning):
        mc.compute_all_movepairs(
            file1.as_posix(),
            file2.as_posix(),
        )


def test_compute_movepairs_5(tmp_path):
    """move to same directory, with parallels"""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("f.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(),
                newpath=sme_file.with_stem("g").as_posix(),
            ),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=smj_file.as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=sma_file.as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath=sme_file.with_stem("g").as_posix(),
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_6(tmp_path):
    """move to different subdir, with parallels"""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("f.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-sme-orig", "ficti", "bub", "g.txt"
                ).as_posix(),
            ),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-smj-orig", "ficti", "bub", "f.txt"
                ).as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-sma-orig", "ficti", "bub", "f.txt"
                ).as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath=tmp_path.joinpath(
            "corpus-sme-orig", "ficti", "bub", "g.txt"
        ).as_posix(),
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_7(tmp_path):
    """move to different genre, with parallels"""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("f.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-sme-orig", "facta", "sub", "g.txt"
                ).as_posix(),
            ),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-smj-orig", "facta", "sub", "f.txt"
                ).as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=tmp_path.joinpath(
                    "corpus-sma-orig", "facta", "sub", "f.txt"
                ).as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath=tmp_path.joinpath(
            "corpus-sme-orig", "facta", "sub", "g.txt"
        ).as_posix(),
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_8(tmp_path):
    """Move to different genre, one parallel needs normalisation"""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "ø.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("ø.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "ø.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(), newpath=sme_file.with_stem("g").as_posix()
            ),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=smj_file.with_stem("o").as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=sma_file.as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath=sme_file.with_stem("g").as_posix(),
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_9(tmp_path):
    """move to same directory, with parallels.

    Parallel needs normalisation. The new parallel name collides with
    normalised name, but is not a duplicate of it.
    """
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("sma", "ø.txt")
    sme_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("ø.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.write_file()

    sma_file.write_text("content of ø")
    sma_file.with_stem("o").write_text("content of o")

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(),
                newpath=sme_file.with_stem("g").as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=sma_file.with_stem("o_1").as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath=sme_file.with_stem("g").as_posix(),
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_10(tmp_path):
    """newpath is empty, no parallels"""
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_file = sme_corpus_dir.joinpath("a.txt")

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(sme_file.as_posix(), "")

    assert mc.filepairs == [
        namechanger.PathPair(
            sme_file.as_posix(),
            newpath="",
        )
    ]


def test_compute_movepairs_11(tmp_path):
    """newpath is empty, with parallels"""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("f.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "f.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(
                oldpath=sme_file.as_posix(),
                newpath="",
            ),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=smj_file.as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=sma_file.as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath="",
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_compute_movepairs_12(tmp_path):
    """Newpath is empty, one parallel needs normalisation."""
    sma_corpus_dir = tmp_path / "corpus-sma-orig" / "ficti" / "sub"
    sma_corpus_dir.mkdir(parents=True)
    sme_corpus_dir = tmp_path / "corpus-sme-orig" / "ficti" / "sub"
    sme_corpus_dir.mkdir(parents=True)
    smj_corpus_dir = tmp_path / "corpus-smj-orig" / "ficti" / "sub"
    smj_corpus_dir.mkdir(parents=True)

    sme_file = sme_corpus_dir.joinpath("f.txt")
    sme_corpuspath = corpuspath.CorpusPath(sme_file.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("smj", "ø.txt")
    sme_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    sme_corpuspath.metadata.write_file()

    smj_file = smj_corpus_dir.joinpath("ø.txt")
    smj_corpuspath = corpuspath.CorpusPath(smj_file.as_posix())

    smj_corpuspath.metadata.set_variable("mainlang", "smj")
    smj_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    smj_corpuspath.metadata.set_parallel_text("sma", "f.txt")
    smj_corpuspath.metadata.write_file()

    sma_file = sma_corpus_dir.joinpath("f.txt")
    sma_corpuspath = corpuspath.CorpusPath(sma_file.as_posix())

    sma_corpuspath.metadata.set_variable("mainlang", "sma")
    sma_corpuspath.metadata.set_parallel_text("sme", "f.txt")
    sma_corpuspath.metadata.set_parallel_text("smj", "ø.txt")
    sma_corpuspath.metadata.write_file()

    want = sorted(
        [
            namechanger.PathPair(oldpath=sme_file.as_posix(), newpath=""),
            namechanger.PathPair(
                oldpath=smj_file.as_posix(),
                newpath=smj_file.with_stem("o").as_posix(),
            ),
            namechanger.PathPair(
                oldpath=sma_file.as_posix(),
                newpath=sma_file.as_posix(),
            ),
        ]
    )

    mc = namechanger.MovepairComputer()
    mc.compute_all_movepairs(
        oldpath=sme_file.as_posix(),
        newpath="",
    )
    got = sorted(mc.filepairs)

    assert got == want


def test_move_orig(tmp_path):
    """move to different subdir, with parallels."""
    sme_orig = tmp_path / "corpus-sme-orig" / "ficti" / "sub" / "f.txt"
    sme_orig.parent.mkdir(parents=True)
    sme_orig.write_text("content of f")

    sme_corpuspath = corpuspath.CorpusPath(sme_orig.as_posix())

    sme_corpuspath.metadata.set_variable("mainlang", "sme")
    sme_corpuspath.metadata.set_parallel_text("nob", "ø.txt")
    sme_corpuspath.metadata.write_file()

    if not sme_orig.exists():
        raise SystemExit(f"{sme_orig} does not exist")

    sme_converted = Path(sme_corpuspath.converted)
    sme_converted.parent.mkdir(parents=True)
    sme_converted.write_text("converted content of f")

    sme_tmx = Path(sme_corpuspath.tmx("nob"))
    sme_tmx.parent.mkdir(parents=True)
    sme_tmx.write_text("parallelised content of f")

    r1 = git.Repo.init(sme_corpuspath.orig_corpus_dir)
    r1.index.add(["ficti"])
    r1.index.commit("a")

    r2 = git.Repo.init(sme_corpuspath.converted_corpus_dir)
    r2.index.add(["tmx", "converted"])
    r2.index.commit("a")
    cfm = namechanger.CorpusFileMover(
        oldpath=sme_corpuspath.orig,
        newpath=sme_corpuspath.move_orig(genre="facta", subdirs="sub"),
    )
    cfm.move_files()

    new_corpuspath = corpuspath.CorpusPath(
        sme_corpuspath.move_orig(genre="facta", subdirs="sub")
    )
    assert new_corpuspath.orig
    assert new_corpuspath.xsl
    assert new_corpuspath.converted
    assert new_corpuspath.tmx("nob")


# class TestCorpusFileRemover(unittest.TestCase):
#     """Test the CorpusFileRemover class."""

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write("corpus-sme-orig/ficti/sub/f.txt", b"content of f")
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.set_parallel_text("sma", "f.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2sma/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_remove_orig(self):
#         """Remove file, with parallels."""
#         cfm = namechanger.CorpusFileRemover(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")
#         )
#         cfm.remove_files()
#         self.tempdir.check_all(
#             "",
#         )


# class TestCorpusFilesetMetadataUpdater1(unittest.TestCase):
#     """Move to new genre/subdir, with parallels, parallel needs normalisation."""

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write("corpus-sme-orig/ficti/sub/f.txt", b"content of f")
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.set_parallel_text("sma", "f.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2sma/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2sma/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )

#         self.tempdir.makedir("corpus-smj-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-smj-orig/ficti/sub/ø.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/ø.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.set_variable("mainlang", "smj")
#         smj_metadata.set_variable("translated_from", "sme")
#         smj_metadata.set_parallel_text("sme", "f.txt")
#         smj_metadata.set_parallel_text("sma", "f.txt")
#         smj_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "converted content of ø".encode("utf8"),
#         )

#         self.tempdir.makedir("corpus-sma-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-sma-orig/ficti/sub/f.txt", "content of f".encode("utf8")
#         )
#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sma_metadata.set_variable("mainlang", "sma")
#         sma_metadata.set_variable("translated_from", "sme")
#         sma_metadata.set_parallel_text("sme", "f.txt")
#         sma_metadata.set_parallel_text("smj", "ø.txt")
#         sma_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sma/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#         oldpath = os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")
#         newpath = os.path.join(self.tempdir.path, "corpus-sme-orig/facta/bub/g.txt")
#         cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
#         cfm.move_files()
#         cfm.update_own_metadata()
#         cfm.update_parallel_files_metadata()

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_move_fileset(self):
#         """Move a set of files."""
#         self.tempdir.check_all(
#             "",
#             "corpus-sma-orig/",
#             "corpus-sma-orig/facta/",
#             "corpus-sma-orig/facta/bub/",
#             "corpus-sma-orig/facta/bub/f.txt",
#             "corpus-sma-orig/facta/bub/f.txt.xsl",
#             "corpus-sma-orig/ficti/",
#             "corpus-sma-orig/ficti/sub/",
#             "corpus-sme-orig/",
#             "corpus-sme-orig/facta/",
#             "corpus-sme-orig/facta/bub/",
#             "corpus-sme-orig/facta/bub/g.txt",
#             "corpus-sme-orig/facta/bub/g.txt.xsl",
#             "corpus-sme-orig/ficti/",
#             "corpus-sme-orig/ficti/sub/",
#             "corpus-smj-orig/",
#             "corpus-smj-orig/facta/",
#             "corpus-smj-orig/facta/bub/",
#             "corpus-smj-orig/facta/bub/o.txt",
#             "corpus-smj-orig/facta/bub/o.txt.xsl",
#             "corpus-smj-orig/ficti/",
#             "corpus-smj-orig/ficti/sub/",
#             "prestable/",
#             "prestable/converted/",
#             "prestable/converted/sma/",
#             "prestable/converted/sma/facta/",
#             "prestable/converted/sma/facta/bub/",
#             "prestable/converted/sma/facta/bub/f.txt.xml",
#             "prestable/converted/sma/ficti/",
#             "prestable/converted/sma/ficti/sub/",
#             "prestable/converted/sme/",
#             "prestable/converted/sme/facta/",
#             "prestable/converted/sme/facta/bub/",
#             "prestable/converted/sme/facta/bub/g.txt.xml",
#             "prestable/converted/sme/ficti/",
#             "prestable/converted/sme/ficti/sub/",
#             "prestable/converted/smj/",
#             "prestable/converted/smj/facta/",
#             "prestable/converted/smj/facta/bub/",
#             "prestable/converted/smj/facta/bub/o.txt.xml",
#             "prestable/converted/smj/ficti/",
#             "prestable/converted/smj/ficti/sub/",
#             "prestable/tmx/",
#             "prestable/tmx/sme2sma/",
#             "prestable/tmx/sme2sma/facta/",
#             "prestable/tmx/sme2sma/facta/bub/",
#             "prestable/tmx/sme2sma/facta/bub/g.txt.tmx",
#             "prestable/tmx/sme2sma/ficti/",
#             "prestable/tmx/sme2sma/ficti/sub/",
#             "prestable/tmx/sme2smj/",
#             "prestable/tmx/sme2smj/facta/",
#             "prestable/tmx/sme2smj/facta/bub/",
#             "prestable/tmx/sme2smj/facta/bub/g.txt.tmx",
#             "prestable/tmx/sme2smj/ficti/",
#             "prestable/tmx/sme2smj/ficti/sub/",
#             "prestable/toktmx/",
#             "prestable/toktmx/sme2sma/",
#             "prestable/toktmx/sme2sma/facta/",
#             "prestable/toktmx/sme2sma/facta/bub/",
#             "prestable/toktmx/sme2sma/facta/bub/g.txt.toktmx",
#             "prestable/toktmx/sme2sma/ficti/",
#             "prestable/toktmx/sme2sma/ficti/sub/",
#             "prestable/toktmx/sme2smj/",
#             "prestable/toktmx/sme2smj/facta/",
#             "prestable/toktmx/sme2smj/facta/bub/",
#             "prestable/toktmx/sme2smj/facta/bub/g.txt.toktmx",
#             "prestable/toktmx/sme2smj/ficti/",
#             "prestable/toktmx/sme2smj/ficti/sub/",
#         )

#     def test_update_metadata(self):
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/facta/bub/g.txt.xsl")
#         )
#         self.assertEqual(sme_metadata.get_variable("genre"), "facta")
#         self.assertEqual(sme_metadata.get_variable("mainlang"), "sme")
#         sme_parallels = sme_metadata.get_parallel_texts()
#         self.assertEqual(sme_parallels["smj"], "o.txt")
#         self.assertEqual(sme_parallels["sma"], "f.txt")

#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/facta/bub/f.txt.xsl")
#         )
#         self.assertEqual(sma_metadata.get_variable("genre"), "facta")
#         sma_parallels = sma_metadata.get_parallel_texts()
#         self.assertEqual(sma_parallels["smj"], "o.txt")
#         self.assertEqual(sma_parallels["sme"], "g.txt")

#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/facta/bub/o.txt.xsl")
#         )
#         self.assertEqual(smj_metadata.get_variable("genre"), "facta")
#         smj_parallels = smj_metadata.get_parallel_texts()
#         self.assertEqual(smj_parallels["sme"], "g.txt")
#         self.assertEqual(smj_parallels["sma"], "f.txt")


# class TestCorpusFilesetMetadataUpdater2(unittest.TestCase):
#     """move to new lang/genre/subdir, with parallels, parallel needs normalisation"""

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write("corpus-sme-orig/ficti/sub/f.txt", b"content of f")
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.set_parallel_text("sma", "f.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2sma/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2sma/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )

#         self.tempdir.makedir("corpus-smj-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-smj-orig/ficti/sub/ø.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/ø.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.set_variable("mainlang", "smj")
#         smj_metadata.set_variable("translated_from", "sme")
#         smj_metadata.set_parallel_text("sme", "f.txt")
#         smj_metadata.set_parallel_text("sma", "f.txt")
#         smj_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "converted content of ø".encode("utf8"),
#         )

#         self.tempdir.makedir("corpus-sma-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-sma-orig/ficti/sub/f.txt", "content of f".encode("utf8")
#         )
#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sma_metadata.set_variable("mainlang", "sma")
#         sma_metadata.set_variable("translated_from", "sme")
#         sma_metadata.set_parallel_text("sme", "f.txt")
#         sma_metadata.set_parallel_text("smj", "ø.txt")
#         sma_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sma/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#         oldpath = os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")
#         newpath = os.path.join(self.tempdir.path, "corpus-smn-orig/facta/bub/g.txt")
#         cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
#         cfm.move_files()
#         cfm.update_own_metadata()
#         cfm.update_parallel_files_metadata()

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_move_fileset(self):
#         self.tempdir.check_all(
#             "",
#             "corpus-sma-orig/",
#             "corpus-sma-orig/facta/",
#             "corpus-sma-orig/facta/bub/",
#             "corpus-sma-orig/facta/bub/f.txt",
#             "corpus-sma-orig/facta/bub/f.txt.xsl",
#             "corpus-sma-orig/ficti/",
#             "corpus-sma-orig/ficti/sub/",
#             "corpus-sme-orig/",
#             "corpus-sme-orig/ficti/",
#             "corpus-sme-orig/ficti/sub/",
#             "corpus-smj-orig/",
#             "corpus-smj-orig/facta/",
#             "corpus-smj-orig/facta/bub/",
#             "corpus-smj-orig/facta/bub/o.txt",
#             "corpus-smj-orig/facta/bub/o.txt.xsl",
#             "corpus-smj-orig/ficti/",
#             "corpus-smj-orig/ficti/sub/",
#             "corpus-smn-orig/",
#             "corpus-smn-orig/facta/",
#             "corpus-smn-orig/facta/bub/",
#             "corpus-smn-orig/facta/bub/g.txt",
#             "corpus-smn-orig/facta/bub/g.txt.xsl",
#             "prestable/",
#             "prestable/converted/",
#             "prestable/converted/sma/",
#             "prestable/converted/sma/facta/",
#             "prestable/converted/sma/facta/bub/",
#             "prestable/converted/sma/facta/bub/f.txt.xml",
#             "prestable/converted/sma/ficti/",
#             "prestable/converted/sma/ficti/sub/",
#             "prestable/converted/sme/",
#             "prestable/converted/sme/ficti/",
#             "prestable/converted/sme/ficti/sub/",
#             "prestable/converted/smj/",
#             "prestable/converted/smj/facta/",
#             "prestable/converted/smj/facta/bub/",
#             "prestable/converted/smj/facta/bub/o.txt.xml",
#             "prestable/converted/smj/ficti/",
#             "prestable/converted/smj/ficti/sub/",
#             "prestable/converted/smn/",
#             "prestable/converted/smn/facta/",
#             "prestable/converted/smn/facta/bub/",
#             "prestable/converted/smn/facta/bub/g.txt.xml",
#             "prestable/tmx/",
#             "prestable/tmx/sme2sma/",
#             "prestable/tmx/sme2sma/ficti/",
#             "prestable/tmx/sme2sma/ficti/sub/",
#             "prestable/tmx/sme2smj/",
#             "prestable/tmx/sme2smj/ficti/",
#             "prestable/tmx/sme2smj/ficti/sub/",
#             "prestable/tmx/smn2sma/",
#             "prestable/tmx/smn2sma/facta/",
#             "prestable/tmx/smn2sma/facta/bub/",
#             "prestable/tmx/smn2sma/facta/bub/g.txt.tmx",
#             "prestable/tmx/smn2smj/",
#             "prestable/tmx/smn2smj/facta/",
#             "prestable/tmx/smn2smj/facta/bub/",
#             "prestable/tmx/smn2smj/facta/bub/g.txt.tmx",
#             "prestable/toktmx/",
#             "prestable/toktmx/sme2sma/",
#             "prestable/toktmx/sme2sma/ficti/",
#             "prestable/toktmx/sme2sma/ficti/sub/",
#             "prestable/toktmx/sme2smj/",
#             "prestable/toktmx/sme2smj/ficti/",
#             "prestable/toktmx/sme2smj/ficti/sub/",
#             "prestable/toktmx/smn2sma/",
#             "prestable/toktmx/smn2sma/facta/",
#             "prestable/toktmx/smn2sma/facta/bub/",
#             "prestable/toktmx/smn2sma/facta/bub/g.txt.toktmx",
#             "prestable/toktmx/smn2smj/",
#             "prestable/toktmx/smn2smj/facta/",
#             "prestable/toktmx/smn2smj/facta/bub/",
#             "prestable/toktmx/smn2smj/facta/bub/g.txt.toktmx",
#         )

#     def test_update_metadata(self):
#         """Update metadata."""
#         smn_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smn-orig/facta/bub/g.txt.xsl")
#         )
#         self.assertEqual(smn_metadata.get_variable("genre"), "facta")
#         self.assertEqual(smn_metadata.get_variable("mainlang"), "smn")
#         smn_parallels = smn_metadata.get_parallel_texts()
#         self.assertEqual(smn_parallels["smj"], "o.txt")
#         self.assertEqual(smn_parallels["sma"], "f.txt")

#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/facta/bub/f.txt.xsl")
#         )
#         self.assertEqual(sma_metadata.get_variable("genre"), "facta")
#         sma_parallels = sma_metadata.get_parallel_texts()
#         self.assertEqual(sma_parallels["smj"], "o.txt")
#         self.assertEqual(sma_parallels["smn"], "g.txt")
#         with self.assertRaises(KeyError):
#             sma_parallels["sme"]

#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/facta/bub/o.txt.xsl")
#         )
#         self.assertEqual(smj_metadata.get_variable("genre"), "facta")
#         smj_parallels = smj_metadata.get_parallel_texts()
#         self.assertEqual(smj_parallels["smn"], "g.txt")
#         self.assertEqual(smj_parallels["sma"], "f.txt")
#         with self.assertRaises(KeyError):
#             smj_parallels["sme"]


# class TestCorpusFilesetMetadataUpdater3(unittest.TestCase):
#     """Move to new genre/subdir, with parallel

#     parallel needs normalisation, normalised name of parallel exists, but the
#     file with the normalised name is not a duplicate of the parallel file
#     """

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write("corpus-sme-orig/ficti/sub/f.txt", b"content of f")
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )

#         self.tempdir.makedir("corpus-smj-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-smj-orig/ficti/sub/ø.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/ø.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.set_variable("mainlang", "smj")
#         smj_metadata.set_variable("translated_from", "sme")
#         smj_metadata.set_parallel_text("sme", "f.txt")
#         smj_metadata.write_file()

#         self.tempdir.write(
#             "corpus-smj-orig/facta/bub/o.txt", "content of o".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/facta/bub/o.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.write_file()

#         self.tempdir.makedir("prestable/converted/smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "converted content of ø".encode("utf8"),
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#         oldpath = os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")
#         newpath = os.path.join(self.tempdir.path, "corpus-sme-orig/facta/bub/g.txt")
#         cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
#         cfm.move_files()
#         cfm.update_own_metadata()
#         cfm.update_parallel_files_metadata()

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_move_fileset(self):
#         """Move fileset."""
#         self.tempdir.check_all(
#             "",
#             "corpus-sme-orig/",
#             "corpus-sme-orig/facta/",
#             "corpus-sme-orig/facta/bub/",
#             "corpus-sme-orig/facta/bub/g.txt",
#             "corpus-sme-orig/facta/bub/g.txt.xsl",
#             "corpus-sme-orig/ficti/",
#             "corpus-sme-orig/ficti/sub/",
#             "corpus-smj-orig/",
#             "corpus-smj-orig/facta/",
#             "corpus-smj-orig/facta/bub/",
#             "corpus-smj-orig/facta/bub/o.txt",
#             "corpus-smj-orig/facta/bub/o.txt.xsl",
#             "corpus-smj-orig/facta/bub/o_1.txt",
#             "corpus-smj-orig/facta/bub/o_1.txt.xsl",
#             "corpus-smj-orig/ficti/",
#             "corpus-smj-orig/ficti/sub/",
#             "prestable/",
#             "prestable/converted/",
#             "prestable/converted/sme/",
#             "prestable/converted/sme/facta/",
#             "prestable/converted/sme/facta/bub/",
#             "prestable/converted/sme/facta/bub/g.txt.xml",
#             "prestable/converted/sme/ficti/",
#             "prestable/converted/sme/ficti/sub/",
#             "prestable/converted/smj/",
#             "prestable/converted/smj/facta/",
#             "prestable/converted/smj/facta/bub/",
#             "prestable/converted/smj/facta/bub/o_1.txt.xml",
#             "prestable/converted/smj/ficti/",
#             "prestable/converted/smj/ficti/sub/",
#             "prestable/tmx/",
#             "prestable/tmx/sme2smj/",
#             "prestable/tmx/sme2smj/facta/",
#             "prestable/tmx/sme2smj/facta/bub/",
#             "prestable/tmx/sme2smj/facta/bub/g.txt.tmx",
#             "prestable/tmx/sme2smj/ficti/",
#             "prestable/tmx/sme2smj/ficti/sub/",
#             "prestable/toktmx/",
#             "prestable/toktmx/sme2smj/",
#             "prestable/toktmx/sme2smj/facta/",
#             "prestable/toktmx/sme2smj/facta/bub/",
#             "prestable/toktmx/sme2smj/facta/bub/g.txt.toktmx",
#             "prestable/toktmx/sme2smj/ficti/",
#             "prestable/toktmx/sme2smj/ficti/sub/",
#         )

#     def test_update_metadata(self):
#         """Update metadata."""
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/facta/bub/g.txt.xsl")
#         )
#         self.assertEqual(sme_metadata.get_variable("genre"), "facta")
#         self.assertEqual(sme_metadata.get_variable("mainlang"), "sme")
#         sme_parallels = sme_metadata.get_parallel_texts()
#         self.assertEqual(sme_parallels["smj"], "o_1.txt")

#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/facta/bub/o_1.txt.xsl")
#         )
#         self.assertEqual(smj_metadata.get_variable("genre"), "facta")
#         smj_parallels = smj_metadata.get_parallel_texts()
#         self.assertEqual(smj_parallels["sme"], "g.txt")


# class TestCorpusFilesetMetadataUpdater4(unittest.TestCase):
#     """move to new genre/subdir, with parallel

#     parallel needs normalisation, normalised name of parallel exists.
#     The file with the normalised name is a duplicate of the parallel file
#     """

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write("corpus-sme-orig/ficti/sub/f.txt", b"content of f")
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             b"converted content of f",
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             b"parallelised content of f",
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#             b"parallelised content of f",
#         )

#         self.tempdir.makedir("corpus-smj-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-smj-orig/ficti/sub/ø.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/ø.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.set_variable("mainlang", "smj")
#         smj_metadata.set_variable("translated_from", "sme")
#         smj_metadata.set_parallel_text("sme", "f.txt")
#         smj_metadata.write_file()

#         self.tempdir.write(
#             "corpus-smj-orig/facta/bub/o.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/facta/bub/o.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.write_file()

#         self.tempdir.makedir("prestable/converted/smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "converted content of ø".encode("utf8"),
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_move_fileset(self):
#         """Move a set of files."""
#         oldpath = os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")
#         newpath = os.path.join(self.tempdir.path, "corpus-sme-orig/facta/bub/g.txt")
#         with self.assertRaises(UserWarning):
#             cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
#             cfm.move_files()
#             cfm.update_own_metadata()
#             cfm.update_parallel_files_metadata()

#         self.tempdir.check_all(
#             "",
#             "corpus-sme-orig/",
#             "corpus-sme-orig/ficti/",
#             "corpus-sme-orig/ficti/sub/",
#             "corpus-sme-orig/ficti/sub/f.txt",
#             "corpus-sme-orig/ficti/sub/f.txt.xsl",
#             "corpus-smj-orig/",
#             "corpus-smj-orig/facta/",
#             "corpus-smj-orig/facta/bub/",
#             "corpus-smj-orig/facta/bub/o.txt",
#             "corpus-smj-orig/facta/bub/o.txt.xsl",
#             "corpus-smj-orig/ficti/",
#             "corpus-smj-orig/ficti/sub/",
#             "corpus-smj-orig/ficti/sub/ø.txt",
#             "corpus-smj-orig/ficti/sub/ø.txt.xsl",
#             "prestable/",
#             "prestable/converted/",
#             "prestable/converted/sme/",
#             "prestable/converted/sme/ficti/",
#             "prestable/converted/sme/ficti/sub/",
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             "prestable/converted/smj/",
#             "prestable/converted/smj/ficti/",
#             "prestable/converted/smj/ficti/sub/",
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "prestable/tmx/",
#             "prestable/tmx/sme2smj/",
#             "prestable/tmx/sme2smj/ficti/",
#             "prestable/tmx/sme2smj/ficti/sub/",
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             "prestable/toktmx/",
#             "prestable/toktmx/sme2smj/",
#             "prestable/toktmx/sme2smj/ficti/",
#             "prestable/toktmx/sme2smj/ficti/sub/",
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#         )


# class TestCorpusFilesetMetadataUpdater5(unittest.TestCase):
#     """Remove file, with parallels, parallel needs normalisation."""

#     def setUp(self):
#         self.tempdir = testfixtures.TempDirectory(ignore=[".git"])

#         self.tempdir.makedir("corpus-sme-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-sme-orig/ficti/sub/f.txt", "content of f".encode("utf8")
#         )
#         sme_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sme_metadata.set_variable("mainlang", "sme")
#         sme_metadata.set_parallel_text("smj", "ø.txt")
#         sme_metadata.set_parallel_text("sma", "f.txt")
#         sme_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sme/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sme/ficti/sub/f.txt.xml",
#             "converted content of f".encode("utf8"),
#         )
#         self.tempdir.makedir("prestable/tmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2smj/ficti/sub/f.txt.tmx",
#             "parallelised content of f".encode("utf8"),
#         )
#         self.tempdir.makedir("prestable/tmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/tmx/sme2sma/ficti/sub/f.txt.tmx",
#             "parallelised content of f".encode("utf8"),
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx",
#             "parallelised content of f".encode("utf8"),
#         )
#         self.tempdir.makedir("prestable/toktmx/sme2sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/toktmx/sme2sma/ficti/sub/f.txt.toktmx",
#             "parallelised content of f".encode("utf8"),
#         )

#         self.tempdir.makedir("corpus-smj-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-smj-orig/ficti/sub/ø.txt", "content of ø".encode("utf8")
#         )
#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/ø.txt.xsl"),
#             create=True,
#         )
#         smj_metadata.set_variable("mainlang", "smj")
#         smj_metadata.set_variable("translated_from", "sme")
#         smj_metadata.set_variable("genre", "ficti")
#         smj_metadata.set_parallel_text("sme", "f.txt")
#         smj_metadata.set_parallel_text("sma", "f.txt")
#         smj_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/smj/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/smj/ficti/sub/ø.txt.xml",
#             "converted content of ø".encode("utf8"),
#         )

#         self.tempdir.makedir("corpus-sma-orig/ficti/sub")
#         self.tempdir.write(
#             "corpus-sma-orig/ficti/sub/f.txt", "content of f".encode("utf8")
#         )
#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/ficti/sub/f.txt.xsl"),
#             create=True,
#         )
#         sma_metadata.set_variable("mainlang", "sma")
#         sma_metadata.set_variable("translated_from", "sme")
#         sma_metadata.set_variable("genre", "ficti")
#         sma_metadata.set_parallel_text("sme", "f.txt")
#         sma_metadata.set_parallel_text("smj", "ø.txt")
#         sma_metadata.write_file()
#         self.tempdir.makedir("prestable/converted/sma/ficti/sub")
#         self.tempdir.write(
#             "prestable/converted/sma/ficti/sub/f.txt.xml",
#             "converted content of f".encode("utf8"),
#         )

#         r = git.Repo.init(self.tempdir.path)
#         r.index.add(["orig", "prestable"])
#         r.index.commit("Added orig and prestable")

#         oldpath = os.path.join(self.tempdir.path, "corpus-sme-orig/ficti/sub/f.txt")

#         cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, "")
#         cfm.move_files()
#         cfm.update_own_metadata()
#         cfm.update_parallel_files_metadata()

#     def tearDown(self):
#         self.tempdir.cleanup()

#     def test_move_fileset(self):
#         self.tempdir.check_all(
#             "",
#             "corpus-sma-orig/",
#             "corpus-sma-orig/ficti/",
#             "corpus-sma-orig/ficti/sub/",
#             "corpus-sma-orig/ficti/sub/f.txt",
#             "corpus-sma-orig/ficti/sub/f.txt.xsl",
#             "corpus-smj-orig/",
#             "corpus-smj-orig/ficti/",
#             "corpus-smj-orig/ficti/sub/",
#             "corpus-smj-orig/ficti/sub/o.txt",
#             "corpus-smj-orig/ficti/sub/o.txt.xsl",
#             "prestable/",
#             "prestable/converted/",
#             "prestable/converted/sma/",
#             "prestable/converted/sma/ficti/",
#             "prestable/converted/sma/ficti/sub/",
#             "prestable/converted/sma/ficti/sub/f.txt.xml",
#             "prestable/converted/smj/",
#             "prestable/converted/smj/ficti/",
#             "prestable/converted/smj/ficti/sub/",
#             "prestable/converted/smj/ficti/sub/o.txt.xml",
#         )

#     def test_update_metadata(self):
#         """Update metadata."""
#         sma_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-sma-orig/ficti/sub/f.txt.xsl")
#         )
#         self.assertEqual(sma_metadata.get_variable("genre"), "ficti")
#         sma_parallels = sma_metadata.get_parallel_texts()
#         with self.assertRaises(KeyError):
#             sma_parallels["sme"]
#         self.assertEqual(sma_parallels["smj"], "o.txt")

#         smj_metadata = xslsetter.MetadataHandler(
#             os.path.join(self.tempdir.path, "corpus-smj-orig/ficti/sub/o.txt.xsl")
#         )
#         self.assertEqual(smj_metadata.get_variable("genre"), "ficti")
#         smj_parallels = smj_metadata.get_parallel_texts()
#         with self.assertRaises(KeyError):
#             smj_parallels["sme"]
#         self.assertEqual(smj_parallels["sma"], "f.txt")

# git filter-repo --path-rename prestable/tmx:tmx && git filter-repo --path prestable/ --invert-paths && git remote add origin git@github.com:giellalt/$(basename $(pwd)) && git push --force -u origin main
