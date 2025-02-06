"""
This is a very basic application that shows what we can do with the daisy-dtb package.

In this command-line based application we do this :

    - Setup of a Daisy Book source with `FolderDtbSource`.
    - Create a `DaisyBook` instance from the source.
    - Associate a `BookNavigator` with this Daisy Book.
    - The user can then use the keyboard to navigate in the book.

Key actions :

    - H or ? : print a help message
    - F      : go to first TOC item
    - N      : go to next TOC item
    - P      : go to previous TOC item
    - L      : go to last TOC item
    - A      : play current section audio clips
    - Q      : Quit the application

Notes :

    - To play the audio clips, the `pygame` package is used.
    - To get the user key pres actions, we use the `getkey` package.
"""

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

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


# Set the log level
LogLevel.set(LogLevel.NONE)

# Initialize the pygame mixer
pygame.mixer.init()


def print_usage() -> None:
    """Print usage message."""
    usage = [
        "? or H : Print this message",
        "  F    : Go to first TOC item",
        "  N    : Go to next TOC item",
        "  P    : Go to previous TOC item",
        "  L    : Go to last TOC item",
        "  A    : Play current section audio",
        "  Q    : Quit the application",
    ]
    print("\n".join(usage))


def keyboard_navigation(book: DaisyBook) -> None:
    """Navigate in a Daisy Book using the keyboard.

    Args:
        book (DaisyBook): the book to navigate in.
    """
    print_usage()
    print(f"Current book : {book.title}")

    # Create a BookNavigator instance
    nav = BookNavigator(book)
    print(f"{nav.current_toc_entry.id} : {nav.current_toc_entry.text} | {len(nav.current_toc_entry.sections)} section(s).")

    # Process the keystrokes...
    while True:
        key = getkey(blocking=True)
        if not isinstance(key, str):
            continue
        # Handle the keys
        match key.upper():
            case "?" | "H":
                print_usage()
            case "F":
                if nav.toc.on_first():
                    continue
                entry = nav.toc.first()
                print(f"{entry.id} : {entry.text} | {len(entry.sections)} section(s).")
            case "N":
                if nav.toc.on_last():
                    continue
                entry = nav.toc.next()
                print(f"{entry.id} : {entry.text} | {len(entry.sections)} section(s).")
            case "P":
                if nav.toc.on_first():
                    continue
                entry = nav.toc.prev()
                print(f"{entry.id} : {entry.text} | {len(entry.sections)} section(s).")
            case "L":
                if nav.toc.on_last():
                    continue
                entry = nav.toc.last()
                print(f"{entry.id} : {entry.text} | {len(entry.sections)} section(s).")
            case "A":
                # Play the audio clip(s) of the first section

                # Get the navigator's context
                _, section, clip = nav.context
                if section is not None and clip is not None:
                    clip_source = ""
                    print(f"{section.text.content} | {len(section.clips)} clip(s)")
                    while clip is not None:
                        print(f"Clip : {clip.src}, duration: {clip.duration:.3f}s")

                        # Check if clip already loaded in pygame
                        if clip.src != clip_source:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(clip.get_sound(as_bytes_io=True))
                            clip_source = clip.src

                        # Play the clip
                        pygame.mixer.music.play(start=clip.begin)
                        pos = pygame.mixer.music.get_pos() / 1000
                        while pos < clip.end and pos >= 0:  # Sometimes, pos is negative...
                            # Display current position
                            print(f"Position : {pos:.3f}s", end="\r")
                            sleep(0.01)
                            pos = pygame.mixer.music.get_pos() / 1000
                        pygame.mixer.music.pause()

                        # Clean position display
                        print(" " * 30, end="\r")
                        print(f"Stopped playing {clip.src} from {clip.begin}s to {clip.end}s. Player position: {pos:.3f}s")
                        clip = nav.clips.next()
            case "Q":
                print("Exiting")
                return 0


if __name__ == "__main__":
    project = SAMPLE_DTB_PROJECT_PATH
    try:
        source = FolderDtbSource(project)
    except FileNotFoundError:
        logger.critical(f"Source {project} not found.")
        sys.exit(-1)

    source.cache_size = 50
    source.enable_stats(True)
    daisy_book = DaisyBook(source)
    sys.exit(keyboard_navigation(daisy_book))
