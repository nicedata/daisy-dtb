"""Daisy library"""

from dataclasses import InitVar, dataclass, field
from pathlib import Path
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
    children: List["Smil"] = field(default_factory=list)


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    id: str
    reference: Reference
    content: str = ""


@dataclass
class Clip:
    """Representation of an audio clip."""

    parent: "Par"
    id: str
    source_file: str
    begin: float
    end: float

    @property
    def duration(self):
        return self.end - self.begin


@dataclass
class Par:
    """Representation of a <par/> section in as SMIL file."""

    id: str
    text: Text = None
    clips: List[Clip] = field(default_factory=list)


@dataclass
class Parallel:
    """
    Representation of a <par/> section in as SMIL file.
    Objects inside the <par> element will be played at the same time (in parallel).
    """


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
class Smil:
    """Representation of a SMIL file."""

    smil_path: InitVar[Path]
    parent: InitVar[NccEntry]
    title: str = ""
    duration: float = 0.0
    pars: List[Par] = field(default_factory=list, init=False)

    def __post_init__(self, smil_path: Path, parent: NccEntry):
        logger.debug(f"Processing SMIL {smil_path}")
        try:
            with open(smil_path) as smil:
                data = smil.read()
                document = DomFactory.create_document_from_string(data)
        except FileNotFoundError:
            logger.critical(f"File not found : {smil_path}.")
            exit()

        # SMIL title
        elt = document.get_elements_by_tag_name("meta", {"name": "title"}).first()
        if elt:
            self.title = elt.get_attr("content")

        # SMIL duration
        elt = document.get_elements_by_tag_name("seq").first()
        if elt:
            self.duration = float(elt.get_attr("dur")[:-1])

        # Process all <par/> elements
        for elt in document.get_elements_by_tag_name("par").all():
            smil_par = Par(elt.get_attr("id"))

            # Get the <text/> element
            text_elt = elt.get_children("text").first()
            text_file, fragment = text_elt.get_attr("src").split("#")
            smil_par.text = Text(text_elt.get_attr("id"), text_file, fragment)

            for seq_elt in elt.get_children("seq").all():
                for audio_elt in seq_elt.get_children("audio").all():
                    smil_par.clips.append(Clip(smil_par, audio_elt.get_attr("id"), audio_elt.get_attr("src"), float(audio_elt.get_attr("clip-begin")[4:-1]), float(audio_elt.get_attr("clip-end")[4:-1])))

            self.pars.append(smil_par)

        parent.children.append(self)


@dataclass
class NewSmil:
    """This class represents a SMIL file."""

    source: DtbResource
    reference: Reference
    title: str = ""
    total_duration: float = 0.0
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
        for body_seq in document.get_elements_by_tag_name("seq", parent_tag_name="body").all():
            # Process the <par/> element in the sequence
            for par in body_seq.get_children("par").all():
                # TODO: Handle the <text/>
                text = par.get_children("text").first()
                id = text.get_attr("id")
                src, frag = text.get_attr("src").split("#")
                t = Text(id, Reference(src, frag), text.get_value())
                print(t)

                # TODO: Handle the <audio/>
                for par_seq in par.get_children("seq").all():
                    audios = par_seq.get_children("audio").all()
                    for audio in audios:
                        id = audio.get_attr("id")
                        source = audio.get_attr("src")
                        begin = float(audio.get_attr("clip-begin")[4:-1])
                        end = float(audio.get_attr("clip-end")[4:-1])
                        au = Audio(id, source, begin, end)
                        print(au)

                # print(text)
                # print(audios)

        self.is_loaded = True
        logger.debug(f"SMIL {self.reference.resource} sucessfully loaded.")


@dataclass
class Dtb:
    """Representation of an NCC file"""

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

        # Populate the metadata list
        self._populate_metadata(data)

        # Populate the entries list
        self._populate_entries(data)

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
                smil_resource, smil_fragment = a.get_attr("href").split("#")
                smil_reference = Reference(smil_resource, smil_fragment)
                self.entries.append(NccEntry(id, level, smil_reference, a.get_text()))

    def _populate_smils(self):
        for entry in self.entries:
            smil = NewSmil(self.source, entry.smil_reference)
            self.smils.append(smil)

    def get_title(self) -> str:
        for meta in self.metadata:
            if meta.name == "dc:title":
                return meta.content
