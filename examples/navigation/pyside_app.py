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


SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")


def get_sound_as_temp_file(data: bytes) -> str:
    file_name = None
    with tempfile.NamedTemporaryFile(prefix="dtb_", mode="wb", delete=False) as temp_file:
        temp_file.write(data)
        file_name = temp_file.name
    return file_name


class MainWindow(QMainWindow):
    TITLE_FONT = QFont("Verdana", 14, QFont.Bold)
    SECTION_FONT = QFont("Verdana", 12, QFont.Bold)
    STATUS_FONT = QFont("Verdana", 10)

    def __init__(self, book: DaisyBook):
        super().__init__()
        self.setWindowTitle("DAISY 2.02 Digital Talking Book Reader")
        self.setFixedSize(800, 400)

        self.book = book
        self.navigator = BookNavigator(self.book)

        # creating a basic vlc instance
        self.vlc_player = vlc.MediaPlayer()
        time.sleep(1)
        self.playing: bool = False

        self.btn_first: QPushButton = None
        self.btn_next: QPushButton = None
        self.btn_pause: QPushButton = None
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

        # Layouts
        page_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        [buttons_layout.addWidget(_) for _ in self.buttons]

        # Build the GUI
        page_layout.addWidget(self.book_title, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addWidget(self.section_text)
        page_layout.addLayout(buttons_layout)
        page_layout.addWidget(self.status)

        # Set book title
        self.book_title.setText(self.book.title)
        self.section_text.setText(self.navigator.current_section.text.content)
        self.set_status("First TOC item ready to be played...")

        # Attach button action handlers
        self.button_actions_setup()

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def update_gui(self):
        self.section_text.setText(self.navigator.current_section.text.content)

    def button_actions_setup(self) -> None:
        self.btn_pause.clicked.connect(self.on_play_pause_click)
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
        self.update_gui()
        self.play_clips()

    def on_next_click(self) -> None:
        if self.navigator.toc.on_last():
            self.set_status("We are on the last item")
        else:
            self.navigator.toc.next()
            self.set_status("")
        self.update_gui()
        self.play_clips()

    def on_prev_click(self) -> None:
        if self.navigator.toc.on_first():
            self.set_status("We are on the first item")
        else:
            self.navigator.toc.prev()
            self.set_status("")
        self.update_gui()
        self.play_clips()

    def on_last_click(self) -> None:
        self.navigator.toc.last()
        self.set_status("Last")
        self.update_gui()
        self.play_clips()

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
            QApplication.processEvents()
            time.sleep(0.1)  # Be nice with CPU

        # Issue a 'pause' to performe quick calculations
        self.vlc_player.pause()

        # Wait until ppause state OK
        while self.vlc_player.get_state().value != 4:
            QApplication.processEvents()
            time.sleep(0.1)  # Be nice with CPU

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
            QApplication.processEvents()
            time.sleep(0.1)  # Be nice with CPU

        self.playing = True
        while self.vlc_player.get_state().value == 3:
            # Get curren position
            pos = self.vlc_player.get_position()

            # Check if end reached...
            if pos >= end_pc:
                self.vlc_player.pause()
                self.playing = False
                break

            QApplication.processEvents()
            time.sleep(0.1)  # Be nice with CPU

    def play_clips(self):
        section = self.navigator.sections.first()
        while section:
            self.set_status(f"Section{section.id}")
            self.section_text.setText(self.navigator.current_section.text.content)

            clip = self.navigator.clips.first()
            current_source = ""
            current_file = ""
            while clip:
                self.set_status(f"{clip.src} : start={clip.begin}, end={clip.end}")
                if current_source != clip.src:
                    try:
                        os.unlink(current_file)
                    except FileNotFoundError:
                        ...
                    current_file = get_sound_as_temp_file(clip.get_sound())
                    current_source = clip.src
                    media = vlc.Media(current_file)
                    self.vlc_player.set_media(media)

                # Issue a 'play' to force data load
                self.vlc_player.play()
                while self.vlc_player.get_state().value != 3:
                    QApplication.processEvents()

                # Issue a 'pause' to performe quick calculations
                self.vlc_player.pause()
                while self.vlc_player.get_state().value != 4:
                    QApplication.processEvents()

                # Get MP3 size, in seconds
                mp3_length = self.vlc_player.get_length() / 1000

                # Use fraction of the total length (0..1)
                start_pc = clip.begin / mp3_length
                end_pc = (clip.begin + clip.duration - 0.1) / mp3_length  #! - 0.1 is to commpensate processing overhead
                self.vlc_player.set_position(start_pc)

                self.vlc_player.play()
                while self.vlc_player.get_state().value != 3:
                    QApplication.processEvents()
                    time.sleep(0.1)  # Be nice with CPU

                self.playing = True
                while self.vlc_player.get_state().value == 3:
                    pos = self.vlc_player.get_position()
                    if pos >= end_pc:
                        self.vlc_player.pause()
                        self.playing = False
                        break
                    QApplication.processEvents()
                    time.sleep(0.1)  # Be nice with CPU

                clip = self.navigator.clips.next()
            section = self.navigator.sections.next()

    def on_play_pause_click(self) -> None:
        if self.playing is False:
            self.set_status("Playing")
            self.btn_pause.setText("Pause")
            self.playing = True
        else:
            self.set_status("Paused")
            self.btn_pause.setText("Play")
            self.playing = False

    def _create_buttons(self) -> List[QPushButton]:
        self.btn_first = QPushButton("First")
        self.btn_first.setFixedSize(100, 60)
        self.btn_next = QPushButton("Next")
        self.btn_next.setFixedSize(100, 60)
        self.btn_pause = QPushButton("Play")
        self.btn_pause.setFixedSize(100, 60)
        self.btn_prev = QPushButton("Prev")
        self.btn_prev.setFixedSize(100, 60)
        self.btn_last = QPushButton("Last")
        self.btn_last.setFixedSize(100, 60)
        return [self.btn_first, self.btn_next, self.btn_pause, self.btn_prev, self.btn_last]


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
