import os


def get_test_string() -> str | None:
    path = os.path.join(os.path.dirname(__file__), "test_data.html")
    try:
        with open(path, "rt") as file:
            return file.read()
    except:
        return None
