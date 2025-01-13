import pytest
from domlib_test_context import get_ncc_document, get_smil_document

from domlib import Document, Element

ncc_document = get_ncc_document()
smil_document = get_smil_document()


def test_get_element_by_id():
    """Find an element by its id."""
    # Test if Document
    assert type(ncc_document) is Document

    # Find elements by id
    ID = "dijn0198"
    test = ncc_document.get_element_by_id(ID)
    assert test is not None
    assert type(test) is Element
    assert test.get_name() == "h5"
    assert test.get_attr("id") == ID
    assert test.get_value() is None
    assert test.get_text() == ""

    ID = "dijn0159"
    test = ncc_document.get_element_by_id(ID)
    assert test is not None
    assert type(test) is Element
    assert test.get_name() == "h2"
    assert test.get_attr("id") == ID
    assert test.get_value() is None
    assert test.get_text() == ""

    # Find an unfindable element
    test = ncc_document.get_element_by_id("unexisting_id")
    assert test is None


def test_get_elements():
    """Find multiple elements with no filter."""

    elements = ncc_document.get_elements_by_tag_name("h1")
    assert elements.get_size() == 15

    elements = ncc_document.get_elements_by_tag_name("H1")
    assert elements.get_size() == 0


def test_get_elements_with_filter():
    """Find multiple elements with a filter."""

    FILTER = {"href": "dijn0038.smil#hvlg_0001"}
    AWAITED_TEXT = "Recommandation du Conseil fédéral et du Parlement"

    elements = ncc_document.get_elements_by_tag_name("*", FILTER)
    assert elements.get_size() == 1
    assert elements.first().get_name() == "a"
    assert elements.first().get_text() == AWAITED_TEXT
    assert elements.first().get_value() == AWAITED_TEXT


def test_get_children():
    # Raise a TypeError if tag_name is not set
    with pytest.raises(TypeError):
        ncc_document.get_elements_by_tag_name()

    # Test get_children in an ncc document
    for element in ncc_document.get_elements_by_tag_name("h1").all():
        assert element.get_children("m").get_size() == 0
        assert element.get_children("a").get_size() == 1

    # Test get_children in an smil document
    elements = smil_document.get_elements_by_tag_name("seq", having_parent_tag_name="body").all()
    assert len(elements) == 1
