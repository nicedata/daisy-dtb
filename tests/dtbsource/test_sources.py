import pytest
import os
from dtbsource import FileDtbResource, WebDtbResource, DtbResource

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


def test_source():
    # Should fail (Cannot create abstract class instance)
    with pytest.raises(TypeError):
        DtbResource(resource_base="any")


def test_file_source():
    source = FileDtbResource(resource_base=SAMPLE_DTB_PROJECT_PATH)

    # Get a string - should work
    data = source.get("ncc.html", convert_to_str=True)
    assert isinstance(data, str)

    # Get a string - should work too (convert_to_str defaults to True)
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("hauy_0002.mp3", convert_to_str=False)
    assert isinstance(data, bytes)

    # Should fail
    data = source.get("dummy.html")
    assert data is None


def test_web_source():
    source = WebDtbResource(resource_base=SAMPLE_DTB_PROJECT_URL)

    # Get a string - should work
    data = source.get("ncc.html")
    assert isinstance(data, str)

    # Get a byte array
    data = source.get("04_Mission_et_valeurs.mp3", convert_to_str=False)
    assert isinstance(data, bytes)

    # Get a string - should fail
    data = source.get("dummy.html")
    assert data is None
