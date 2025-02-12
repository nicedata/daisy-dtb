"""Test the cache module."""

from daisy_dtb import Cache


def test_sizeing():
    cache = Cache(max_size=-3)
    assert cache.maxlen == 0

    cache.resize(3)
    assert cache.maxlen == 3

    # Set size to 100 elements
    cache.resize(100)
    assert cache.maxlen == 100

    # Set size to 100 elements
    cache.resize(0)
    assert cache.maxlen == 0


def test_sizeing_with_elements():
    items = [
        dict(key="first", data=b"first"),
        dict(key="next 1", data=b"next 1"),
        dict(key="next 2", data=b"next 2"),
        dict(key="last", data=b"last"),
    ]

    cache = Cache(max_size=4)
    assert cache.maxlen == 4

    for item in items:
        cache.add(item["key"], item["data"])

    assert cache.get("next 2") == b"next 2"
    assert cache.get("last") == b"last"

    cache.resize(3)
    assert cache.get("last") == b"last"
    assert cache.get("first") is None

    cache.resize(0)

    for item in items:
        cache.add(item["key"], item["data"])

    assert cache.get("last") is None
    assert cache.get("first") is None


def test_adding_items():
    # Create a cache for 3 items
    cache = Cache(max_size=3)
    assert cache.maxlen == 3

    # Add bytes
    item1 = dict(key="item 1", data=b"12345")
    cache.add(item1["key"], item1["data"])

    cached_item = cache.get("item 1")
    assert isinstance(cached_item, bytes) is True

    # Add a simple string
    item2 = dict(key="item 2", data=b"ABCDEF")
    cache.add(item2["key"], item2["data"])

    cached_item = cache.get("item 2")
    assert cached_item == item2["data"]

    # Add an xml string
    xml_str = "<a>This is<b>a test</b></a>"
    cache.add("item 3", xml_str)

    cached_item = cache.get("item 3")
    assert cached_item == xml_str

    # Add one more xml string (should remove the first item since the cache size is 3)
    item4 = dict(key="item 4", data="<a>This is<b>a test</b></a>")
    cache.add(item4["key"], item4["data"])

    # Item 4 tests
    cached_item = cache.get("item 4")
    assert cached_item == item4["data"]

    # Item 1 should not be cached anymore
    cached_item = cache.get("item 1")
    assert cached_item is None


def test_stats():
    items = [
        dict(key="first", data=b"first"),
        dict(key="next 1", data=b"next 1"),
        dict(key="next 2", data=b"next 2"),
        dict(key="last", data=b"last"),
    ]

    cache = Cache(max_size=4, with_stats=True)
    assert cache.maxlen == 4
    [cache.add(_["key"], _["data"]) for _ in items]

    for i in range(13):
        cache.get("first")

    for i in range(8):
        cache.get("next 1")

    for i in range(2):
        cache.get("next 2")

    for i in range(20):
        cache.get("dummy")

    for i in range(12):
        cache.get("last")

    print(cache.get_stats())
