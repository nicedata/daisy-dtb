"""Project classes"""

from dataclasses import dataclass, field
from typing import List, Union

from loguru import logger

from domlib import Document
from dtbsource import DtbSource


@dataclass
class MetaData:
    """Representation of metadata."""

    name: str
    content: str
    scheme: str = ""


@dataclass
class Reference:
    """This class represents a reference to a fragment in a file."""

    resource: str
    fragment: str

    @staticmethod
    def create_href_or_src(string: str) -> Union["Reference", None]:
        """Create a Reference from a string.

        Example:
        - "dijn0159.smil#mxhp_0001" will return Reference(resource="dijn0159.smil", fragment="mxhp_0001").


        Returns:
            Union["Reference", None]: the Reference.
        """
        if "#" not in string:
            return None
        source, fragment = string.split("#")
        return Reference(source, fragment)


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    source: DtbSource
    id: str
    reference: Reference

    # Internal attributes
    _content: str = field(init=False, default=None)

    @property
    def content(self) -> str:
        if self._content is None:
            self._parse()
        return self._content

    def _parse(self) -> None:
        """Get the text from a resource.

        Notes:
        - If the text has already been retrieved, return the instances text content.


        Returns:
            str: the text.
        """
        # Check if text already here
        if self._content is not None:
            logger.debug(f"Content {self.reference.resource}/{self.reference.fragment} is already present.")
            return self._content

        # Get it from the source
        logger.debug(f"Loading text from {self.reference.resource}, fragment id is {self.reference.fragment}.")
        data = self.source.get(self.reference.resource)

        # The fetched data must be a Document
        if isinstance(data, Document) is False:
            logger.error(f"The retrieval attempt of {self.reference.resource} as Document failed.")
            self._content = ""
            return

        # Find the text identified by its id
        element = data.get_element_by_id(self.reference.fragment)
        if element is not None:
            self._content = element.text
            logger.debug(f"Text with id {self.reference.fragment} found in {self.reference.resource}.")
            return
        else:
            logger.error(f"Could not retrieve element {self.reference.fragment} in the {self.reference.resource} Document.")

        self._content = ""


@dataclass
class Audio:
    """
    Representation of a <audio/> section in a SMIL file.
    - Defines an audio clip.
    """

    source: DtbSource
    id: str
    src: str
    begin: float
    end: float

    @property
    def duration(self) -> float:
        """Get the duration of a clip, in seconds."""
        return self.end - self.begin

    @property
    def data(self) -> bytes:
        return self.source.get(self.src)


@dataclass
class Section:
    """
    Representation of a <par/> section in as SMIL file.
    Objects inside the <par> element will be played at the same time (in parallel).
    """

    source: DtbSource
    id: str
    text: Text

    # Private attributes
    _clips: List[Audio] = field(init=False, default_factory=list)
    # _clip_nav: ClipNavigator = field(init=False, default=None)

    # @property
    # def clips(self) -> ClipNavigator:
    #     if self._clip_nav is None:
    #         self._clip_nav = ClipNavigator(self._clips)
    #     return self._clip_nav


@dataclass
class Clip:
    text: str
    audio: Audio


@dataclass
class Smil:
    """This class represents a SMIL file."""

    source: DtbSource
    reference: Reference

    # Internal attributes (dynamically populated)
    _title: str = field(init=False, default="")
    _total_duration: float = field(init=False, default=0.0)
    _is_parsed: bool = field(init=False, default=False)
    _sections: List[Section] = field(init=False, default_factory=list)

    def __post_init__(self): ...

    @property
    def title(self) -> str:
        if not self._is_parsed:
            self._parse()
        return self._title

    @property
    def total_duration(self) -> str:
        if not self._is_parsed:
            self._parse()
        return self._total_duration

    @property
    def sections(self) -> List[Section]:
        if not self._is_parsed:
            self._parse()
        return self._sections

    def get_full_text(self) -> str:
        result = []
        if self._is_parsed is False:
            self._parse()
        for par in self._sections:
            result.append(par.text._parse())

        return "\n".join(result)

    def _parse(self) -> None:
        """Load a the SMIL file (if not already loaded) and parse it."""
        if self._is_parsed:
            logger.debug(f"SMIL '{self.reference.resource}' is already loaded.")
            return

        # Get the resource data
        data = self.source.get(self.reference.resource)

        if data is None:
            logger.debug(f"Could not get SMIL '{self.reference.resource}'.")
            return

        if not isinstance(data, Document):
            logger.debug(f"No Document to process ({self.reference.resource}).")
            return

        # Title
        elt = data.get_elements_by_tag_name("meta", {"name": "dc:title"}).first()
        if elt:
            self._title = elt.get_attr("content")
            logger.debug(f"SMIL '{self.reference.resource}' title set : '{self._title}'.")

        # Total duration
        elt = data.get_elements_by_tag_name("meta", {"name": "ncc:timeInThisSmil"}).first()
        if elt:
            duration = elt.get_attr("content")
            h, m, s = duration.split(":")
            self._total_duration = float(h) * 3600 + float(m) * 60 + float(s)
            logger.debug(f"SMIL {self.reference.resource} duration set : {self._total_duration}s.")

        # Process sequences in body
        for body_seq in data.get_elements_by_tag_name("seq", having_parent_tag_name="body").all():
            # Process the <par/> element in the sequence
            for par in body_seq.get_children_by_tag_name("par").all():
                par_id = par.get_attr("id")

                # Handle the <text/>
                text = par.get_children_by_tag_name("text").first()
                id = text.get_attr("id")
                reference = Reference.create_href_or_src(text.get_attr("src"))
                current_text = Text(self.source, id, reference)
                current_par = Section(self.source, par_id, current_text)

                # Handle the <audio/> clip
                for par_seq in par.get_children_by_tag_name("seq").all():
                    for audio in par_seq.get_children_by_tag_name("audio").all():
                        id = audio.get_attr("id")
                        src = audio.get_attr("src")
                        begin = float(audio.get_attr("clip-begin")[4:-1])
                        end = float(audio.get_attr("clip-end")[4:-1])
                        current_par._clips.append(Audio(self.source, id, src, begin, end))
                    logger.debug(f"SMIL {self.reference.resource}, par: {current_par.id} contains {len(current_par._clips)} clip(s).")

                # Add to the list of Parallel
                self._sections.append(current_par)

        self._is_parsed = True
        logger.debug(f"SMIL {self.reference.resource} contains {len(self._sections)} pars.")
        logger.debug(f"SMIL {self.reference.resource} sucessfully loaded.")


@dataclass
class TocEntry:
    """Representation of an entry in the NCC file."""

    source: DtbSource
    id: str
    level: int
    smil_reference: Reference
    text: str

    # Internal attributes
    _smil: Smil = field(init=False, default=None)

    def __post_init__(self):
        # Build the SMIL from its reference
        self._smil = Smil(self.source, self.smil_reference)
        logger.debug(f"Smil set from {self.smil_reference}")

    # @property
    # def sections(self) -> SectionNavigator:
    #     self._smil._section_nav

    @property
    def smil(self) -> "Smil":
        """Get the attached SMIL.

        Returns:
            Smil: the SMIL.
        """
        return self._smil

    @property
    def sections(self) -> List[Section]:
        return self._smil.sections
