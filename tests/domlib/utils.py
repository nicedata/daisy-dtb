import os
from domlib import DomFactory, Document

test_file_path = os.path.join(os.path.dirname(__file__), "test_data.html")


def get_test_string() -> str | None:

    try:
        with open(test_file_path, "rt") as file:
            return file.read()
    except:
        return None


def get_test_document() -> Document | None:
    # Get a document for the tests
    return DomFactory.create_document_from_string(get_test_string())
