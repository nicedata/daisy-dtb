"""Ncc class tests"""

from daisy_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL

from daisy import Dtb
from dtbsource import FileDtbResource, WebDtbResource


def test_ncc_load_from_filesystem():
    try:
        source = FileDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)
    except FileNotFoundError:
        return

    assert isinstance(source, FileDtbResource)

    dtb = Dtb(source)
    assert isinstance(dtb, Dtb)
    assert dtb.is_valid is True
    assert len(dtb.metadata) == 30
    assert len(dtb.entries) == 30
    assert len(dtb.smils) == 30
    assert dtb.get_title() == "Valentin Haüy - the father of the education for the blind"

    dtb.smils[0].load()
    assert dtb.smils[0].is_loaded is True


def test_ncc_load_from_web():
    try:
        source = WebDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)
    except FileNotFoundError:
        return

    assert isinstance(source, WebDtbResource)

    dtb = Dtb(source)
    assert isinstance(dtb, Dtb)
    assert dtb.is_valid is True
    assert len(dtb.metadata) == 32
    assert len(dtb.entries) == 87
    assert len(dtb.smils) == 87
    assert dtb.get_title() == "Guide pratique bénéficiaires"

    dtb.smils[0].load()
    assert dtb.smils[0].is_loaded is True
