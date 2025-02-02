from dataclasses import dataclass

from sources.source import DtbSource


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

    @property
    def sound(self) -> bytes:
        """Get the actual sound data (.wav, .mp3, ...)"""
        return self.source.get(self.src)
