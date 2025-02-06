from typing import Any, Callable, List, Union

from loguru import logger


class BaseNavigator:
    """
    This class implements basic metods to navigate in a list of items.

    Navigation means that the class implements a "cursor" that retains the currently selected item of the list.

    Methods:
        - first() : returns the first item.
        - next() : returns the next item or None if there is no next element in the list.
        - prev() : returns the previous item or None if there is no previous element in the list.
        - last() : returns the last item.
        - current() : returns the current item.
        - navigate_to(id) : returns the item by its id.
        - all() : return all items.
        - add_callback(func(item)) : add a callback function, triggered on navigation (when the current item changes).

    Notes:
        - on instanciation, the first item of the list is pointed.
        - the navigate_to(id) method works only if the items have an 'id' attribute.
          If the method fails, no exception is raised, but it simply returns None.
    """

    def __init__(self, items: List[Any], callback: Callable[[Any], None] = None) -> None:
        """Instanciate a `BasicNavigator` class.

        Args:
            items (List[Any]]): a list of elements.
            callback (callback: Callable[[Any], None], optional) : a function to be called on navigation events.

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
        self._items: List[Any] = items
        self._id_list: List[str] = None
        self._current_index: int = 0
        self._max_index: int = len(self._items) - 1
        self._on_navigate: Callable[[Any], None] = callback

        logger.debug(f"{type(self)} instance created with {len(self._items)} element(s) of type {items_type}.")

        # Populate the list of ids if the attribute exists
        is_id_attribute_present = "id" in dict(items[0]).keys() if hasattr(items_type, "keys") else hasattr(items[0], "id")
        if is_id_attribute_present:
            if hasattr(items_type, "keys"):
                self._id_list = [_["id"] for _ in self._items]
            else:
                self._id_list = [getattr(_, "id") for _ in self._items]

    @property
    def length(self) -> int:
        return len(self._items)

    def set_callback(self, callback: Callable[[Any], None]) -> None:
        """Sets a navigation callback function.

        It allows to attach an external navigation handler.

        Args:
            func (Callable[[Any],Any]): a callback function which can handle the current item as a parameter.
        """
        self._on_navigate = callback

    def on_first(self) -> bool:
        """Test if the current item is the first one.

        Returns:
            bool: True if the current item is the first one, False otherwise.
        """
        return self._current_index == 0

    def on_last(self) -> bool:
        """Test if the current item is the last one.

        Returns:
            bool: True if the current item is the last one, False otherwise.
        """
        return self._current_index == self._max_index

    def all(self) -> List[Any]:
        """Return all items as a list.

        Returns:
            List[Any]: the navigator items.
        """
        return self._items

    def first(self) -> Any:
        """"""
        """Go to the first item.

        Returns:
            Any: the first item in the list.
        """
        self._current_index = 0
        item = self._items[self._current_index]

        # Perform a callback if required
        if self._on_navigate is not None:
            self._on_navigate(item)

        return item

    def next(self) -> Union[Any, None]:
        """Go to the next item.

        Returns:
            Union[Any, None]: the next item in the list or None if no next item.
        """
        if self._current_index + 1 <= self._max_index:
            self._current_index += 1
            item = self._items[self._current_index]
        else:
            return None

        # Perform a callback if required
        if self._on_navigate is not None:
            self._on_navigate(item)

        return item

    def prev(self) -> Union[Any, None]:
        """Go to the previous item.

        Returns:
            Union[Any, None]: the previous item in the list or None if no previous item.
        """
        if self._current_index - 1 >= 0:
            self._current_index = self._current_index - 1
            item = self._items[self._current_index]
        else:
            return None

        # Perform a callback if required
        if self._on_navigate:
            self._on_navigate(item)

        return item

    def last(self) -> Any:
        """Go to the last item.

        Returns:
            Any: the previous item in the list.
        """
        self._current_index = self._max_index
        item = self._items[self._current_index]

        # Perform a callback if required
        if self._on_navigate:
            self._on_navigate(item)

        return item

    def current(self) -> Any:
        """Get the current item.

        Returns:
            Any: the current item.
        """
        item = self._items[self._current_index]

        return item

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
            item = self._items[self._id_list.index(item_id)]
            logger.debug(f"Item with id {item_id} of type {type(item)} found.")
            if self._on_navigate is not None:
                self._on_navigate(item)
            return item
        except ValueError:
            logger.debug(f"Item with id {item_id} not found.")
            return None
