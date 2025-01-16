from navigator_test_context import folder_book

from develop import DaisyDtbNavigator


def test_nav_level() -> None:
    nav = DaisyDtbNavigator(folder_book)

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
    nav = DaisyDtbNavigator(folder_book)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.first_entry()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.next_entry()

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.first_entry()
    assert entry.id == "rgn_ncc_0001"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next_entry()

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.first_entry()
    assert entry.id == "rgn_ncc_0002"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next_entry()

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.first_entry()
    assert entry.id == "rgn_ncc_0003"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.next_entry()


def test_level_navigation_last_to_first() -> None:
    nav = DaisyDtbNavigator(folder_book)

    # No level filtering
    assert nav.get_nav_level() == 0
    entry = nav.last_entry()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level in [1, 2, 3]
        entry = nav.prev_entry()

    # Level 1
    assert nav.increase_nav_level() == 1
    entry = nav.last_entry()
    assert entry.id == "rgn_ncc_0052"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev_entry()

    # Level 2
    assert nav.increase_nav_level() == 2
    entry = nav.last_entry()
    assert entry.id == "rgn_ncc_0057"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev_entry()

    # Level 3
    assert nav.increase_nav_level() == 3
    entry = nav.last_entry()
    assert entry.id == "rgn_ncc_0040"
    while entry is not None:
        assert entry.level == nav.get_nav_level()
        entry = nav.prev_entry()
