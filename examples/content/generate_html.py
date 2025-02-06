"""
Generate HTML code from a book.

Two methods are used :
    - Method A : cycle through the toc entries and the sections (for loops)
    - Method B : use a book navigator (while loops)
"""

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

# Set debug level
LogLevel.set(LogLevel.DEBUG)


def generate_html_way_A(book: DaisyBook):
    """Generate an HTML document from a book.

    - In this example we cycle through the toc entries and the sections (for loops).

    Args:
        book (DaisyBook): the book.
    """
    html = [f'<!DOCTYPE html>\n<html lang="{book.langage}">\n<head>\n<meta charset="{book.charset}">\n<title>{book.title}</title>\n</head>\n<body>']

    for entry in book.toc_entries:
        # Indentation makes it nice !
        indent = "   " * entry.level
        spacer = "   "
        # Header
        html.append(f"{indent}<h{entry.level}>{entry.text}</h{entry.level}>")
        # Sections
        for section in entry.sections:
            html.append(f"{indent}<p>\n{indent}{spacer}{section.text.content}\n{indent}</p>")
    html.append("</body>\n</html>")

    print("\n".join(html))


def generate_html_way_B(book: DaisyBook):
    """Generate an HTML document from a book.

    - In this example we use a book navigator (while loops)

    Args:
        book (DaisyBook): the book.
    """
    html = [f'<!DOCTYPE html>\n<html lang="{book.langage}">\n<head>\n<meta charset="{book.charset}">\n<title>{book.title}</title>\n</head>\n<body>']

    # Create a BookNavigator instance
    nav = BookNavigator(book)

    entry = nav.toc.first()
    while entry is not None:
        # Indentation makes it nice !
        indent = "   " * entry.level
        spacer = "   "
        # Header
        html.append(f"{indent}<h{entry.level}>{entry.text}</h{entry.level}>")

        # Sections
        section = nav.sections.first()
        while section is not None:
            html.append(f"{indent}<p>\n{indent}{spacer}{section.text.content}\n{indent}</p>")
            # Next section (or None)
            section = nav.sections.next()

        # Next entry (or None)
        entry = nav.toc.next()

    print("\n".join(html))


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
        generate_html_way_A(daisy_book)
        generate_html_way_B(daisy_book)
        print(f"Cache efficiency: {daisy_book.cache_stats['cache_efficiency']:.2%}")
