import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))
# Import daisy-dtb modules
from daisy_dtb import BookNavigator, DaisyBook, FolderDtbSource, LogLevel

# Clean the modules search path
del sys.path[-1]

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")


def debug(book: DaisyBook):
    navigator = BookNavigator(book)

    navigator.toc.next()
    print("SC", navigator.sections.length)

    section = navigator.sections.first()
    while section:
        print(section.text.content)
        section = navigator.sections.next()


if __name__ == "__main__":
    LogLevel.set(LogLevel.NONE)
    source = FolderDtbSource(SAMPLE_DTB_PROJECT_PATH_2)
    source.cache_size = 50
    source.enable_stats(True)
    daisy_book = DaisyBook(source)

    debug(daisy_book)
