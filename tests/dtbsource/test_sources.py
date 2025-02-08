from dataclasses import dataclass
from typing import Any

import pytest
from cache import Cache
from dtbsource_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL, SAMPLE_DTB_ZIP_PATH, SAMPLE_DTB_ZIP_URL, UNEXISTING_PATH, UNEXISTING_URL, UNEXISTING_ZIP
from sources import DtbSource, FolderDtbSource, ZipDtbSource
from utilities import Document


@dataclass
class TestItem:
    key: str
    data: Any


def test_source_fail():
    # Should fail (Cannot create abstract class instance)
    with pytest.raises(TypeError):
        DtbSource(base_path="any")


def test_file_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        FolderDtbSource(base_path=UNEXISTING_PATH)


def test_web_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        FolderDtbSource(base_path=UNEXISTING_URL)


def test_web_source_success():
    # Should succeed
    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_URL)
    assert isinstance(source, FolderDtbSource)


def test_file_source():
    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH)

    # Get a string - should work
    data = source.get("ncc.html")
    assert isinstance(data, Document)

    # Get a byte array
    data = source.get("hauy_0002.mp3")
    assert isinstance(data, bytes)

    # Should fail
    data = source.get("dummy.html")
    assert data is None


def test_web_source():
    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_URL)

    # Get a string - should work
    data = source.get("ncc.html")
    assert isinstance(data, Document)

    # Get a byte array
    data = source.get("04_Mission_et_valeurs.mp3")
    assert isinstance(data, bytes)

    # Get a string - should fail
    data = source.get("dummy.html")
    assert data is None


def test_zip_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        ZipDtbSource(base_path=UNEXISTING_ZIP)

    with pytest.raises(FileNotFoundError):
        ZipDtbSource(base_path=UNEXISTING_URL)


def test_zip_source():
    # Tests with an existing filesystem archive
    source = ZipDtbSource(base_path=SAMPLE_DTB_ZIP_PATH)

    data = source.get("ncc.html")
    assert isinstance(data, Document)

    data = source.get("ncc.html")
    assert isinstance(data, Document)

    data = source.get("13_Verrine_de_tiramisu_sal__au.mp3")
    assert isinstance(data, bytes)

    # This fails !
    assert source.get("unexisting.file") is None

    # Tests with an existing web archive
    source = ZipDtbSource(base_path=SAMPLE_DTB_ZIP_URL)

    data = source.get("stnz0037.smil")
    assert isinstance(data, Document)

    data = source.get("13_Verrine_de_tiramisu_sal__au.mp3")
    assert isinstance(data, bytes)

    assert source.get("unexisting.file") is None


def test_source_with_buffer():
    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_URL, initial_cache_size=22)
    assert source.cache_size == 22

    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH, initial_cache_size=10)
    assert source.cache_size == 10


def test_source_with_buffer_fail():
    with pytest.raises(ValueError):
        FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH, initial_cache_size=-1)

    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH, initial_cache_size=5)
    assert source.cache_size == 5

    # Try buffer resize with negatve value
    source.cache_size = -1
    assert source.cache_size == 5

    # Try buffer resize (no change)
    source.cache_size = 5
    assert source.cache_size == 5

    # Try buffer resize
    source.cache_size = 15
    assert source.cache_size == 15


def test_source_get_with_buffering():
    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_PATH, initial_cache_size=5)
    data = source.get("hauy_0001.smil")
    data = source.get("hauy_0002.smil")
    data = source.get("hauy_0001.smil")
    data = source.get("hauy_0002.smil")
    assert isinstance(data, Document) is True

    source = FolderDtbSource(base_path=SAMPLE_DTB_PROJECT_URL, initial_cache_size=1)
    data = source.get("ncc.html")
    assert isinstance(data, Document) is True
    data = source.get("04_Mission_et_valeurs.mp3")
    assert isinstance(data, bytes) is True


def test_buffering():
    cache = Cache(max_size=5)

    items = [
        TestItem("item1", b"123"),
        TestItem("item2", b"444"),
        TestItem("item1", b"456"),
        TestItem("item3", "string 4"),
        TestItem("item4", "string 5"),
        TestItem("item5", "string 6"),
        TestItem("item6", "string 7"),
        TestItem("item7", b"string 8"),
    ]

    assert cache.maxlen == 5
    [cache.add(_.key, _.data) for _ in items]

    cache.resize(10)
    assert cache.maxlen == 10
    [cache.add(_.key, _.data) for _ in items]

    data = cache.get("item5")
    assert data == "string 6"
