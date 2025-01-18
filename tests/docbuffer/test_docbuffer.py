import pytest
from docbuffer_test_context import TEST_NCC_PATH  # , TEST_SMIL_PATH

from docbuffer import DocBuffer, DocBufferItem
from domlib import Document

with open(TEST_NCC_PATH, "rt") as source:
    data = source.read()

buffer = DocBuffer()


def test_data():
    assert isinstance(data, str)


def test_success():
    assert isinstance(buffer.add("test", data), Document)
    assert len(buffer._items) == 1
    assert isinstance(buffer._items[0], DocBufferItem)
    assert isinstance(buffer.get("test"), Document)


def test_fail():
    with pytest.raises(TypeError):
        buffer.add("testa", b"XXXX")
    assert buffer.add("testa", "XXXX") is None
