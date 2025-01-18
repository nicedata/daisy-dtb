from dataclasses import dataclass, field
from typing import Any, List, Union

from loguru import logger

from domlib import Document, DomFactory


@dataclass
class ResourceBufferItem:
    """This class represents a buffered resource."""

    name: str
    data: Union[bytes, str, Document] = None
    data_type: str = None

    @staticmethod
    def _convert_data(data: bytes) -> Union[bytes, str]:
        """Convert `bytes` to a `str` or if possible.

        Args:
            data (bytes): the input bytes.

        Returns:
            bytes | str | Document: the returned str (or original data).
        """
        if not isinstance(data, bytes):
            return data

        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data

    def __post_init__(self):
        data = self._convert_data(self.data)
        if isinstance(data, str):
            document = DomFactory.create_document_from_string(self.data)
            if document is not None:
                self.data = document
                logger.debug(f"A document has been created from {self.name}.")
        self.data_type = type(self.data)
        logger.debug(f"Data type is {self.data_type}")


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
        """Add a `ResourceBufferItem` into the buffer.

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
        logger.debug(f"Adding item {item.name} into the buffer.")
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
