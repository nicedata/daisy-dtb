import os
from dataclasses import dataclass
from typing import List, override

from loguru import logger

from base_navigator import BaseNavigator
from daisy import DaisyDtb, NccEntry, Parallel
from dtbsource import DtbResource, FolderDtbResource

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


@dataclass
class TocNavigator(BaseNavigator):
    """
    This class provides method to navigate in table of contents of a digital talking book.

    Notes :
        - It overrides the methods of its `Navigator` base class.
        - It also provides methods to generate a TOC of the book
    """

    dtb: DaisyDtb

    # Internal attributes
    _max_nav_level: int = 0
    _current_nav_level: int = 0

    def __post_init__(self):
        """Postinitialitation of the dataclass.
        - Initialize the base class
        - Set the max. navigation level
        """
        super().__init__(self.dtb.entries)
        self._max_nav_level = self.dtb.get_depth()
        logger.debug(f"Initialization of class {type(self)} done. Max. naigation level is {self._max_nav_level}.")

    @property
    def nav_filter_is_active(self) -> bool:
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

        if self.nav_filter_is_active:
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
        if self.nav_filter_is_active:
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
        if self.nav_filter_is_active:
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
        if self.nav_filter_is_active:
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
                for entry in self.dtb.entries:
                    result += f'{"   " * (entry.level-1)}* {entry.text}\n'
            case "md-headers":
                for entry in self.dtb.entries:
                    result += f'{"#" * (entry.level):6} {entry.text}\n'
            case "html-headers":
                for entry in self.dtb.entries:
                    result += f"<h{(entry.level)}>{entry.text}</h{(entry.level)}>\n"
            case _:
                raise ValueError(f"Invalid format ({format}).")

        return result


def test_dtb(dtb: DaisyDtb) -> None:
    """Test DTB navigation"""

    # Resize buffer
    dtb.source.resize_buffer(20)

    nav = TocNavigator(dtb)

    entry = nav.first()
    entry = nav.next()

    smil = entry.smil
    smil.load()

    smilnav = BaseNavigator(smil.pars)

    item: Parallel = smilnav.first()
    while item is not None:
        # print(item.text.get())
        item = smilnav.next()

    return


def main():
    """Perform tests"""
    paths = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]
    paths = [SAMPLE_DTB_PROJECT_PATH_2]
    sources: List[DtbResource] = []

    for path in paths:
        try:
            if path.startswith("http"):
                sources.append(FolderDtbResource(path))
            else:
                sources.append(FolderDtbResource(path))
        except FileNotFoundError:
            logger.critical(f"Source {path} not found.")
            return

    for source in sources:
        source.resize_buffer(10)
        dtb = DaisyDtb(source)
        test_dtb(dtb)


if __name__ == "__main__":
    main()
