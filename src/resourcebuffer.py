from dataclasses import dataclass, field
from typing import Set

RESOURCE_BUFFER_MAX_SIZE = 50


@dataclass
class ResourceBufferItem:
    name: str
    data: bytes | str = None

    def __hash__(self):
        return hash(self.name)


@dataclass
class ResourceBuffer:
    size: int
    items: Set[ResourceBufferItem] = field(default_factory=set)

    def __post_init__(self):
        if self.size > RESOURCE_BUFFER_MAX_SIZE:
            raise ValueError(f"The buffer size may not exceed {RESOURCE_BUFFER_MAX_SIZE}")

    def add(item: ResourceBufferItem) -> ResourceBufferItem: ...
