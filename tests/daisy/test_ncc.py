"""Ncc class tests"""

from daisy import Ncc
from dtbsource import FileDtbResource
from daisy_test_context import SAMPLE_DTB_PROJECT_PATH


def test_ncc_load_from_filesystem():
    source = FileDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)
