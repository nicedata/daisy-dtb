"""Definition of various classes used to implement book navigation"""

from typing import List, Union

from loguru import logger

from daisy import Audio, NccEntry, Parallel


class BasicNavigator:
    """
    This class implements basic metods to navigate in a list of items.

    Navigation means that the class implements a "cursor" that retains the currently selected item of the list.

    Methods:
        - first() : returns the first item
        - next() : returns the next item or None if there is no next element in the list
        - prev() : returns the previous item or None if there is no previous element in the list
        - last() : returns the last item
        - current() : returns the current item
        - navigate_to(id) : returns the item by its id

    Note(s):
        - the navigate_to(id) method works only if the items have an 'id' attribute.
          If the method fails, no exception is raised, but it simply returns None.
    """

    def __init__(self, items: List[Union[NccEntry, Parallel, Audio]]) -> None:
        """Instanciate a `BasicNavigator` class.

        Args:
            items (List[Union[NccEntry, Parallel, Audio]]): a list of elements related to the digital talking book.

        Raises:
            ValueError: if the supplied list is not iterable
            ValueError: if the list is empty
            ValueError: if all list items ar not of the same type
        """

        # Check if we have a list
        if not isinstance(items, List):
            error_message = "The supplied argument must be a List."
            logger.error(error_message)
            raise ValueError(error_message)

        # Zero length lists are meaningless !
        if len(items) == 0:
            error_message = "An empty list has been supplied."
            logger.error(error_message)
            raise ValueError(error_message)

        # Make sure that all list items are of same kind
        # The relevant type is taken frm the first element in the list
        items_type = type(items[0])
        for item in items:
            if not isinstance(item, items_type):
                error_message = f"All list items must be of same type (in this case {items_type})."
                logger.error(error_message)
                raise ValueError(error_message)

        # Internal attriutes
        self._items = items
        self._current_index = 0
        self._max_index = len(self._items) - 1

    def first(self) -> Union[NccEntry, Parallel, Audio]:
        """Go to the first item.

        Returns:
            Union[NccEntry, Parallel, Audio]: the first item in the list.
        """
        self._current_index = 0
        return self._items[self._current_index]

    def next(self) -> Union[NccEntry, Parallel, Audio, None]:
        """Go to the next item.

        Returns:
            Union[NccEntry, Parallel, Audio, None]: the next item in the list.
        """
        if self._current_index + 1 < self._max_index:
            self._current_index = self._current_index + 1
            return self._items[self._current_index]
        return None

    def prev(self) -> Union[NccEntry, Parallel, Audio, None]:
        """Go to the previous item.

        Returns:
            Union[NccEntry, Parallel, Audio, None]: the previous item in the list.
        """
        if self._current_index - 1 >= 0:
            self._current_index = self._current_index - 1
            return self._items[self._current_index]
        return None

    def last(self) -> NccEntry | Parallel | Audio:
        """Go to the last item.

        Returns:
            Union[NccEntry, Parallel, Audio]: the previous item in the list.
        """
        self._current_index = self._max_index
        return self._items[self._current_index]

    def current(self) -> Union[NccEntry, Parallel, Audio]:
        """Get the current item.

        Returns:
            Union[NccEntry, Parallel, Audio]: the current item.
        """
        return self._items[self._current_index]

    def navigate_to(self, item_id: str | int) -> Union[NccEntry, Parallel, Audio, None]:
        """Navigate to a specific item based on its id.

        Note :
            - If the item has no 'id' attribute, the method does nothing.

        Args:
            item_id (str): the searched item id

        Returns:
            Union[NccEntry, Parallel, Audio, None]: te returned item.
        """
        # Do we have classes or dicts ?
        is_class_list = True
        try:
            vars(self._items[0])  # This fails on a dict !
        except TypeError:
            is_class_list = False

        try:
            index = [(_.id if is_class_list else _["id"]) for _ in self._items].index(item_id)
            logger.debug(f"Item with id {item_id} found.")
            return self._items[index]
        except ValueError:
            logger.debug(f"Item with id {item_id} not found.")
            return None
        except (AttributeError, KeyError):
            logger.debug("One of the items in the list has no id attribute.")
            return None
