import os
import sys
from typing import List

import pygame
import PySide6.QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget

# Adapt the modules search path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from daisybook import DaisyBook
from navigators.book_navigator import BookNavigator
from sources.folder_source import FolderDtbSource
from utilities.logconfig import LogLevel

# Clean the modules search path
del sys.path[-1]

pygame.mixer.init()

SAMPLE_DTB_PROJECT_PATH_1 = os.path.join(os.path.dirname(__file__), "../../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_PATH_2 = os.path.join(os.path.dirname(__file__), "../../tests/samples/local/vf_2024_02_09")


# Prints PySide6 version
print(PySide6.__version__)

# Prints the Qt version used to compile PySide6
print(PySide6.QtCore.__version__)

print(SAMPLE_DTB_PROJECT_PATH_1)


# class MyWidget(QWidget):
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
        self.section_text.setText(self.navigator.section.text.content)
        self.set_status("First TOC item ready to be played...")

        # Attach button action handlers
        self.button_actions_setup()

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def update_gui(self):
        self.section_text.setText(self.navigator.section.text.content)

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
        if self.navigator.toc.is_last():
            self.set_status("We are on the last item")
        else:
            self.navigator.toc.next()
            self.set_status("")
        self.update_gui()
        self.play_clips()

    def on_prev_click(self) -> None:
        if self.navigator.toc.is_first():
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

    def play_clips(self):
        current_source: str = None
        section = self.navigator.sections.first()
        while section:
            self.set_status(f"Section{section.id}")
            self.section_text.setText(self.navigator.section.text.content)
            clip = self.navigator.clips.first()
            while clip:
                self.set_status(f"{clip.src} : start={clip.begin}, end={clip.end}")
                if current_source != clip.src:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(clip.get_sound(as_bytes_io=True))
                current_source = clip.src
                pygame.mixer.music.play(start=clip.begin)
                self.playing = True
                while True:
                    pos = pygame.mixer.music.get_pos() / 1000
                    self.set_status(f"{pos}/{clip.end}")
                    if pos >= clip.end:
                        pygame.mixer.music.pause()
                        self.set_status(f"Stopped : {pos} / {clip.end}")
                        self.playing = False
                        break
                    QApplication.processEvents()
                clip = self.navigator.clips.next()
            section = self.navigator.sections.next()

    def on_play_pause_click(self) -> None:
        if self.playing is False:
            self.set_status("Playing")
            self.btn_pause.setText("Pause")
            pygame.mixer.music.unpause()
            self.playing = True
        else:
            self.set_status("Paused")
            self.btn_pause.setText("Play")
            pygame.mixer.music.pause()
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
    source = FolderDtbSource(SAMPLE_DTB_PROJECT_PATH_2)
    source.cache_size = 50
    source.enable_stats(True)
    daisy_book = DaisyBook(source)

    app = QApplication(sys.argv)
    window = MainWindow(daisy_book)
    window.show()
    sys.exit(app.exec())
