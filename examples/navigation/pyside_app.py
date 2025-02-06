"""
This is a very basic PySide6 application that shows what we can do with the daisy-dtb package.

In this QApplication based application we do this :

    - Setup of a Daisy Book source with `FolderDtbSource`.
    - Create a `DaisyBook` instance from the source.
    - Pass the `DaisyBook` to a `QMainWindow`.
    - Create GUI elements (`QtWidgets`).
    - Handle `QPushButton` events to navigate in the book

Notes :

    - To play the audio clips, the `python-vlc` package is used.
"""

import os
import sys
import tempfile
import time
from typing import List

import vlc
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget

# Adapt the modules search path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from daisybook import DaisyBook
from models.audio import Audio
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

APP_TITLE = "DAISY 2.02 Digital Talking Book Reader"
SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")
BUFFER_FILE_PATH = f"{tempfile.gettempdir()}/_pyside_buffer_.tmp"


def get_sound_as_temp_file(data: bytes) -> str:
    """Create a temporary sound file.

    We do this because `python-vlc` cannot handle `BytesIO` as a media source.

    This is not so nice, but allowed us to focus on GUI application.

    Args:
        data (bytes): the sound bytes.

    Returns:
        str: a file name.
    """
    with open(BUFFER_FILE_PATH, "wb") as file:
        file.write(data)
        file_name = file.name
    return file_name


class MainWindow(QMainWindow):
    TITLE_FONT = QFont("Verdana", 14, QFont.Bold)
    SECTION_FONT = QFont("Verdana", 12, QFont.Bold)
    STATUS_FONT = QFont("Verdana", 10)

    def __init__(self, book: DaisyBook):
        """Instance initilization.

        Args:
            book (DaisyBook): the book to play with.
        """
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(800, 400)

        self.book = book
        self.navigator = BookNavigator(self.book)

        # creating a basic vlc instance
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()
        time.sleep(1)

        # Buttons
        self.btn_first: QPushButton = None
        self.btn_next: QPushButton = None
        self.btn_prev: QPushButton = None
        self.btn_last: QPushButton = None

        # GUI elements
        self.buttons: List[QPushButton] = self._create_buttons()
        self.book_title = QLabel("Book Title goes here")
        self.book_title.setFont(MainWindow.TITLE_FONT)
        self.book_title.setStyleSheet("color: rgb(0, 102, 204)")
        self.section_text = QTextEdit("Current Section Text goes here", readOnly=True)
        self.section_text.setFont(MainWindow.SECTION_FONT)
        self.section_text.setStyleSheet("background-color: yellow")
        self.status = QLabel("Messages go here")
        self.status.setFont(MainWindow.STATUS_FONT)

        # Page layout
        page_layout = QVBoxLayout()

        # Buttons layout
        buttons_layout = QHBoxLayout()
        [buttons_layout.addWidget(_) for _ in self.buttons]

        # Build the GUI
        page_layout.addWidget(self.book_title, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addWidget(self.section_text)
        page_layout.addLayout(buttons_layout)
        page_layout.addWidget(self.status)

        # Set book title
        self.book_title.setText(self.book.title)
        self.section_text.setText(self.navigator.section_text)
        self.set_status("First TOC item ready to be played...")

        # Attach button action handlers
        self.button_actions_setup()

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def closeEvent(self, event):
        self.vlc_player.stop()
        self._wait_and_process_events()
        self.vlc_player.release()

    def button_actions_setup(self) -> None:
        self.btn_first.clicked.connect(self.on_first_click)
        self.btn_next.clicked.connect(self.on_next_click)
        self.btn_prev.clicked.connect(self.on_prev_click)
        self.btn_last.clicked.connect(self.on_last_click)

    def set_status(self, text: str):
        self.status.setText(text)
        QApplication.processEvents()

    def on_first_click(self) -> None:
        self.navigator.toc.first()
        self.set_status("First")
        self.section_text.setText(self.navigator.section_text)
        self.play_clips()

    def on_next_click(self) -> None:
        if self.navigator.toc.on_last():
            self.set_status("We are on the last item")
        else:
            self.navigator.toc.next()
            self.set_status("")
        self.section_text.setText(self.navigator.section_text)
        self.play_clips()

    def on_prev_click(self) -> None:
        if self.navigator.toc.on_first():
            self.set_status("We are on the first item")
        else:
            self.navigator.toc.prev()
            self.set_status("")
        self.section_text.setText(self.navigator.section_text)
        self.play_clips()

    def on_last_click(self) -> None:
        self.navigator.toc.last()
        self.set_status("Last")
        self.section_text.setText(self.navigator.section_text)
        self.play_clips()

    def _wait_and_process_events(self):
        status_text = ""
        match self.vlc_player.get_state().value:
            case 1:
                status_text = "Opening"
            case 2:
                status_text = "Buffering"
            case 3:
                status_text = "Playing"
            case 4:
                status_text = "Paused"
            case 5:
                status_text = "Stopped"
            case 6:
                status_text = "Ended"
            case 7:
                status_text = "Error"
            case _:
                status_text = ""
        self.set_status(status_text)
        QApplication.processEvents()
        time.sleep(0.1)  # Be nice with CPU

    def play_clip(self, clip: Audio) -> None:
        """Play a clip.

        It's a bit complicated, but works.

        We did some research on the python-vlc package to make it work...

        Args:
            clip (Audio): the clip.
        """
        # Issue a 'play' to force data load
        self.vlc_player.play()

        # Wait until play state OK
        while self.vlc_player.get_state().value != 3:
            self._wait_and_process_events()

        # Issue a 'pause' to performe quick calculations
        self.vlc_player.pause()

        # Wait until pause state OK
        while self.vlc_player.get_state().value != 4:
            self._wait_and_process_events()

        # Get MP3 size, in seconds
        mp3_length = self.vlc_player.get_length() / 1000

        # Use fraction of the total length (0..1)
        start_pc = clip.begin / mp3_length
        end_pc = (clip.begin + clip.duration - 0.1) / mp3_length  #! - 0.1 is to commpensate processing overhead

        # Set the clip start position & play !
        self.vlc_player.set_position(start_pc)
        self.vlc_player.play()

        # Wait until play state OK
        while self.vlc_player.get_state().value != 3:
            self._wait_and_process_events()

        while self.vlc_player.get_state().value == 3:
            # Get current position
            pos = self.vlc_player.get_position()

            # Check if end reached...
            if pos >= end_pc:
                self.vlc_player.pause()
                break
            self._wait_and_process_events()
        self._wait_and_process_events()

    def play_clips(self):
        _, section, clip = self.navigator.context
        while section:
            self.set_status(f"Section{section.id}")
            self.section_text.setText(self.navigator.section_text)

            clip = self.navigator.clips.first()
            current_source = ""
            sound_file = ""
            while clip:
                self.set_status(f"{clip.src} : start={clip.begin}, end={clip.end}")
                if current_source != clip.src:
                    sound_file = get_sound_as_temp_file(clip.get_sound())
                    current_source = clip.src
                    media = self.vlc_instance.media_new(sound_file)
                    self.vlc_player.set_media(media)

                    # Play the clip
                    self.play_clip(clip)

                clip = self.navigator.clips.next()
            section = self.navigator.sections.next()

    def _create_buttons(self) -> List[QPushButton]:
        self.btn_first = QPushButton("First")
        self.btn_first.setFixedSize(100, 60)
        self.btn_next = QPushButton("Next")
        self.btn_next.setFixedSize(100, 60)
        self.btn_prev = QPushButton("Prev")
        self.btn_prev.setFixedSize(100, 60)
        self.btn_last = QPushButton("Last")
        self.btn_last.setFixedSize(100, 60)
        return [self.btn_first, self.btn_next, self.btn_prev, self.btn_last]


if __name__ == "__main__":
    LogLevel.set(LogLevel.NONE)
    source = FolderDtbSource(SAMPLE_DTB_PROJECT_PATH_1)
    source.cache_size = 50
    source.enable_stats(True)
    daisy_book = DaisyBook(source)

    app = QApplication(sys.argv)
    window = MainWindow(daisy_book)
    window.show()
    sys.exit(app.exec())
