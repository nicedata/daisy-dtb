import os

from utils import get_test_string

from domlib import Document, DomFactory, Element


def test_get_element_by_id():
    """Find an element by its id."""
    string = get_test_string()
    document = DomFactory.create_document_from_string(string)

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
