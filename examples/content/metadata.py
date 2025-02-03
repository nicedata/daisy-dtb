"""Working with metadata"""

import os
import sys
from typing import List

from loguru import logger

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))


# Import daisy-dtb modules
from daisybook import DaisyBook
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from sources.source import DtbSource
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

PROJECTS = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]


def list_all_metadata(book: DaisyBook):
    for meta in book.metadata:
        print(meta)


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
        list_all_metadata(daisy_book)
