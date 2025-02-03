import os
import sys
from time import sleep

import pygame
from getkey import getkey
from loguru import logger

# Adapt the modules search path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))


# Import daisy-dtb modules
from daisybook import DaisyBook
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

PROJECTS = [SAMPLE_DTB_PROJECT_PATH_1, SAMPLE_DTB_PROJECT_PATH_2, SAMPLE_DTB_PROJECT_URL]

LogLevel.set(LogLevel.NONE)

# Initialize the pygame mixer
pygame.mixer.init()


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
            case "A":
                # Play the first audio clip of th first section
                section = nav.sections.first()
                clip = nav.clips.first()
                if section is not None and clip is not None:
                    print(f"{section.text.content}")
                    while clip is not None:
                        print(clip.src)
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(clip.get_sound(as_bytes_io=True))
                        pygame.mixer.music.play(start=clip.begin)
                        while True:
                            pos = pygame.mixer.music.get_pos() / 1000
                            if pos >= clip.end:
                                pygame.mixer.music.stop()
                                print(f"Stopped : {pos} / {clip.end}")
                                break
                            sleep(0.05)
                        clip = nav.clips.next()
            case "Q":
                print("Exiting")
                break


if __name__ == "__main__":
    project = SAMPLE_DTB_PROJECT_PATH_1
    try:
        source = FolderDtbSource(project)
    except FileNotFoundError:
        logger.critical(f"Source {project} not found.")
        exit()

    source.cache_size = 50
    source.enable_stats(True)
    daisy_book = DaisyBook(source)
    dynamic_navigation(daisy_book)
