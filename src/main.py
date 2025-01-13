import os
from dataclasses import dataclass
from pprint import pprint
from typing import List

from loguru import logger

from daisy import DaisyDtb, NccEntry, NewSmil
from dtbsource import DtbResource, FolderDtbResource

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


@dataclass
class DaisyDtbNavigator:
    dtb: DaisyDtb
    max_nav_level: int = 0
    current_nav_level: int = 0
    current_ncc_entry_index: int = -1
    max_ncc_entry_index: int = 0

    def __post_init__(self):
        self.max_nav_level = self.dtb.get_depth()
        self.max_ncc_entry_index: int = len(self.dtb.entries) - 1

    def set_nav_level(self, level: int) -> int:
        if level < 0 or level > self.max_nav_level:
            return self.current_nav_level
        self.current_nav_level = level
        return self.current_nav_level

    def first_entry(self):
        self.current_ncc_entry_index = 0
        if self.current_nav_level > 0:
            for index, entry in enumerate(self.dtb.entries):
                print(f"index {index}, self.current_nav_level: {self.current_nav_level}, entry.level: {entry.level}, check: {self.current_nav_level == entry.level}")
                if entry.level == self.current_nav_level:
                    self.current_ncc_entry_index = index
                    break
        else:
            self.current_ncc_entry_index = 0

        return self.dtb.entries[self.current_ncc_entry_index]

    def last_entry(self):
        self.current_ncc_entry_index = self.max_ncc_entry_index
        return self.dtb.entries[self.current_ncc_entry_index]

    def next_entry(self) -> NccEntry:
        if self.current_nav_level > 0:
            for index in range(self.current_ncc_entry_index + 1, self.max_ncc_entry_index):
                if self.dtb.entries[index].level == self.current_nav_level:
                    self.current_ncc_entry_index = index
                    break
        else:
            self.current_ncc_entry_index = self.current_ncc_entry_index + 1 if self.current_ncc_entry_index < self.max_ncc_entry_index else self.current_ncc_entry_index
        return self.dtb.entries[self.current_ncc_entry_index]

    def prev_entry(self) -> NccEntry:
        self.current_ncc_entry_index = self.current_ncc_entry_index - 1 if self.current_ncc_entry_index > 0 else self.current_ncc_entry_index
        return self.dtb.entries[self.current_ncc_entry_index]


def test_dtb(dtb: DaisyDtb) -> None:
    """Test DTB navigation"""

    nav = DaisyDtbNavigator(dtb)
    print(f"Entries : {len(dtb.entries)}, Smils: {len(dtb.smils)}, Depth: {dtb.get_depth()}")

    print("Level:", nav.set_nav_level(1))
    print("First", nav.first_entry())
    print("Next", nav.next_entry())

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
        test(source)


if __name__ == "__main__":
    main()
