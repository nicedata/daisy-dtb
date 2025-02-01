"""Daisy library"""

from dataclasses import dataclass, field
from typing import List

from loguru import logger

from domlib import Document
from dtb import MetaData, Reference, Smil, TocEntry
from dtbsource import DtbSource
from navigators.toc_navigator import TocNavigator


class DaisyBookError(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass
class DaisyBook:
    """Representation of a Daisy 2.02 Digital Talking Book file."""

    source: DtbSource

    # Internal attributes
    _title: str = field(init=False, default="")
    _navigation_depth: int = field(init=False, default=0)
    _metadata: List[MetaData] = field(init=False, default_factory=list)
    _toc_entries: List[TocEntry] = field(init=False, default_factory=list)
    _toc_navigator: TocNavigator = field(init=False, default=None)
    _smils: List[Smil] = field(init=False, default_factory=list)

    def __post_init__(self):
        # Get the ncc.html file content
        ncc_document = self.source.get("ncc.html")

        # No data, no further processing !
        if ncc_document is None or not isinstance(ncc_document, Document):
            message = f"Could not process {self.source.base_path}."
            logger.critical(message)
            raise DaisyBookError(f"Could not process {message}.")

        # Populate the entries list
        self._populate_entries(ncc_document)

        # Populate the metadata list
        self._populate_metadata(ncc_document)

        # Populate the smils list
        for entry in self._toc_entries:
            self._smils.append(entry.smil)

        # Set the title and navigation depth from the metadata
        for meta in self._metadata:
            match meta.name:
                case "dc:title":
                    self._title = meta.content
                case "ncc:depth":
                    self._navigation_depth = int(meta.content)

        # Add a TOC navigator
        self._toc_navigator = TocNavigator(self._toc_entries, self.navigation_depth)

    @property
    def cache_stats(self) -> dict:
        return self.source._cache.get_stats()

    @property
    def toc(self) -> TocNavigator:
        return self._toc_navigator

    @property
    def title(self) -> str:
        return self._title

    @property
    def navigation_depth(self) -> int:
        return self._navigation_depth

    @property
    def metadata(self) -> int:
        return self._metadata

    @property
    def smils(self) -> int:
        return self.smils

    @property
    def toc_entries(self) -> int:
        return self._toc_entries

    def _populate_entries(self, ncc_document: Document):
        """Process and store the NCC entries (h1 ... h6 tags)."""
        body = ncc_document.get_elements_by_tag_name("body").first()
        for element in body.get_children_by_tag_name().all():
            element_name = element.name
            if element_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element_name[1])
                id = element.get_attr("id")
                a = element.get_children_by_tag_name("a").first()
                smil_reference = Reference.create_href_or_src(a.get_attr("href"))
                self._toc_entries.append(TocEntry(self.source, id, level, smil_reference, a.text))
        logger.debug(f"Size of toc_entries : {len(self._toc_entries)}.")

    def _populate_metadata(self, ncc_document: Document) -> None:
        """Process and store all metadata."""
        for element in ncc_document.get_elements_by_tag_name("meta").all():
            name = element.get_attr("name")
            if name is not None:
                self._metadata.append(MetaData(name, element.get_attr("content"), element.get_attr("scheme")))
        logger.debug(f"Size of metadata : {len(self._metadata)}.")
