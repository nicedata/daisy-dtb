import os
from domlib import DomFactory, Document

TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "../samples/test_data.html")


def get_test_string() -> str | None:
    "Get a string for the tests"

    try:
        with open(TEST_FILE_PATH, "rt") as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_test_document() -> Document | None:
    "Get a document for the tests"

    return DomFactory.create_document_from_string(get_test_string())
