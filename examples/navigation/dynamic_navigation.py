# Adapt the modules search path
import os
import sys
from typing import List

from getkey import getkey
from loguru import logger

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from daisybook import DaisyBook

# Import daisy-dtb modules
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

LogLevel.set(LogLevel.NONE)


# def test_dtb(dtb: DaisyBook) -> None:
#     """Test DTB navigation"""
#     LogLevel.set(LogLevel.NONE)


#         # print(entry.text)

#     dtb.toc.set_nav_level(1)
#     entry = dtb.toc.first()
#     while entry:
#         section = entry.sections.first()
#         while section:
#             clip_nav = section.clips
#             clip = clip_nav.first()
#             while clip:
#                 print(clip)
#                 clip = clip_nav.next()
#             section = entry.sections.next()

#             print("-" * 80)
#         entry = dtb.toc.next()

#     pprint(dtb.cache_stats)
#     print("^" * 80)
#     return

#     res = []

#     entry: TocEntry = dtb._toc_navigator.navigate_to("lyrg0005")
#     entry = dtb._toc_navigator.first()
#     while entry is not None:
#         res.append(entry.smil.get_full_text())
#         entry = dtb._toc_navigator.next()

#     # print(" ".join(res))
#     # pprint(f"{dtb.source._cache.get_stats()}")

#     # for par in entry.smil.pars:
#     #     print(par.text.get())
#     # return
#     # while entry is not None:
#     #     smil = entry.smil
#     #     print("E", entry)
#     #     pprint(smil)
#     #     print(smil.get_full_text())
#     #     # smilnav = BaseNavigator(entry.smil.pars)
#     #     # xx = smilnav.first()
#     #     # while xx is not None:
#     #     #     print("XX", xx)
#     #     #     xx = smilnav.next()

#     #     # #     smil: Smil = smilnav.first()
#     #     # #     while smil is not        None:
#     #     # #         print(smil.get_full_text())
#     #     # #         smil = smilnav.next()
#     #     entry = dtb.toc_navigator.next()
#     # print("FE", entry)

#     # return
#     # entry = nav.first()

#     # smil = entry.smil
#     # # # smil.load()

#     # smilnav = BaseNavigator(smil.pars)

#     # smilnav.first()

#     # print(smil.get_full_text())

#     # print(f"Cache queries: {dtb.source.cache_queries()}, cache hits: {dtb.source.cache_hits()}")


#     # # while item is not None:
#     # #     item.text.get()
#     # #     print(item.text)
#     # #     item = smilnav.next()
def dynamic_navigation(book: DaisyBook) -> None:
    print(book.title)
    # Create a BookNavigator instance
    nav = BookNavigator(book)

    entry = nav.toc.first()
    while True:
        key = getkey(blocking=True)
        if not isinstance(key, str):
            continue
        match key.upper():
            case "F":
                print("TOC first")
                entry = nav.toc.first()
            case "N":
                print("TOC next")
                new_entry = nav.toc.next()
                if new_entry is None:
                    print("Last entry !")
                else:
                    entry = new_entry
            case "P":
                print("TOC previous")
                new_entry = nav.toc.prev()
                if new_entry is None:
                    print("First entry !")
                else:
                    entry = new_entry
            case "L":
                print("TOC last")
                entry = nav.toc.last()
            case "T":
                print("Text")
                print(entry.text)
            case "Q":
                print("Exiting")
                break


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
        dynamic_navigation(daisy_book)
