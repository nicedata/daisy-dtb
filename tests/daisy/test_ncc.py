"""Ncc class tests"""

from daisy_test_context import SAMPLE_DTB_PROJECT_PATH

from daisy import Ncc
from dtbsource import FileDtbResource


def test_ncc_load_from_filesystem():
    try:
        source = FileDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)
    except FileNotFoundError:
        return

    assert isinstance(source, FileDtbResource)

    ncc = Ncc(source)
    assert isinstance(ncc, Ncc)
    assert len(ncc.metadata) == 30
    assert len(ncc.entries) == 30
