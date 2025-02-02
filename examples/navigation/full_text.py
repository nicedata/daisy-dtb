import os
import sys
from typing import List

from loguru import logger

# Adapt the modules search path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

# Import daisy-dtb modules
from daisybook import DaisyBook
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from sources.source import DtbSource
from utilities.logconfig import LogLevel

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

PROJECTS = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]

# Clean the modules search path
del sys.path[-1]


# Set logging level
LogLevel.set(LogLevel.NONE)


def show_full_text(book: DaisyBook) -> None:
    """Display the full text of a Daisy book.

    Args:
        dtb (DaisyBook): the Daisy book.
    """
    # Create a BookNavigator instance
    nav = BookNavigator(book)

    # Iterate over the TOC, with level selection
    for _ in range(book.navigation_depth + 1):
        print(f"Full text in '{book.title}' display. Level filter is {'not set.' if nav.toc.get_nav_level()== 0 else nav.toc.get_nav_level()}", end="\n\n")
        # TOC navigation
        toc_entry = nav.toc.first()
        while toc_entry:
            header = f"TOC item. Level is {toc_entry.level}.The TOC text is '{toc_entry.text}'. Sections text below."
            print("-" * 150)
            print(header)
            print("-" * 150)
            section = nav.sections.first()
            while section:
                print(section.text.content)
                section = nav.sections.next()
            toc_entry = nav.toc.next()
        print("=" * 80, end="\n\n")
        nav.toc.increase_nav_level()


def show_full_text_with_clips(book: DaisyBook) -> None:
    """Display the full text of a Daisy book as well as the realated audio clips.

    Args:
        dtb (DaisyBook): the Daisy book.
    """
    # Create a BookNavigator instance
    nav = BookNavigator(book)

    # Iterate over the TOC, with level selection
    for _ in range(book.navigation_depth + 1):
        print(f"Full text in '{book.title}' display. Level filter is {'not set.' if nav.toc.get_nav_level()== 0 else nav.toc.get_nav_level()}", end="\n\n")
        # TOC navigation
        toc_entry = nav.toc.first()
        while toc_entry:
            header = f"TOC item. Level is {toc_entry.level}.The TOC text is '{toc_entry.text}'. Sections text below."
            print("-" * 150)
            print(header)
            print("-" * 150)
            section = nav.sections.first()
            while section:
                for clip in section.clips:
                    print(f"{section.text.content:60.60s} | Clip source: {clip.src}, range: {clip.begin:.2f}s -> {clip.end:.2f}s (dur.: {clip.duration:.2f}s)")
                section = nav.sections.next()
            toc_entry = nav.toc.next()
        print("=" * 80, end="\n\n")
        nav.toc.increase_nav_level()


def main():
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
        show_full_text(daisy_book)
        show_full_text_with_clips(daisy_book)


if __name__ == "__main__":
    main()
