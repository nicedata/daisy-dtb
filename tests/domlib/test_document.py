import os

from utils import get_test_document

from domlib import Document, DomFactory, Element

document = get_test_document()


def test_get_element_by_id():
    """Find an element by its id."""
    # Test if Document
    assert type(document) == Document

    # Find elements
    test = document.get_element_by_id("dijn0198")
    assert test != None
    assert type(test) == Element
    assert test.name == "h5"

    test = document.get_element_by_id("dijn0159")
    assert test != None
    assert type(test) == Element
    assert test.name == "h2"

    # Find an unfindable element
    test = document.get_element_by_id("unexisting_id")
    assert test == None


def test_get_elements():
    """Find multiple elements with no filter."""

    elements = document.get_elements("h1")
    assert elements.size == 15

    elements = document.get_elements("H1")
    assert elements.size == 0


def test_get_elements_with_filter():
    """Find multiple elements with a filter."""

    filter = {"href": "dijn0038.smil#hvlg_0001"}

    elements = document.get_elements("*", filter)
    assert elements.size == 1
    assert elements.first().get_text() == "Recommandation du Conseil fédéral et du Parlement"
