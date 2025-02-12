from dataclasses import dataclass, field
from typing import List, override

from loguru import logger

from ..models.toc_entry import TocEntry
from .base_navigator import BaseNavigator


@dataclass
class TocNavigator(BaseNavigator):
    """
    This class provides method to navigate in table of contents of a digital talking book.
    The TOC is provided by the ncc.html file, common in Daisy 2.02 projects.

    Notes :
        - It overrides the methods of its `Navigator` base class.
        - It also provides methods to generate a TOC of the book
    """

    toc_entries: List[TocEntry]
    navigation_depth: int

    # Internal attributes
    _max_nav_level: int = field(init=False, default=0)
    _current_nav_level: int = field(init=False, default=0)

    def __post_init__(self):
        """Postinitialitation of the dataclass.

        Action(s):
            - Initialize the base class
            - Set the max. navigation level
        """
        super().__init__(self.toc_entries)
        self._max_nav_level = self.navigation_depth
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
    def first(self) -> TocEntry:
        """Get the first NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the first entry
        """
        item: TocEntry = super().first()

        if self.filter_is_active:
            # Enumerate upwards
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().next()

        return item

    @override
    def last(self) -> TocEntry:
        """Get the last NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the last entry
        """
        item: TocEntry = super().last()
        if self.filter_is_active:
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().prev()

        return item

    @override
    def next(self) -> TocEntry | None:
        """Get the next NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the next entry
        """
        item: TocEntry = super().next()
        if self.filter_is_active:
            while item is not None:
                if item.level == self._current_nav_level:
                    break
                item = super().next()

        return item

    @override
    def prev(self) -> TocEntry | None:
        """Get the previous NCC entry.
        - If a level filter is active, it is taken into account.

        Returns:
            NccEntry: the previous entry
        """
        item: TocEntry = super().prev()
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
                for entry in self.toc_entries:
                    result += f'{"   " * (entry.level-1)}* {entry.text}\n'
            case "md-headers":
                for entry in self.toc_entries:
                    result += f'{"#" * (entry.level):6} {entry.text}\n'
            case "html-headers":
                for entry in self.toc_entries:
                    result += f"<h{(entry.level)}>{entry.text}</h{(entry.level)}>\n"
            case _:
                raise ValueError(f"Invalid format ({format}).")

        return result
