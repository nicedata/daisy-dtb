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
class SmilReference:
    """This class represents a reference to a SMIL file."""

    resource: str
    fragment: str


@dataclass
class NccEntry:
    """Representation of an entry in the NCC file."""

    id: str
    level: int
    smil_reference: SmilReference
    text: str
    children: List["Smil"] = field(default_factory=list)


@dataclass
class NewSmil:
    """This class represents a SMIL file."""

    source: DtbResource
    reference: SmilReference
    title: str = ""
    total_duration: float = 0.0
    is_loaded: bool = False

    def __post_init__(self): ...

    def load(self) -> None:
        """Load a the SMIL file (if not already loaded)."""
        if self.is_loaded:
            return

        # Get the resource data
        data = self.source.get(self.reference.resource)
        if data is None:
            return

        # Prepare a document
        document = DomFactory.create_document_from_string(data)

        # Title
        elt = document.get_elements("meta", {"name": "dc:title"}).first()
        if elt:
            self.title = elt.get_attr("content")

        # Total duration
        elt = document.get_elements("meta", {"name": "ncc:timeInThisSmil"}).first()
        if elt:
            duration = elt.get_attr("content")
            h, m, s = duration.split(":")
            self.total_duration = float(h) * 3600 + float(m) * 60 + float(s)

        self.is_loaded = True
        print(self)


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
        for element in DomFactory.create_document_from_string(data).get_elements("meta").all():
            name = element.get_attr("name")
            if name:
                self.metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))

    def _populate_entries(self, data: str):
        """Process and store the NCC entries (hx tags)."""
        body = DomFactory.create_document_from_string(data).get_elements("body").first()
        for element in body.get_children().all():
            element_name = element.get_name()
            if element_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element_name[1])
                id = element.get_attr("id")
                a = element.get_children("a").first()
                smil_resource, smil_fragment = a.get_attr("href").split("#")
                smil_reference = SmilReference(smil_resource, smil_fragment)
                self.entries.append(NccEntry(id, level, smil_reference, a.get_text()))

    def _populate_smils(self):
        for entry in self.entries:
            smil = NewSmil(self.source, entry.smil_reference)
            self.smils.append(smil)

    def get_title(self) -> str:
        for meta in self.metadata:
            if meta.name == "dc:title":
                return meta.content


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    id: str
    text_file: str
    fragment: str
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
        elt = document.get_elements("meta", {"name": "title"}).first()
        if elt:
            self.title = elt.get_attr("content")

        # SMIL duration
        elt = document.get_elements("seq").first()
        if elt:
            self.duration = float(elt.get_attr("dur")[:-1])

        # Process all <par/> elements
        for elt in document.get_elements("par").all():
            smil_par = Par(elt.get_attr("id"))

            # Get the <text/> element
            text_elt = elt.get_children("text").first()
            text_file, fragment = text_elt.get_attr("src").split("#")
            smil_par.text = Text(text_elt.get_attr("id"), text_file, fragment)

            for seq_elt in elt.get_children("seq").all():
                for audio_elt in seq_elt.get_children("audio").all():
                    smil_par.clips.append(
                        Clip(
                            smil_par,
                            audio_elt.get_attr("id"),
                            audio_elt.get_attr("src"),
                            float(audio_elt.get_attr("clip-begin")[4:-1]),
                            float(audio_elt.get_attr("clip-end")[4:-1]),
                        )
                    )

            self.pars.append(smil_par)

        parent.children.append(self)
