import pytest

from dtbsource import DtbResource, FileDtbResource, WebDtbResource

from dtbsource_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL, UNEXISTING_URL, UNEXISTING_PATH


def test_source_fail():
    # Should fail (Cannot create abstract class instance)
    with pytest.raises(TypeError):
        DtbResource(resource_base="any")


def test_file_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        FileDtbResource(resource_base=UNEXISTING_PATH)


def test_web_source_fail():
    # Should fail (FileNotFound exception)
    with pytest.raises(FileNotFoundError):
        WebDtbResource(resource_base=UNEXISTING_URL)


def test_web_source_success():
    # Should succeed
    source = WebDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)
    assert isinstance(source, WebDtbResource)


def test_file_source():
    source = FileDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)

    # Get a string - should work
    data = source.get("ncc.html", convert_to_str=True)
    assert isinstance(data, str)

    # Get a string - should work too (convert_to_str defaults to True)
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("hauy_0002.mp3", convert_to_str=False)
    assert isinstance(data, bytes)

    # Should fail
    data = source.get("dummy.html")
    assert data is None


def test_web_source():
    source = WebDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)

    # Get a string - should work (convert_to_str defaults to True)
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("04_Mission_et_valeurs.mp3", convert_to_str=False)
    assert isinstance(data, bytes)

    # Get a string - should fail
    data = source.get("dummy.html")
    assert data is None
