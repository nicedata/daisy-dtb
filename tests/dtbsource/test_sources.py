import pytest
from dtbsource_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL, SAMPLE_DTB_ZIP_PATH, SAMPLE_DTB_ZIP_URL, UNEXISTING_PATH, UNEXISTING_URL, UNEXISTING_ZIP

from dtbsource import DtbResource, FolderDtbResource, ZipDtbResource


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
    source = FolderDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL, buffer_size=10)
    print("XXX", source.buffer)
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
