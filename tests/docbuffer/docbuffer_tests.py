# from docbuffer import DocBuffer

from docbuffer_test_context import TEST_NCC_PATH  # , TEST_SMIL_PATH


def test_open():
    with open(TEST_NCC_PATH, "rt") as source:
        data = source.read()

    assert isinstance(data, bytes)
    print("TOTO")
