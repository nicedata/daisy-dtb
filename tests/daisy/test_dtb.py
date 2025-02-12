"""Ncc class tests"""

import pytest
from daisy_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL

from daisy_dtb.book import DaisyBook, DaisyBookException
from daisy_dtb.sources import FolderDtbSource


def test_bool_load_failure():
    try:
        source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH)
    except FileNotFoundError:
        return

    # Maniputate the source base path to generate an error :-)
    source._base_path = "X"
    with pytest.raises(DaisyBookException):
        DaisyBook(source)


def test_ncc_load_from_filesystem():
    try:
        source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH)
    except FileNotFoundError:
        return

    assert isinstance(source, FolderDtbSource)

    dtb = DaisyBook(source)
    assert isinstance(dtb, DaisyBook)
    assert len(dtb._metadata) == 30
    assert len(dtb._toc_entries) == 30
    assert len(dtb._smils) == 30
    assert dtb.title == "Valentin Haüy - the father of the education for the blind"

    dtb._smils[0]._parse()
    assert dtb._smils[0]._is_parsed is True


def test_ncc_load_from_web():
    try:
        source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_URL)
    except FileNotFoundError:
        return

    assert isinstance(source, FolderDtbSource)

    dtb = DaisyBook(source)
    assert isinstance(dtb, DaisyBook)
    assert len(dtb._metadata) == 32
    assert len(dtb._toc_entries) == 87
    assert len(dtb._smils) == 87
    assert dtb.title == "Guide pratique bénéficiaires"

    dtb._smils[0]._parse()
    assert dtb._smils[0]._is_parsed is True
