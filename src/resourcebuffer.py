from dataclasses import dataclass, field
from typing import List

from loguru import logger


@dataclass(frozen=True)
class ResourceBufferItem:
    name: str
    data: bytes | str = None

    @property
    def type(self):
        return type(self.data)


@dataclass
class ResourceBuffer:
    size: int
    items: List[ResourceBufferItem] = field(default_factory=list)

    def add(self, item: ResourceBufferItem) -> None:
        # Check if item exists
        if item.name in [v.name for v in self.items]:
            logger.debug(f"Item {item.name} is alerady in the buffer")
            return

        # In case of buffer size limit reached, remove the oldest item
        if len(self.items) + 1 > self.size:
            logger.debug(f"Removing item {self.items[0].name}")
            del self.items[0]

        logger.debug(f"Adding item {item.name} to the buffer")
        self.items.append(item)

    def get(self, resource_name: str) -> ResourceBufferItem | None:
        try:
            index = [v.name for v in self.items].index(resource_name)
            logger.debug(f"Index of item {resource_name} is {index}")
        except ValueError:
            logger.debug(f"Item {resource_name} not found in buffer")
            return None

        logger.debug(f"Item {resource_name} found in the buffer")
        return self.items[index]
