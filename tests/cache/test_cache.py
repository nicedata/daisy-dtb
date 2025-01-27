"""Test the cache module."""

from cache import Cache, _CacheItem
from domlib import Document


def test_sizeing():
    cache = Cache(max_size=-3)
    assert cache.get_max_size() == 0

    cache.resize(3)
    assert cache.get_max_size() == 3

    # Set size to 100 elements
    cache.resize(100)
    assert cache.get_max_size() == 100

    # Set size to 100 elements
    cache.resize(0)
    assert cache.get_max_size() == 0


def test_sizeing_with_elements():
    items = [
        _CacheItem("first", b"first"),
        _CacheItem("next 1", b"next 1"),
        _CacheItem("next 2", b"next 2"),
        _CacheItem("last", b"last"),
    ]

    cache = Cache(max_size=4)
    assert cache.get_max_size() == 4

    for item in items:
        cache.add(item)

    assert cache.get("next 2") == _CacheItem("next 2", b"next 2")
    assert cache.get("last") == _CacheItem("last", b"last")

    cache.resize(3)
    assert cache.get("last") == _CacheItem("last", b"last")
    assert cache.get("first") is None

    cache.resize(0)

    for item in items:
        cache.add(item)

    assert cache.get("last") is None
    assert cache.get("first") is None


def test_adding_items():
    # Create a cache for 3 items
    cache = Cache(max_size=3)
    assert cache.get_max_size() == 3

    # Add bytes
    item1 = _CacheItem("item 1", b"123345")
    cache.add(item1)

    cached_item = cache.get("item 1")
    assert cached_item is item1
    assert cached_item.type is str

    # Add a simple string
    item2 = _CacheItem("item 2", "ABCDEF")
    cache.add(item2)

    cached_item = cache.get("item 2")
    assert cached_item is item2
    assert cached_item.type is str

    # Add an xml string
    item3 = _CacheItem("item 3", "<a>This is<b>a test</b></a>")
    cache.add(item3)

    cached_item = cache.get("item 3")
    assert cached_item is item3
    assert cached_item.type is Document

    # Add one more xml string (should remove the first item since the cache size is 3)
    item4 = _CacheItem("item 4", "<a>This is<b>a test</b></a>")
    cache.add(item4)

    # Item 4 tests
    cached_item = cache.get("item 4")
    assert cached_item is item4
    assert cached_item.type is Document

    # Item 1 should not be cached anymore
    cached_item = cache.get("item 1")
    assert cached_item is None


def test_stats():
    items = [
        _CacheItem("first", b"first"),
        _CacheItem("next 1", b"next 1"),
        _CacheItem("next 2", b"next 2"),
        _CacheItem("last", b"last"),
    ]

    cache = Cache(max_size=4, with_stats=True)
    assert cache.get_max_size() == 4
    [cache.add(_) for _ in items]

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
