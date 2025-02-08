from dataclasses import dataclass


@dataclass
class MetaData:
    """Representation of metadata."""

    name: str
    content: str
    scheme: str = ""
