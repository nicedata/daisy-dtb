from dataclasses import dataclass, field
from typing import List

from loguru import logger

from .reference import Reference
from .section import Section
from .smil import Smil
from ..sources.source import DtbSource


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
