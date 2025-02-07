import os
import sys
from typing import List

from loguru import logger

# Adapt the modules search path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

# Import daisy-dtb modules
from book.daisybook import DaisyBook
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from sources.source import DtbSource
from utilities.fetcher import Fetcher
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

PROJECTS = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]

LogLevel.set(LogLevel.NONE)


def book_nav_toc_first_to_last_page(book: DaisyBook):
    """Navigate a book from the first to the last page.

    Args:
        book (DaisyBook): a Daisy book.
    """
    print("*" * 80)
    print("TOC navigation from first to last page")
    print("*" * 80)

    # Create a BookNavigator instance
    nav = BookNavigator(book)

    # Iterate over the TOC, with level selection
    for level in range(book.navigation_depth + 1):
        print(f"Navigation through '{book.title}'. Level filter is {'not set.' if nav.toc.get_nav_level()== 0 else nav.toc.get_nav_level()}", end="\n\n")
        toc_entry = nav.toc.first()
        while toc_entry:
            print(f"TOC item. Level is {toc_entry.level}.The text is '{toc_entry.text}'")
            toc_entry = nav.toc.next()
        print("=" * 80, end="\n\n")
        nav.toc.increase_nav_level()

    print(f"Fetcher statistics : {Fetcher.get_stats()}")
    print("^" * 80, end="\n\n")


def book_nav_toc_last_to_first_page(book: DaisyBook):
    """Navigate a book from the last to the first page.

    Args:
        book (DaisyBook): a Daisy book.
    """
    print("*" * 80)
    print("TOC navigation from last to first page")
    print("*" * 80)
    # print("=" * 80, end="\n\n")

    # Create a BookNavigator instance
    nav = BookNavigator(book)

    # Iterate over the TOC, with level selection
    for level in range(book.navigation_depth + 1):
        print(f"Navigation through '{book.title}'. Level filter is {'not set.' if nav.toc.get_nav_level()== 0 else nav.toc.get_nav_level()}", end="\n\n")
        toc_entry = nav.toc.last()
        while toc_entry:
            print(f"TOC item. Level is {toc_entry.level}.The text is '{toc_entry.text}'")
            toc_entry = nav.toc.prev()
        print("=" * 80, end="\n\n")
        nav.toc.increase_nav_level()

    print(f"Fetcher statistics : {Fetcher.get_stats()}")
    print("^" * 80, end="\n\n")


def main():
    sources: List[DtbSource] = []
    for project in PROJECTS:
        print(project)
        try:
            sources.append(FolderDtbSource(project))
        except FileNotFoundError:
            logger.critical(f"Source {project} not found.")
            exit()

    for source in sources:
        source.cache_size = 50
        source.enable_stats(True)
        dtb = DaisyBook(source)
        book_nav_toc_first_to_last_page(dtb)
        book_nav_toc_last_to_first_page(dtb)


if __name__ == "__main__":
    main()
