"""Ncc class tests"""

from daisy_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL

from daisy import DaisyDtb
from dtbsource import FolderDtbResource


def test_ncc_load_from_filesystem():
    try:
        source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)
    except FileNotFoundError:
        return

    assert isinstance(source, FolderDtbResource)

    dtb = DaisyDtb(source)
    assert isinstance(dtb, DaisyDtb)
    assert dtb._is_valid is True
    assert len(dtb._metadata) == 30
    assert len(dtb._entries) == 30
    assert len(dtb._smils) == 30
    assert dtb.get_title() == "Valentin Haüy - the father of the education for the blind"

    dtb._smils[0].load()
    assert dtb._smils[0]._is_loaded is True


def test_ncc_load_from_web():
    try:
        source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)
    except FileNotFoundError:
        return

    assert isinstance(source, FolderDtbResource)

    dtb = DaisyDtb(source)
    assert isinstance(dtb, DaisyDtb)
    assert dtb._is_valid is True
    assert len(dtb._metadata) == 32
    assert len(dtb._entries) == 87
    assert len(dtb._smils) == 87
    assert dtb.get_title() == "Guide pratique bénéficiaires"

    dtb._smils[0].load()
    assert dtb._smils[0]._is_loaded is True
