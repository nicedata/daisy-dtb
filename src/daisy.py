"""Daisy library"""

from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import List

from loguru import logger

from domlib import DomFactory


@dataclass
class MetaData:
    """Representation of metadata."""

    name: str
    content: str
    scheme: str = ""


@dataclass
class NccEntry:
    """Representation of an entry in the NCC file."""

    id: str
    level: int
    smil_file: str
    fragment: str
    text: str
    children: List["Smil"] = field(default_factory=list)


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
