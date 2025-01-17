import os
from dataclasses import dataclass
from pprint import pprint
from typing import List, override

from loguru import logger

from basic_navigator import BasicNavigator
from daisy import DaisyDtb, NccEntry, NewSmil
from dtbsource import DtbResource, FolderDtbResource

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


@dataclass
class TocNavigator(BasicNavigator):
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
        super().__init__(self.dtb.entries)
        self._max_nav_level = self.dtb.get_depth()

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
        item = super().first()

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
        item = super().last()
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
        item = super().next()
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
        item = super().prev()
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

        return result


TEST_LIST_A = [
    {"id": 1, "value": "1"},  # 0
    {"id": 2, "value": "2"},  # 1
    {"id": 3, "value": "3"},  # 2
    {"id": 4, "value": "4"},  # 3
    {"id": 5, "value": "5"},  # 4
    {"id": 6, "value": "6"},  # 5
]


def test_dict_list():
    nav = BasicNavigator(TEST_LIST_A)
    item = nav.navigate_to(3)
    print(item)


def test_dtb(dtb: DaisyDtb) -> None:
    """Test DTB navigation"""

    # Resize buffer
    dtb.source.resize_buffer(20)

    nav = TocNavigator(dtb)
    entry = nav.first()

    item = nav.navigate_to("rgn_ncc_0009")
    print(item)

    return
    print(f"Entries : {len(dtb.entries)}, Smils: {len(dtb.smils)}, Depth: {dtb.get_depth()}")
    nav.increase_nav_level()
    print(nav.get_nav_level())

    entry = nav.first()
    entry = nav.next()
    return
    while entry is not None:
        print(entry.id, " -> ", entry.level)
        entry = nav.next()

    return

    entry = nav.navigate_to("rgn_ncc_0056")
    entry = nav.first()

    smilnav = BasicNavigator(dtb.smils)
    smil = smilnav.first()
    while smil is not None:
        smil = smilnav.next()

    return

    nav.first_entry()
    entry = nav.next_entry()

    smil = entry.smil

    smilnav = SmilNavigator(smil)
    par = smilnav.navigate_to("rgn_par_0002_0008")
    pprint(par)
    return

    par = smilnav.first_par()
    par = smilnav.next_par()

    clipnav = ClipNavigator(par)
    print(clipnav)

    return
    while par is not None:
        pprint(par)
        par = smilnav.next_par()
    print("-" * 80)
    par = smilnav.last_par()
    while par is not None:
        pprint(par)
        par = smilnav.prev_par()
    return

    return

    for par in smil.pars:
        for index, audio in enumerate(par.clips):
            data = dtb.source.get(audio.src)
            print(index, audio, len(data))
        print()

    for item in dtb.source.buffer._items:
        print(item.name)

    return

    for entry in dtb.entries:
        print(entry.smil_reference, entry.text)
        smil = NewSmil(dtb.source, entry.smil_reference)
        index: int = None
        try:
            index = dtb.smils.index(smil)
        except ValueError:
            ...
        if index is not None:
            dtb.smils[index].load()


def test(source: DtbResource) -> None:
    logger.info(f"Working on {source.resource_base}")
    logger.info(f"Source class is {source.__class__.__name__}")
    logger.info(f"Source {source.resource_base} is OK")

    dtb = DaisyDtb(source)
    logger.info(f"The DTB was correctly loaded: {dtb.is_valid}")
    logger.info(f"Metadata count: {len(dtb.metadata)}")
    logger.info(f"Ncc entries count: {len(dtb.entries)}")
    logger.info(f"Smil count: {len(dtb.smils)}")

    # for smil in dtb.smils:
    #     logger.info(f"Loading smil {smil.reference.resource} ...")
    #     smil.load()
    #     logger.info(f"Smil {smil.reference.resource} - Loaded {'OK' if smil.is_loaded else 'KO'}")
    logger.info(f"Finished working on {source.resource_base}\n")

    test_dtb(dtb)


def main():
    test_dict_list()

    """Perform tests"""
    paths = [SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL]
    paths = [SAMPLE_DTB_PROJECT_PATH]
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
