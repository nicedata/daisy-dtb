"""Daisy library"""

from dataclasses import dataclass, field
from typing import List

from loguru import logger

from domlib import Document
from dtbsource import DtbResource


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


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    source: DtbResource
    id: str
    reference: Reference

    # Internal attributes
    _content: str = None

    # Internal attributes
    _is_loaded: bool = False

    def get(self) -> str:
        result = ""
        if self._content is not None:
            logger.debug(f"Content {self.reference.resource}/{self.reference.fragment} is already present.")
            return self._content
        logger.debug(f"Loading text from {self.reference.resource}, fragment id is {self.reference.fragment}.")

        data = self.source.get(self.reference.resource)
        if isinstance(data, Document) is False:
            logger.error(f"The retrieval attempt of {self.reference.resource} as Document failed.")
            return result

        element = data.get_element_by_id(self.reference.fragment)
        if element is not None:
            self._content = element.text
            self._is_loaded = True
            return self._content
        else:
            logger.error(f"Could not retrieve element {self.reference.fragment} in the {self.reference.resource} Document.")

        return result


@dataclass
class Audio:
    """
    Representation of a <audio/> section in as SMIL file.
    Defines an audio clip.
    """

    source: DtbResource
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
class Parallel:
    """
    Representation of a <par/> section in as SMIL file.
    Objects inside the <par> element will be played at the same time (in parallel).
    """

    source: DtbResource
    id: str
    text: Text
    clips: List[Audio] = field(default_factory=list)


@dataclass
class Smil:
    """This class represents a SMIL file."""

    source: DtbResource
    reference: Reference
    title: str = ""
    total_duration: float = 0.0

    # Internal attributes (dynamically populated)
    _pars: List[Parallel] = field(default_factory=list)
    _is_loaded: bool = False

    def __post_init__(self): ...

    @property
    def pars(self):
        if not self._is_loaded:
            self.load()
        return self._pars

    def get_full_text(self) -> str:
        result = []
        if self._is_loaded is False:
            self.load()
        for par in self._pars:
            result.append(par.text.get())

        return " \n".join(result)

    def load(self) -> None:
        """Load a the SMIL file (if not already loaded)."""
        if self._is_loaded:
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
            self.title = elt.get_attr("content")
            logger.debug(f"SMIL '{self.reference.resource}' title set : '{self.title}'.")

        # Total duration
        elt = data.get_elements_by_tag_name("meta", {"name": "ncc:timeInThisSmil"}).first()
        if elt:
            duration = elt.get_attr("content")
            h, m, s = duration.split(":")
            self.total_duration = float(h) * 3600 + float(m) * 60 + float(s)
            logger.debug(f"SMIL {self.reference.resource} duration set : {self.total_duration}s.")

        # Process sequences in body
        for body_seq in data.get_elements_by_tag_name("seq", having_parent_tag_name="body").all():
            # Process the <par/> element in the sequence
            for par in body_seq.get_children_by_tag_name("par").all():
                par_id = par.get_attr("id")

                # Handle the <text/>
                text = par.get_children_by_tag_name("text").first()
                id = text.get_attr("id")
                src, frag = text.get_attr("src").split("#")
                current_text = Text(self.source, id, Reference(src, frag))
                current_par = Parallel(self.source, par_id, current_text)

                # Handle the <audio/> clip
                for par_seq in par.get_children_by_tag_name("seq").all():
                    audios = par_seq.get_children_by_tag_name("audio").all()
                    for audio in audios:
                        id = audio.get_attr("id")
                        src = audio.get_attr("src")
                        begin = float(audio.get_attr("clip-begin")[4:-1])
                        end = float(audio.get_attr("clip-end")[4:-1])
                        current_par.clips.append(Audio(self.source, id, src, begin, end))
                    logger.debug(f"SMIL {self.reference.resource}, par: {current_par.id} contains {len(current_par.clips)} audio clip(s).")

                # Add to the list of Parallel
                self._pars.append(current_par)

        self._is_loaded = True
        logger.debug(f"SMIL {self.reference.resource} contains {len(self._pars)} pars.")
        logger.debug(f"SMIL {self.reference.resource} sucessfully loaded.")


@dataclass
class NccEntry:
    """Representation of an entry in the NCC file."""

    source: DtbResource
    id: str
    level: int
    smil_reference: Reference
    text: str
    _smil: Smil = None

    @property
    def smil(self) -> "Smil":
        """Get the attached smil. Load it if needed.

        Returns:
            NewSmil: The attached smil.
        """
        if self._smil is None:
            self._smil = Smil(self.source, self.smil_reference)
            logger.debug(f"Smil set from {self.smil_reference}")
        return self._smil


@dataclass
class Sequence:
    """
    Representation of a <seq/> section in as SMIL file.
    The children elements of the <seq> element are displayed in a sequence, one after each other.
    """


@dataclass
class DaisyDtb:
    """Representation of a Daisy 2.02 Digital Talking Book file."""

    source: DtbResource = field(default_factory=DtbResource)
    _metadata: List[MetaData] = field(init=False, default_factory=list)
    _entries: List[NccEntry] = field(init=False, default_factory=list)
    _smils: List[Smil] = field(init=False, default_factory=list)
    _is_valid: bool = field(init=False, default=False)

    def __post_init__(self):
        # Get the ncc.html file content
        ncc = self.source.get("ncc.html")

        # No data, no further processing !
        if ncc is None or not isinstance(ncc, Document):
            return

        # Populate the entries list
        self._populate_entries(ncc)

        # Populate the metadata list
        self._populate_metadata(ncc)

        # Populate the smils list
        self._populate_smils()

        self._is_valid = True

    def _populate_metadata(self, data: Document) -> None:
        """Process and store all metadata."""
        for element in data.get_elements_by_tag_name("meta").all():
            name = element.get_attr("name")
            if name:
                self._metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))

    def _populate_entries(self, data: Document):
        """Process and store the NCC entries (h1 ... h6 tags)."""
        body = data.get_elements_by_tag_name("body").first()
        for element in body.get_children_by_tag_name().all():
            element_name = element.name
            if element_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element_name[1])
                id = element.get_attr("id")
                a = element.get_children_by_tag_name("a").first()
                src, frag = a.get_attr("href").split("#")
                smil_reference = Reference(src, frag)
                self._entries.append(NccEntry(self.source, id, level, smil_reference, a.text))

    def _populate_smils(self):
        for entry in self._entries:
            smil = Smil(self.source, entry.smil_reference)
            self._smils.append(smil)

    def get_title(self) -> str:
        for meta in self._metadata:
            if meta.name == "dc:title":
                return meta.content
        return ""

    def get_depth(self) -> int:
        for meta in self._metadata:
            if meta.name == "ncc:depth":
                return int(meta.content)
        return 0
