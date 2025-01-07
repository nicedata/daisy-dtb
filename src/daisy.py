"""Daisy library"""

import time
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


@dataclass
class DaisyBook:
    """Representation of a full Daisy 2.02 project."""

    project_folder: Path
    title: str = ""
    metadata: List[MetaData] = field(default_factory=list)
    entries: List[NccEntry] = field(default_factory=list)
    smils: List[Smil] = field(default_factory=list)
    _start = time.time()

    def _process_meta(self, data: str) -> None:
        """Process and store all metadata."""
        for element in DomFactory.create_document_from_string(data).get_elements("meta").all():
            name = element.get_attr("name")
            if name:
                self.metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))

    def _process_headers(self, data: str):
        """Process and store the NCC entries (hx tags)."""
        body = DomFactory.create_document_from_string(data).get_elements("body").first()
        for el in body.get_children().all():
            if el.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(el.name[1])
                id = el.get_attr("id")
                a = el.get_children("a").first()
                smil_file, fragment = a.get_attr("href").split("#")
                text = a.get_text()
                self.entries.append(NccEntry(id, level, smil_file, fragment, text))

    def _process_smils(self):
        for entry in self.entries:
            smil_path = Path(f"{self.project_folder}/{entry.smil_file}")
            smil = Smil(smil_path, entry)
            self.smils.append(smil)

    def _process_text(self):
        curr_path: Path = None

        for smil in self.smils:
            for par in smil.pars:
                source_path = Path(f"{self.project_folder}/{par.text.text_file}")

                if curr_path != source_path:
                    curr_path = source_path
                    with open(curr_path, "rt") as source:
                        data = source.read()
                        document = DomFactory.create_document_from_string(data)
                elt = document.get_element_by_id(par.text.fragment)
                if elt:
                    par.text.content = elt.get_text()

    def __post_init__(self):
        ncc_file = Path(f"{self.project_folder}/ncc.html")
        logger.debug(f"Processing NCC {ncc_file}")

        try:
            with open(ncc_file) as ncc:
                data = ncc.read()
        except FileNotFoundError:
            logger.critical(f"File not found : {ncc_file}.")
            exit()

        document = DomFactory.create_document_from_string(data)

        # Project title
        self.title = document.get_elements("title").first()

        # Project Metadata
        self._process_meta(data)

        # NCC entries (h1 .. h6)
        self._process_headers(data)

        # SMILS
        self._process_smils()

        # Source text
        self._process_text()

        logger.debug(f"Project {self.project_folder} load time : {(time.time() - self._start):.2f}s")
