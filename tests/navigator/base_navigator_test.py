import pytest

from base_navigator import BaseNavigator


class TestItemWithId:
    def __init__(self, id: str | int, length: int):
        self.id = id
        self.length = length


class TestItemWithoutId:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


DICT_LIST_WITH_ID = [
    {"id": 1, "value": "1"},  # 0
    {"id": 2, "value": "2"},  # 1
    {"id": 3, "value": "3"},  # 2
    {"id": 4, "value": "4"},  # 3
    {"id": 5, "value": "5"},  # 4
    {"id": 6, "value": "6"},  # 5
]

DICT_LIST_WITHOUT_ID = [
    {"data": 1, "value": "1"},  # 0
    {"data": 2, "value": "2"},  # 1
    {"data": 3, "value": "3"},  # 2
    {"data": 4, "value": "4"},  # 3
    {"data": 5, "value": "5"},  # 4
    {"data": 6, "value": "6"},  # 5
]

CLASS_LIST_WITH_ID = [
    TestItemWithId(1, 121),  # 0
    TestItemWithId(2, 122),  # 1
    TestItemWithId(3, 123),  # 2
    TestItemWithId(4, 124),  # 3
    TestItemWithId(5, 125),  # 4
    TestItemWithId(6, 126),  # 5
]

CLASS_LIST_WITHOUT_ID = [
    TestItemWithoutId("A", 12),  # 0
    TestItemWithoutId("B", 12),  # 1
    TestItemWithoutId("C", 12),  # 2
    TestItemWithoutId("D", 12),  # 3
    TestItemWithoutId("E", 12),  # 4
    TestItemWithoutId("F", 12),  # 4
]

CLASS_LIST_MIXED = [
    TestItemWithoutId("A", 12),
    TestItemWithId(1, 12),
    TestItemWithoutId("C", 12),
    TestItemWithId(2, 12),
    TestItemWithoutId("E", 12),
    TestItemWithoutId("F", 12),
]


def test_init():
    """Test BasicNavigator class intanciation"""
    # Fail : the argument is not a list
    with pytest.raises(ValueError):
        BaseNavigator("1234")

    # Fail : the argument is an empty list
    with pytest.raises(ValueError):
        BaseNavigator([])

    # Fail : mixed element types in the list
    with pytest.raises(ValueError):
        BaseNavigator(CLASS_LIST_MIXED)

    # Success : the list is OK
    nav = BaseNavigator(["A", "B", "C"])
    assert isinstance(nav, BaseNavigator)


def test_dict_with_id_list_navigation():
    """Test navigation using a dict list (with an id attribute)"""

    nav = BaseNavigator(DICT_LIST_WITH_ID)
    assert isinstance(nav, BaseNavigator)

    # Get the first element
    assert nav.first() == DICT_LIST_WITH_ID[0]

    # Get the previous element (shoud be None)
    assert nav.prev() is None

    # The current element should still be the first one
    assert nav.current() is DICT_LIST_WITH_ID[0]

    # The next element should second one
    assert nav.next() is DICT_LIST_WITH_ID[1]

    # Get the last element
    assert nav.last() == DICT_LIST_WITH_ID[5]

    # Get the next element (shoud be None)
    assert nav.next() is None

    # Get the previous element (shoud be the 5th one)
    assert nav.prev() == DICT_LIST_WITH_ID[4]

    # Navigate to the element with id=3
    item = nav.navigate_to(3)
    assert nav.navigate_to(3) == DICT_LIST_WITH_ID[2]


def test_dict_without_id_list_navigation():
    """Test navigation using a dict list (with NO id attribute)"""

    nav = BaseNavigator(DICT_LIST_WITHOUT_ID)
    assert isinstance(nav, BaseNavigator)

    # Get the first element
    assert nav.first() == DICT_LIST_WITHOUT_ID[0]

    # Get the previous element (shoud be None)
    assert nav.prev() is None

    # The current element should still be the first one
    assert nav.current() is DICT_LIST_WITHOUT_ID[0]

    # The next element should second one
    assert nav.next() is DICT_LIST_WITHOUT_ID[1]

    # Get the last element
    assert nav.last() == DICT_LIST_WITHOUT_ID[5]

    # Get the next element (shoud be None)
    assert nav.next() is None

    # Get the previous element (shoud be the 5th one)
    assert nav.prev() == DICT_LIST_WITHOUT_ID[4]

    # Navigate to the element with id=3 (no id attribute)
    assert nav.navigate_to(3) is None


def test_class_with_id_list_navigation():
    """Test navigation using a class list (with an id attribute)"""

    nav = BaseNavigator(CLASS_LIST_WITH_ID)
    assert isinstance(nav, BaseNavigator)

    # Get the first element
    assert nav.first() == CLASS_LIST_WITH_ID[0]

    # Get the previous element (shoud be None)
    assert nav.prev() is None

    # The current element should still be the first one
    assert nav.current() is CLASS_LIST_WITH_ID[0]

    # The next element should second one
    assert nav.next() is CLASS_LIST_WITH_ID[1]

    # Get the last element
    assert nav.last() == CLASS_LIST_WITH_ID[5]

    # Get the next element (shoud be None)
    assert nav.next() is None

    # Get the previous element (shoud be the 5th one)
    assert nav.prev() == CLASS_LIST_WITH_ID[4]

    # Navigate to the element with id=3
    assert nav.navigate_to(3) == CLASS_LIST_WITH_ID[2]


def test_class_without_id_list_navigation():
    """Test navigation using a class list (with NO id attribute)"""

    nav = BaseNavigator(CLASS_LIST_WITHOUT_ID)
    assert isinstance(nav, BaseNavigator)

    # Get the first element
    assert nav.first() == CLASS_LIST_WITHOUT_ID[0]

    # Get the previous element (shoud be None)
    assert nav.prev() is None

    # The current element should still be the first one
    assert nav.current() is CLASS_LIST_WITHOUT_ID[0]

    # The next element should second one
    assert nav.next() is CLASS_LIST_WITHOUT_ID[1]

    # Get the last element
    assert nav.last() == CLASS_LIST_WITHOUT_ID[5]

    # Get the next element (shoud be None)
    assert nav.next() is None

    # Get the previous element (shoud be the 5th one)
    assert nav.prev() == CLASS_LIST_WITHOUT_ID[4]

    # Navigate to the element with id=3 (no id attribute)
    assert nav.navigate_to(3) is None
