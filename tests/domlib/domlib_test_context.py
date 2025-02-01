import os
from domlib import DomFactory, Document

TEST_NCC_PATH = os.path.join(os.path.dirname(__file__), "../samples/test_data.html")
TEST_SMIL_PATH = os.path.join(os.path.dirname(__file__), "../samples/valentin_hauy/hauy_0029.smil")


def get_ncc_string() -> str | None:
    "Get a string for the tests"

    try:
        with open(TEST_NCC_PATH, "rt") as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_smil_string() -> str | None:
    "Get a string for the tests"

    try:
        with open(TEST_SMIL_PATH, "rt") as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_ncc_document() -> Document | None:
    "Get a document for the tests"
    return DomFactory.create_document_from_string(get_ncc_string())


def get_smil_document() -> Document | None:
    "Get a document for the tests"
    return DomFactory.create_document_from_string(get_smil_string())
