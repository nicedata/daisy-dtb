from navigator_test_context import folder_book

from develop import NccNavigator


def test_nav_level() -> None:
    nav = NccNavigator(folder_book)

    # This book has a depth of 3
    assert nav.max_nav_level == 3

    # Initial nav level must be 0
    assert nav.get_nav_level() == 0

    assert nav.increase_nav_level() == 1
    assert nav.increase_nav_level() == 2
    assert nav.increase_nav_level() == nav.max_nav_level
    assert nav.increase_nav_level() == nav.max_nav_level

    # Current level is 3 (max_nav_level)
    assert nav.decrease_nav_level() == 2
    assert nav.decrease_nav_level() == 1
    assert nav.decrease_nav_level() == 0
    assert nav.decrease_nav_level() == 0

    assert nav.increase_nav_level() == 1
    assert nav.reset_nav_level() == 0


def test_level_navigation_first_to_last() -> None:
    nav = NccNavigator(folder_book)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.first()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.next()

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.first()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.first()
    assert entry.id == "rgn_ncc_0002"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.first()
    assert entry.id == "rgn_ncc_0003"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next()


def test_level_navigation_last_to_first() -> None:
    nav = NccNavigator(folder_book)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.last()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.prev()

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.last()
    assert entry.id == "rgn_ncc_0052"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.last()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.last()
    assert entry.id == "rgn_ncc_0040"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev()
