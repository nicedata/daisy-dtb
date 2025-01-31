import os
from pprint import pprint
from typing import List

from loguru import logger

from daisy import DaisyDtb, NccEntry
from dtbsource import DtbResource, FolderDtbResource
from logutils import LogLevel
from navigators import BaseNavigator, TocNavigator

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


def test_dtb(dtb: DaisyDtb) -> None:
    """Test DTB navigation"""
    LogLevel.set(LogLevel.DEBUG)

    # Resize buffer
    dtb.source.cache_size = 1
    dtb.source.enable_stats(True)

    nav = TocNavigator(dtb)
    nav.generate_toc("html-headers")
    exit()

    res = []

    entry: NccEntry = nav.navigate_to("lyrg0005")
    entry = nav.first()
    while entry is not None:
        res.append(entry.smil.get_full_text())
        entry = nav.next()

    # print(" ".join(res))
    # pprint(f"{dtb.source._cache.get_stats()}")

    # for par in entry.smil.pars:
    #     print(par.text.get())
    return
    while entry is not None:
        smil = entry.smil
        print("E", entry)
        pprint(smil)
        print(smil.get_full_text())
        # smilnav = BaseNavigator(entry.smil.pars)
        # xx = smilnav.first()
        # while xx is not None:
        #     print("XX", xx)
        #     xx = smilnav.next()

        # #     smil: Smil = smilnav.first()
        # #     while smil is not None:
        # #         print(smil.get_full_text())
        # #         smil = smilnav.next()
        entry = nav.next()
    print("FE", entry)

    return
    entry = nav.first()

    smil = entry.smil
    # # smil.load()

    smilnav = BaseNavigator(smil.pars)

    smilnav.first()

    print(smil.get_full_text())

    print(f"Cache queries: {dtb.source.cache_queries()}, cache hits: {dtb.source.cache_hits()}")

    # while item is not None:
    #     item.text.get()
    #     print(item.text)
    #     item = smilnav.next()


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
        source.cache_size = 10
        dtb = DaisyDtb(source)
        test_dtb(dtb)


if __name__ == "__main__":
    main()
