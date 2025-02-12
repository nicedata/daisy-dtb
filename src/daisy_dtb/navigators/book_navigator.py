from dataclasses import dataclass, field
from typing import Tuple

from ..book.daisybook import DaisyBook
from ..models import Audio, Section, TocEntry
from .clip_navigator import ClipNavigator
from .section_navigator import SectionNavigator
from .toc_navigator import TocNavigator


class BookNavigatorException(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass
class BookNavigator:
    """This class provides book navigation features.

    It provides 3 navigators:
        - A Table Of Content navigator to navigate in the TOC items.
        - A section navigator to navigate in the sections of the current TOC entry.
        - A clip navigator to navigate in the current sections clips.

    Notes:
        - On class instanciation, section and clip pointers are set to the first section and clip respectively.
        - On TOC navigation, section and clip pointers are set to the first section and clip respectively
        - On Section navigation, the clip pointer is set to the first clip of the section

    Raises:
        BookNavigatorException: raised when the supplied instance creation is not a valid `DaisyBook` instance.
    """

    book: DaisyBook
    toc: TocNavigator = field(init=False, default=None)
    sections: SectionNavigator = field(init=False, default=None)
    clips: ClipNavigator = field(init=False, default=None)

    # Private attributes
    _current_entry: TocEntry = field(init=False, default=None)
    _current_section: Section = field(init=False, default=None)
    _current_clip: Audio = field(init=False, default=None)

    @property
    def context(self) -> Tuple[TocEntry, Section, Audio]:
        """Get the current context.

        The context is a tuple containing:
            - the current TOC entry
            - the current section
            - the current clip

        Returns:
            Tuple[TocEntry, Section, Audio]: the current context.
        """
        return (self._current_entry, self._current_section, self._current_clip)

    @property
    def section_text(self) -> str:
        """Get the current section's text.

        Returns:
            str: the current section's text.
        """
        return self._current_section.text.content

    @property
    def toc_text(self) -> str:
        """Get the current TOC entry's text.

        Returns:
            str: the current TOC entry's text.
        """
        return self._current_entry.text

    @property
    def current_toc_entry(self) -> TocEntry:
        """Get the current TOC entry.

        Returns:
            TocEntry: the current TOC entry.
        """
        return self._current_entry

    @property
    def current_section(self) -> Section:
        """Gets the current section.

        Returns:
            Section: the current section.
        """
        return self._current_section

    @property
    def current_clip(self) -> Audio:
        """Gets the current clip.

        Returns:
            Audio: Gets the current clip.
        """
        return self._current_clip

    def __post_init__(self):
        """`BookNavigator` instance post-initialization.

        - Sets the private attributes of the class.
        - Adds callback method to maintain synchronization between the 3 navigators (toc, sections, clips).

        Raises:
            BookNavigatorException: _description_
        """
        if not isinstance(self.book, DaisyBook):
            raise BookNavigatorException("The supplied parameter is not valid.")

        self.toc = TocNavigator(self.book.toc_entries, self.book.navigation_depth)
        self.toc.set_callback(self.on_toc_navigation)
        self._current_entry = self.toc.first()

    def on_toc_navigation(self, toc_entry: TocEntry) -> None:
        self._current_entry = toc_entry
        self.sections = SectionNavigator(toc_entry.sections, self.on_section_navigation)
        self._current_section = self.sections.first()

    def on_section_navigation(self, section: Section) -> None:
        self._current_section = section
        self.clips = ClipNavigator(section._clips, self.on_clip_navigation)
        self._current_clip = self.clips.first()

    def on_clip_navigation(self, clip: Section) -> None:
        self._current_clip = clip
