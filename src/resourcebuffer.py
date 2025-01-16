from dataclasses import dataclass, field
from typing import List

from loguru import logger


@dataclass(frozen=True)
class ResourceBufferItem:
    """This class represents a buffered resource."""

    name: str
    data: bytes | str = None


@dataclass
class ResourceBuffer:
    """Representation of resource buffer"""

    # Internal attributes
    _size: int = 0
    _items: List[ResourceBufferItem] = field(default_factory=list)

    def set_size(self, size: int) -> None:
        """Set the buffer size.

        Args:
            size (int): requested size. Must be greter or equal to 0.
        """
        self._size = size if size >= 0 else self._size

    def get_size(self) -> int:
        """Get the buffer size.

        Returns:
            int: the actual buffer size.
        """
        return self._size

    def add(self, item: ResourceBufferItem) -> None:
        """Add a `ResourceBufferItem` to the buffer.

        This method takes care of the buffer size:
            - If it is 0, nothing is done.
            - If the addition would overfill the buffer, the oldest item is removed before adding the new one.

        Args:
            item (ResourceBufferItem): the item to add.
        """

        # No buffer, no buffering
        if self._size == 0:
            logger.debug(f"Item {item.name} will not be added. The buffer size is 0.")
            return

        # Check if item exists
        if item.name in [_.name for _ in self._items]:
            logger.debug(f"Item {item.name} is alerady in the buffer.")
            return

        # In case of buffer size limit reached, remove the oldest item
        if len(self._items) + 1 > self._size:
            logger.debug(f"Removing item {self._items[0].name}")
            del self._items[0]

        # Append the item
        logger.debug(f"Adding item {item.name} to the buffer.")
        self._items.append(item)

    def get(self, resource_name: str) -> ResourceBufferItem | None:
        """Get a `ResourceBufferItem` from the buffer.

        Args:
            resource_name (str): the requested resource

        Returns:
            ResourceBufferItem | None: the found `ResourceBufferItem` or None
        """
        try:
            index = [_.name for _ in self._items].index(resource_name)
            logger.debug(f"Index of item {resource_name} is {index}.")
        except ValueError:
            logger.debug(f"Item {resource_name} not found in buffer.")
            return None

        logger.debug(f"Item {resource_name} found in the buffer.")
        return self._items[index]
