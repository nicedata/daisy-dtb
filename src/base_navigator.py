"""Definition of `BaseNavigator` which allows to navigate in a list of elements."""

from typing import Any, List, Union

from loguru import logger


class BaseNavigator:
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

    def __init__(self, items: List[Any]) -> None:
        """Instanciate a `BasicNavigator` class.

        Args:
            items (List[Any]]): a list of elements.

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
        self._id_list: List = None
        self._current_index = 0
        self._max_index = len(self._items) - 1
        logger.debug(f"{type(self)} instance created with {len(self._items)} element(s) of type {items_type}.")

        # Populate the list of ids if the attribute exists
        is_id_attribute_present = "id" in dict(items[0]).keys() if hasattr(items_type, "keys") else hasattr(items[0], "id")
        if is_id_attribute_present:
            if hasattr(items_type, "keys"):
                self._id_list = [_["id"] for _ in self._items]
            else:
                self._id_list = [getattr(_, "id") for _ in self._items]

    def first(self) -> Any:
        """"""
        """Go to the first item.

        Returns:
            Any: the first item in the list.
        """
        self._current_index = 0
        return self._items[self._current_index]

    def next(self) -> Union[Any, None]:
        """Go to the next item.

        Returns:
            Union[Any, None]: the next item in the list or None if no next item.
        """
        if self._current_index + 1 < self._max_index:
            self._current_index = self._current_index + 1
            return self._items[self._current_index]
        return None

    def prev(self) -> Union[Any, None]:
        """Go to the previous item.

        Returns:
            Union[Any, None]: the previous item in the list or None if no previous item.
        """
        if self._current_index - 1 >= 0:
            self._current_index = self._current_index - 1
            return self._items[self._current_index]
        return None

    def last(self) -> Any:
        """Go to the last item.

        Returns:
            Any: the previous item in the list.
        """
        self._current_index = self._max_index
        return self._items[self._current_index]

    def current(self) -> Any:
        """Get the current item.

        Returns:
            Any: the current item.
        """
        return self._items[self._current_index]

    def navigate_to(self, item_id: str | int) -> Union[Any, None]:
        """Navigate to a specific item based on its id.

        Note :
            - If the item has no 'id' attribute, the method does nothing and returns None.

        Args:
            item_id (str): the searched item id

        Returns:
            Union[Any, None]: the targeted item item or None.
        """
        # Can we search by id ?
        if self._id_list is None:
            logger.debug("There is no id attribute present in the list items")
            return None

        try:
            result = self._items[self._id_list.index(item_id)]
            logger.debug(f"Item with id {item_id} of type {type(result)} found.")
            return result
        except ValueError:
            logger.debug(f"Item with id {item_id} not found.")
            return None
