from domlib_test_context import get_ncc_string

from daisy_dtb import Document, DomFactory


def test_create_document_from_url():
    """Test document creation from document URLs"""

    # Valid urls
    valid_urls = [
        "http://webplayer.abage.ch/media/VOTATIONS/VF/ncc.html",
        "https://webplayer.abage.ch/media/VOTATIONS/VF/source.html",
    ]

    for url in valid_urls:
        document = DomFactory.create_document_from_url(url)
        assert type(document) is Document

    # Invalid urls
    invalid_urls = [
        "htt://webplayer.abage.ch/media/VOTATIONS/VF/ncc.html",
        "https://nodomain/media/VOTATIONS/VF/source.html",
        "https://webplayer.abage.ch/media/VOTATIONS/VF/error",
    ]
    for url in invalid_urls:
        document = DomFactory.create_document_from_url(url)
        assert document is None


def test_create_document_from_string():
    # This should be OK
    string = get_ncc_string()
    document = DomFactory.create_document_from_string(string)
    assert type(document) is Document

    # This should fail
    string = ""
    document = DomFactory.create_document_from_string(string)
    assert document is None
