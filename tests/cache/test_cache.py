"""Test the cache module."""

from cache import Cache, CacheItem
from domlib import Document


def test_sizeing():
    cache = Cache(max_size=-3)
    assert cache.get_max_size() == 0
    assert cache.get_current_size() == 0

    cache.set_max_size(3)
    assert cache.get_max_size() == 3
    assert cache.get_current_size() == 0

    # Set size to 100 elements
    cache.set_max_size(100)
    assert cache.get_max_size() == 100
    assert cache.get_current_size() == 0

    # Resizeing to negative values does not work
    cache.set_max_size(-1)
    assert cache.get_max_size() == 100

    # Resize to 0
    cache.set_max_size(0)
    assert cache.get_current_size() == 0


def test_adding_items():
    # Create a cache for 3 items
    cache = Cache(max_size=3)
    assert cache.get_max_size() == 3

    # Add bytes
    item1 = CacheItem("item 1", b"123345")
    cache.add(item1)

    cached_item = cache.get("item 1")
    assert cached_item is item1
    assert cached_item.get_type() is str

    # Add a simple string
    item2 = CacheItem("item 2", "ABCDEF")
    cache.add(item2)

    cached_item = cache.get("item 2")
    assert cached_item is item2
    assert cached_item.get_type() is str

    # Add an xml string
    item3 = CacheItem("item 3", "<a>This is<b>a test</b></a>")
    cache.add(item3)

    cached_item = cache.get("item 3")
    assert cached_item is item3
    assert cached_item.get_type() is Document

    # Add one more xml string (should remove the first item since the cache size is 3)
    item4 = CacheItem("item 4", "<a>This is<b>a test</b></a>")
    cache.add(item4)

    # Cache current size should still be 3
    assert cache.get_current_size() == 3

    # Item 4 tests
    cached_item = cache.get("item 4")
    assert cached_item is item4
    assert cached_item.get_type() is Document

    # Item 1 should not be cached anymore
    cached_item = cache.get("item 1")
    assert cached_item is None

    # Cache size should still be 3
    assert cache.get_current_size() == 3


def test_autoexpand_adding_items():
    # Create a cache for 3 items
    cache = Cache(auto_expand=True)
    assert cache.get_max_size() == 0
    assert cache.get_current_size() == 0

    # Add bytes
    for n in range(3):
        print(n)
        item = CacheItem(f"item {n}", b"123345")
        cache.add(item)

    assert cache.get_current_size() == 3

    for n in range(3):
        print(n)
        item = CacheItem(f"item {n}", b"123345")
        cache.add(item)

    # Force addition
    for n in range(3):
        print(n)
        item = CacheItem(f"item {n}", b"123345")
        cache.add(item, force=True)

    assert cache.get_current_size() == 6
