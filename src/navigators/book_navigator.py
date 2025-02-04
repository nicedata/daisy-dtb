from dataclasses import dataclass, field

from daisybook import DaisyBook
from models import Audio, Section, TocEntry
from navigators.clip_navigator import ClipNavigator
from navigators.section_navigator import SectionNavigator
from navigators.toc_navigator import TocNavigator


class BookNavigatorException(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass
class BookNavigator:
    """This class provides book navigation features."""

    book: DaisyBook
    toc: TocNavigator = field(init=False, default=None)
    sections: SectionNavigator = field(init=False, default=None)
    clips: ClipNavigator = field(init=False, default=None)

    # Private attributes
    _entry: TocEntry = field(init=False, default=None)
    _section: Section = field(init=False, default=None)
    _clip: Audio = field(init=False, default=None)

    def __post_init__(self):
        if not isinstance(self.book, DaisyBook):
            raise BookNavigatorException("The supplied parameter is not valid.")

        self.toc = TocNavigator(self.book.toc_entries, self.book.navigation_depth)
        self.toc.add_callback(self.on_toc_navigation)
        self._entry = self.toc.first()

    @property
    def entry(self) -> TocEntry:
        return self._entry

    @property
    def section(self) -> Section:
        return self._section

    @property
    def clip(self) -> Audio:
        return self._clip

    def on_toc_navigation(self, toc_entry: TocEntry) -> None:
        self._entry = toc_entry
        self.sections = SectionNavigator(toc_entry.sections)
        self.sections.add_callback(self.on_section_navigation)
        self._section = self.sections.first()

    def on_section_navigation(self, section: Section) -> None:
        self._section = section
        self.clips = ClipNavigator(section._clips)
        self.clips.add_callback(self.on_clip_navigation)
        self._clip = self.clips.first()

    def on_clip_navigation(self, clip: Section) -> None:
        self._clip = clip
