from utils import get_test_document

from domlib import Document, Element

document = get_test_document()


def test_get_element_by_id():
    """Find an element by its id."""
    # Test if Document
    assert type(document) is Document

    # Find elements by id
    ID = "dijn0198"
    test = document.get_element_by_id(ID)
    assert test is not None
    assert type(test) is Element
    assert test.get_name() == "h5"
    assert test.get_attr("id") == ID
    assert test.get_value() is None
    assert test.get_text() == ""

    ID = "dijn0159"
    test = document.get_element_by_id(ID)
    assert test is not None
    assert type(test) is Element
    assert test.get_name() == "h2"
    assert test.get_attr("id") == ID
    assert test.get_value() is None
    assert test.get_text() == ""

    # Find an unfindable element
    test = document.get_element_by_id("unexisting_id")
    assert test is None


def test_get_elements():
    """Find multiple elements with no filter."""

    elements = document.get_elements("h1")
    assert elements.get_size() == 15

    elements = document.get_elements("H1")
    assert elements.get_size() == 0


def test_get_elements_with_filter():
    """Find multiple elements with a filter."""

    FILTER = {"href": "dijn0038.smil#hvlg_0001"}
    AWAITED_TEXT = "Recommandation du Conseil fédéral et du Parlement"

    elements = document.get_elements("*", FILTER)
    assert elements.get_size() == 1
    assert elements.first().get_name() == "a"
    assert elements.first().get_text() == AWAITED_TEXT
    assert elements.first().get_value() == AWAITED_TEXT
