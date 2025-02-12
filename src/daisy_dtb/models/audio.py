from dataclasses import dataclass
from io import BytesIO

from ..sources.source import DtbSource


@dataclass
class Audio:
    """
    Representation of a <audio/> section in a SMIL file.
    - Defines an audio clip.
    """

    source: DtbSource
    id: str
    src: str
    begin: float
    end: float

    @property
    def duration(self) -> float:
        """Get the duration of a clip, in seconds."""
        return self.end - self.begin

    def get_sound(self, as_bytes_io: bool = False) -> bytes:
        """Get the actual sound data (.wav, .mp3, ...)"""
        return BytesIO(self.source.get(self.src)) if as_bytes_io is True else self.source.get(self.src)
