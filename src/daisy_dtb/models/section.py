from dataclasses import dataclass, field
from typing import List

from .audio import Audio
from .text import Text
from ..sources.source import DtbSource


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

    @property
    def clips(self) -> List[Audio]:
        return self._clips
