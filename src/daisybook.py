import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from loguru import logger

from . import DomFactory, MetaData, NccEntry, Smil


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
        for element in DomFactory.create_document_from_string(data).get_elements_by_tag_name("meta").all():
            name = element.get_attr("name")
            if name:
                self.metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))

    def _process_headers(self, data: str):
        """Process and store the NCC entries (hx tags)."""
        body = DomFactory.create_document_from_string(data).get_elements_by_tag_name("body").first()
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
        self.title = document.get_elements_by_tag_name("title").first()

        # Project Metadata
        self._process_meta(data)

        # NCC entries (h1 .. h6)
        self._process_headers(data)

        # SMILS
        self._process_smils()

        # Source text
        self._process_text()

        logger.debug(f"Project {self.project_folder} load time : {(time.time() - self._start):.2f}s")
