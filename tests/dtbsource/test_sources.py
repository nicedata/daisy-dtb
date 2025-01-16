import pytest
from dtbsource_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL, SAMPLE_DTB_ZIP_PATH, SAMPLE_DTB_ZIP_URL, UNEXISTING_PATH, UNEXISTING_URL, UNEXISTING_ZIP

from dtbsource import DtbResource, FolderDtbResource, ZipDtbResource
from resourcebuffer import ResourceBuffer, ResourceBufferItem


def test_source_fail():
    # Should fail (Cannot create abstract class instance)
    with pytest.raises(TypeError):
        DtbResource(resource_base="any")


def test_file_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        FolderDtbResource(resource_base=UNEXISTING_PATH)


def test_web_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        FolderDtbResource(resource_base=UNEXISTING_URL)


def test_web_source_success():
    # Should succeed
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)
    assert isinstance(source, FolderDtbResource)


def test_file_source():
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)

    # Get a string - should work
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("hauy_0002.mp3")
    assert isinstance(data, bytes)

    # Should fail
    data = source.get("dummy.html")
    assert data is None


def test_web_source():
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)

    # Get a string - should work
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("04_Mission_et_valeurs.mp3")
    assert isinstance(data, bytes)

    # Get a string - should fail
    data = source.get("dummy.html")
    assert data is None


def test_zip_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        ZipDtbResource(resource_base=UNEXISTING_ZIP)

    with pytest.raises(FileNotFoundError):
        ZipDtbResource(resource_base=UNEXISTING_URL)


def test_zip_source():
    # Tests with an existing filesystem archive
    source = ZipDtbResource(resource_base=SAMPLE_DTB_ZIP_PATH)

    data = source.get("ncc.html")
    assert isinstance(data, str)

    data = source.get("13_Verrine_de_tiramisu_sal__au.mp3")
    assert isinstance(data, bytes)

    # This fails !
    assert source.get("unexisting.file") is None

    # Tests with an existing web archive
    source = ZipDtbResource(resource_base=SAMPLE_DTB_ZIP_URL)

    data = source.get("stnz0037.smil")
    assert isinstance(data, str)

    data = source.get("13_Verrine_de_tiramisu_sal__au.mp3")
    assert isinstance(data, bytes)

    assert source.get("unexisting.file") is None


def test_source_with_buffer():
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL, buffer_size=22)
    assert source.get_buffer_size() == 22

    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH, buffer_size=10)
    assert source.get_buffer_size() == 10


def test_source_with_buffer_fail():
    with pytest.raises(ValueError):
        FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH, buffer_size=-1)

    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH, buffer_size=5)
    assert source.get_buffer_size() == 5

    # Try buffer resize with negatve value
    source.resize_buffer(-1)
    assert source.get_buffer_size() == 5

    # Try buffer resize (no change)
    source.resize_buffer(5)
    assert source.get_buffer_size() == 5

    # Try buffer resize
    source.resize_buffer(15)
    assert source.get_buffer_size() == 15


def test_source_get_with_buffering():
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH, buffer_size=5)
    data = source.get("hauy_0001.smil")
    data = source.get("hauy_0002.smil")
    data = source.get("hauy_0001.smil")
    data = source.get("hauy_0002.smil")
    assert isinstance(data, str) is True

    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL, buffer_size=1)
    data = source.get("ncc.html")
    assert isinstance(data, str) is True
    data = source.get("ncc.html")
    assert isinstance(data, str) is True
    data = source.get("04_Mission_et_valeurs.mp3")
    assert isinstance(data, bytes) is True
    data = source.get("ncc.html")
    assert isinstance(data, str) is True


def test_buffering():
    buffer = ResourceBuffer(5)

    items = [
        ResourceBufferItem("item1", b"123"),
        ResourceBufferItem("item2", b"444"),
        ResourceBufferItem("item1", b"456"),
        ResourceBufferItem("item3", "string 4"),
        ResourceBufferItem("item4", "string 5"),
        ResourceBufferItem("item5", "string 6"),
        ResourceBufferItem("item6", "string 7"),
        ResourceBufferItem("item7", b"string 8"),
    ]

    assert buffer.get_size() == 5
    for item in items:
        buffer.add(item)

    buffer.set_size(10)
    assert buffer.get_size() == 10
    for item in items:
        buffer.add(item)

    item = buffer.get("item5")
    assert item.name == "item5"
