"""Working with book metadata"""

import os
import sys
from typing import List

from loguru import logger

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))


# Import daisy-dtb modules
from book.daisybook import DaisyBook
from sources.folder_source import FolderDtbSource
from sources.source import DtbSource
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

PROJECTS = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]

LogLevel.set(LogLevel.NONE)


def list_metadata(book: DaisyBook):
    """List book metadata.

    Args:
        book (DaisyBook): the book.
    """
    print("-" * len(book.title))
    print(book.title)
    print("-" * len(book.title))

    print("Dublin Core metadata:\n")
    metadata = book.dc_metadata
    if len(metadata) == 0:
        print("No DC metadata found.")
    else:
        for meta in metadata:
            print(meta)
    print()

    print("Navigation Control Center metadata:\n")
    metadata = book.ncc_metadata
    if len(metadata) == 0:
        print("No NCC metadata found.")
    else:
        for meta in metadata:
            print(meta)
    print()

    print("Other metadata:\n")
    metadata = book.other_metadata
    if len(metadata) == 0:
        print("No Other metadata found.")
    else:
        for meta in metadata:
            print(meta)
    print()


if __name__ == "__main__":
    sources: List[DtbSource] = []
    for project in PROJECTS:
        try:
            sources.append(FolderDtbSource(project))
        except FileNotFoundError:
            logger.critical(f"Source {project} not found.")
            exit()

    for source in sources:
        source.cache_size = 50
        source.enable_stats(True)
        daisy_book = DaisyBook(source)
        list_metadata(daisy_book)
