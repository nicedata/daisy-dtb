from dtbsource_test_context import SAMPLE_DTB_ZIP_WITH_ROOT_FOLDER_PATH, SAMPLE_DTB_ZIP_WITH_ROOT_FOLDER_URL

from daisy_dtb import Document, ZipDtbSource


def test_zip_with_foldersource():
    # Tests with an existing filesystem archive
    source = ZipDtbSource(base_path=SAMPLE_DTB_ZIP_WITH_ROOT_FOLDER_PATH)

    data = source.get("ncc.html")
    assert isinstance(data, Document)


def test_zip_with_web_foldersource():
    # Tests with an existing filesystem archive
    source = ZipDtbSource(base_path=SAMPLE_DTB_ZIP_WITH_ROOT_FOLDER_URL)

    data = source.get("ncc.html")
    assert isinstance(data, Document)
