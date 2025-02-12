from navigator_test_context import folder_book

from daisy_dtb import TocNavigator


def test_nav_level() -> None:
    nav = TocNavigator(folder_book._toc_entries, folder_book.navigation_depth)

    # This book has a depth of 3
    assert nav._max_nav_level == 3

    # Initial nav level must be 0
    assert nav.get_nav_level() == 0

    assert nav.increase_nav_level() == 1
    assert nav.increase_nav_level() == 2
    assert nav.increase_nav_level() == nav._max_nav_level
    assert nav.increase_nav_level() == nav._max_nav_level

    # Current level is 3 (max_nav_level)
    assert nav.decrease_nav_level() == 2
    assert nav.decrease_nav_level() == 1
    assert nav.decrease_nav_level() == 0
    assert nav.decrease_nav_level() == 0

    assert nav.increase_nav_level() == 1
    assert nav.reset_nav_level() == 0


def test_level_navigation_first_to_last() -> None:
    nav = TocNavigator(folder_book._toc_entries, folder_book.navigation_depth)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.first()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.next()

    assert nav.on_last() is True

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.first()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()

    assert nav.on_last() is True

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.first()
    assert entry.id == "rgn_ncc_0002"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()

    assert nav.on_last() is True

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.first()
    assert entry.id == "rgn_ncc_0003"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()

    assert nav.on_last() is True


def test_level_navigation_last_to_first() -> None:
    nav = TocNavigator(folder_book._toc_entries, folder_book.navigation_depth)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.last()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.prev()

    assert nav.on_first() is True

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.last()
    assert entry.id == "rgn_ncc_0052"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()

    assert nav.on_first() is True

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.last()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()

    assert nav.on_first() is True

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.last()
    assert entry.id == "rgn_ncc_0040"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()

    assert nav.on_first() is True
