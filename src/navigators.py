from dataclasses import dataclass, field
from typing import Any, List, Union, override

from loguru import logger

from daisy import DaisyDtb, NccEntry


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


@dataclass
class TocNavigator(BaseNavigator):
    """
    This class provides method to navigate in table of contents of a digital talking book.
    The TOC is provided by the ncc.html file, common in Daisy 2.02 projects.

    Notes :
        - It overrides the methods of its `Navigator` base class.
        - It also provides methods to generate a TOC of the book
    """

    dtb: DaisyDtb

    # Internal attributes
    _max_nav_level: int = field(init=False, default=0)
    _current_nav_level: int = field(init=False, default=0)

    def __post_init__(self):
        """Postinitialitation of the dataclass.

        Action(s):
            - Initialize the base class
            - Set the max. navigation level
        """
        super().__init__(self.dtb._entries)
        self._max_nav_level = self.dtb.get_depth()
        logger.debug(f"Initialization of class {type(self)} done. Max. naigation level is {self._max_nav_level}.")

    @property
    def filter_is_active(self) -> bool:
        return self._current_nav_level != 0

    def set_nav_level(self, level: int) -> int:
        """Set the navigation level.

        Args:
            level (int): the requested navigation level

        Returns:
            int: the actual navigation level
        """
        # Check
        if level < 0 or level > self._max_nav_level:
            return self._current_nav_level

        self._current_nav_level = level
        return self._current_nav_level

    def get_nav_level(self) -> int:
        """Get the current navigation level.

        Returns:
            int: the current navigation level.
        """
        return self._current_nav_level

    def increase_nav_level(self) -> int:
        """Increase the navigation level.

        Returns:
            int: the updated navigation level
        """
        return self.set_nav_level(self._current_nav_level + 1)

    def decrease_nav_level(self) -> int:
        """Decrease the navigation level.

        Returns:
            int: the updated navigation level
        """
        return self.set_nav_level(self._current_nav_level - 1)

    def reset_nav_level(self) -> int:
        """Reset (remove) the navigation level.

        Returns:
            int: the updated navigation level
        """
        return self.set_nav_level(0)

    @override
    def first(self) -> NccEntry:
        """Get the first NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the first entry
        """
        item: NccEntry = super().first()

        if self.filter_is_active:
            # Enumerate upwards
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().next()

        return item

    @override
    def last(self) -> NccEntry:
        """Get the last NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the last entry
        """
        item: NccEntry = super().last()
        if self.filter_is_active:
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().prev()

        return item

    @override
    def next(self) -> NccEntry | None:
        """Get the next NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the next entry
        """
        item: NccEntry = super().next()
        if self.filter_is_active:
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().next()

        return item

    @override
    def prev(self) -> NccEntry | None:
        """Get the previous NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the previous entry
        """
        item: NccEntry = super().prev()
        if self.filter_is_active:
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().prev()

        return item

    def generate_toc(self, format: str) -> str:
        """Generate a TOC of the current book.

        Supported formats:
            - `md-list`    : a Markdown list (*)
            - `md-headers` : Markdown headers (#)
            - `html-headers` : HTML headers (<h1/> to <h6/>)

        Args:
            format (str): the requested format

        Raises:
            ValueError: raised when a format is not handled.

        Returns:
            str: the formatted TOC
        """
        result = ""
        if isinstance(format, str) is False:
            return result

        match format.lower():
            case "md-list":
                for entry in self.dtb._entries:
                    result += f'{"   " * (entry.level-1)}* {entry.text}\n'
            case "md-headers":
                for entry in self.dtb._entries:
                    result += f'{"#" * (entry.level):6} {entry.text}\n'
            case "html-headers":
                for entry in self.dtb._entries:
                    result += f"<h{(entry.level)}>{entry.text}</h{(entry.level)}>\n"
            case _:
                raise ValueError(f"Invalid format ({format}).")

        return result
