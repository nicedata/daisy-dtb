"""Daisy library"""

from dataclasses import dataclass, field
from typing import List

from loguru import logger

from domlib import DomFactory
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
class NccEntry:
    """Representation of an entry in the NCC file."""

    id: str
    level: int
    smil_reference: Reference
    text: str
    children: List["NewSmil"] = field(default_factory=list)


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    id: str
    reference: Reference
    content: str = ""


@dataclass
class Sequence:
    """
    Representation of a <seq/> section in as SMIL file.
    The children elements of the <seq> element are displayed in a sequence, one after each other.
    """


@dataclass
class Audio:
    """
    Representation of a <audio/> section in as SMIL file.
    Defines an audio clip.
    """

    id: str
    source: str
    begin: float
    end: float

    def get_duration(self) -> float:
        """Get the duration of a clip, in seconds."""
        return self.end - self.begin


@dataclass
class Parallel:
    """
    Representation of a <par/> section in as SMIL file.
    Objects inside the <par> element will be played at the same time (in parallel).
    """

    id: str
    text: Text
    clips: List[Audio] = field(default_factory=list)


@dataclass
class NewSmil:
    """This class represents a SMIL file."""

    source: DtbResource
    reference: Reference
    title: str = ""
    total_duration: float = 0.0
    pars: List[Parallel] = field(default_factory=list)

    is_loaded: bool = False

    def __post_init__(self): ...

    def load(self) -> None:
        """Load a the SMIL file (if not already loaded)."""
        if self.is_loaded:
            logger.debug(f"SMIL {self.reference.resource} is already loaded.")
            return

        # Get the resource data
        data = self.source.get(self.reference.resource)
        if data is None:
            logger.debug(f"Could not get SMIL {self.reference.resource}.")
            return

        # Prepare a document
        document = DomFactory.create_document_from_string(data)
        if document is None:
            logger.debug(f"Could not create a document from {self.reference.resource}.")
            return

        # Title
        elt = document.get_elements_by_tag_name("meta", {"name": "dc:title"}).first()
        if elt:
            self.title = elt.get_attr("content")
            logger.debug(f"SMIL {self.reference.resource} title set : {self.title}s.")

        # Total duration
        elt = document.get_elements_by_tag_name("meta", {"name": "ncc:timeInThisSmil"}).first()
        if elt:
            duration = elt.get_attr("content")
            h, m, s = duration.split(":")
            self.total_duration = float(h) * 3600 + float(m) * 60 + float(s)
            logger.debug(f"SMIL {self.reference.resource} duration set : {self.total_duration}s.")

        # Process sequences in body
        for body_seq in document.get_elements_by_tag_name("seq", having_parent_tag_name="body").all():
            # Process the <par/> element in the sequence
            for par in body_seq.get_children("par").all():
                par_id = par.get_attr("id")

                # Handle the <text/>
                text = par.get_children("text").first()
                id = text.get_attr("id")
                src, frag = text.get_attr("src").split("#")
                current_text = Text(id, Reference(src, frag), text.get_value())
                current_par = Parallel(par_id, current_text)

                # Handle the <audio/> clip
                for par_seq in par.get_children("seq").all():
                    audios = par_seq.get_children("audio").all()
                    for audio in audios:
                        id = audio.get_attr("id")
                        source = audio.get_attr("src")
                        begin = float(audio.get_attr("clip-begin")[4:-1])
                        end = float(audio.get_attr("clip-end")[4:-1])
                        current_par.clips.append(Audio(id, source, begin, end))
                    logger.debug(f"SMIL {self.reference.resource}, par: {current_par.id} contains {len(current_par.clips)} audio clip(s).")

                # Add to the list of Parallel
                self.pars.append(current_par)

        self.is_loaded = True
        logger.debug(f"SMIL {self.reference.resource} contains {len(self.pars)} pars.")
        logger.debug(f"SMIL {self.reference.resource} sucessfully loaded.")


@dataclass
class DaisyDtb:
    """Representation of a Daisy 2.03 Digital Talking Book file"""

    source: DtbResource
    metadata: List[MetaData] = field(default_factory=list)
    entries: List[NccEntry] = field(default_factory=list)
    smils: List[NewSmil] = field(default_factory=list)
    is_valid: bool = False

    def __post_init__(self):
        # Get the ncc.html file content
        data = self.source.get("ncc.html")

        # No data, no further processing !
        if data is None:
            return

        # Populate the entries list
        self._populate_entries(data)

        # Populate the metadata list
        self._populate_metadata(data)

        # Populate the smils list
        self._populate_smils()

        self.is_valid = True

    def _populate_metadata(self, data: str) -> None:
        """Process and store all metadata."""
        for element in DomFactory.create_document_from_string(data).get_elements_by_tag_name("meta").all():
            name = element.get_attr("name")
            if name:
                self.metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))

    def _populate_entries(self, data: str):
        """Process and store the NCC entries (hx tags)."""
        body = DomFactory.create_document_from_string(data).get_elements_by_tag_name("body").first()
        for element in body.get_children().all():
            element_name = element.get_name()
            if element_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element_name[1])
                id = element.get_attr("id")
                a = element.get_children("a").first()
                src, frag = a.get_attr("href").split("#")
                smil_reference = Reference(src, frag)
                self.entries.append(NccEntry(id, level, smil_reference, a.get_text()))

    def _populate_smils(self):
        for entry in self.entries:
            smil = NewSmil(self.source, entry.smil_reference)
            self.smils.append(smil)

    def get_title(self) -> str:
        for meta in self.metadata:
            if meta.name == "dc:title":
                return meta.content
        return ""

    def get_depth(self) -> int:
        for meta in self.metadata:
            if meta.name == "ncc:depth":
                return int(meta.content)
        return 0
