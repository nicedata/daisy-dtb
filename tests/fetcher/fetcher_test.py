from utilities.fetcher import Fetcher
from fetcher_test_context import SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL, SAMPLE_DTB_ZIP_PATH, SAMPLE_DTB_ZIP_URL, UNEXISTING_PATH, UNEXISTING_URL, UNEXISTING_ZIP


def test_availability():
    assert Fetcher.is_available(b"invalid argument type") is False

    assert Fetcher.is_available(SAMPLE_DTB_PROJECT_PATH) is True
    assert Fetcher.is_available(SAMPLE_DTB_PROJECT_URL) is True
    assert Fetcher.is_available(SAMPLE_DTB_ZIP_PATH) is True
    assert Fetcher.is_available(SAMPLE_DTB_ZIP_URL) is True
    assert Fetcher.is_available(UNEXISTING_PATH) is False
    assert Fetcher.is_available(UNEXISTING_URL) is False
    assert Fetcher.is_available(UNEXISTING_ZIP) is False


def test_fetch():
    data = Fetcher.fetch(SAMPLE_DTB_ZIP_PATH)
    assert len(data) == 11543058
    assert isinstance(data, bytes)

    data = Fetcher.fetch(SAMPLE_DTB_ZIP_URL)
    assert len(data) == 11543058
    assert isinstance(data, bytes)

    data = Fetcher.fetch(UNEXISTING_ZIP)
    assert len(data) == 0
    assert isinstance(data, bytes)

    data = Fetcher.fetch(SAMPLE_DTB_PROJECT_PATH)
    assert len(data) == 0
    assert isinstance(data, bytes)

    data = Fetcher.fetch(SAMPLE_DTB_PROJECT_URL)
    assert len(data) == 0
    assert isinstance(data, bytes)

    data = Fetcher.fetch(b"invalid argument type")
    assert len(data) == 0
    assert isinstance(data, bytes)
