"""Resource cacheing classes"""

from dataclasses import InitVar, dataclass, field
from typing import Any, List, Union

from loguru import logger

from domlib import DomFactory


@dataclass
class CacheItem:
    """This class represents a cached resource.

    This class tries to be smart:
    - If the input bytes can be converted to a string, they will
    - It a string conversion happened, a conversion to a `Document` will be tried

    This is done this way since the project mainly deals with XML/HTML documents and binary audio files.
    """

    name: InitVar[str] = None
    data: InitVar[Any] = None

    # Internal attributes
    __name: str = field(init=False, default=None)
    __data: str = field(init=False, default=None)

    def __post_init__(self, name, data):
        """
        Class post initilization :
        - try to cenvert the data to a `str`
        - try to convert the string to a `Document`
        """
        self.__name = name

        self.__data = self._convert_data(data)
        if isinstance(self.__data, str):
            document = DomFactory.create_document_from_string(self.__data)
            if document is not None:
                self.__data = document
                logger.debug(f"A document has been created from '{self.__name}'.")
        logger.debug(f"The cache item '{self.__name}' has been created. Its type is {self.get_type()}.")

    def get_type(self) -> type:
        return type(self.__data)

    def get_name(self) -> str:
        return self.__name

    def get_data(self) -> str:
        return self.__data

    @staticmethod
    def _convert_data(data: bytes) -> Union[bytes, str]:
        """Convert `bytes` to a `str` or if possible.

        Args:
            data (bytes): the input bytes.

        Returns:
            bytes | str | the decoded bytes (str) or the original data.
        """
        if not isinstance(data, bytes):
            return data

        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data


@dataclass(kw_only=True)
class Cache:
    """Representation of resource cache"""

    max_size: InitVar[int] = 0
    auto_expand: InitVar[bool] = False

    # Internal attributes
    __max_size: int = field(init=False, default=0)
    __auto_expand: bool = field(init=False, default=False)
    __items: List[CacheItem] = field(init=False, default_factory=list)
    __queries: int = field(init=False, default=0)
    __hits: int = field(init=False, default=0)

    def __post_init__(self, max_size: int, auto_expand: bool) -> None:
        """Cache post initialize.

        Args:
            max_size (int): the maximum cache items number.
            auto_expand (bool): auto expand the size if Tue.
        """
        self.__auto_expand = auto_expand

        if max_size < 0:
            logger.warning(f"The cache size must be positive. You supplied {max_size}. Cache size set to 0.")
            self.__max_size = 0
        else:
            self.__max_size = max_size

    @property
    def queries(self) -> int:
        return self.__queries

    @property
    def hits(self) -> int:
        return self.__hits

    @property
    def efficiency(self) -> float:
        return self.__hits / self.__queries if self.__queries > 0 else 0.0

    def get_current_size(self) -> int:
        """Get the current cache size.

        Returns:
            int: the actual cache size.
        """
        return len(self.__items)

    def get_max_size(self) -> int:
        """Get the max. cache size.

        Returns:
            int: the actual cache size.
        """
        return self.__max_size

    def set_max_size(self, size: int) -> None:
        """Set the cache size.

        Args:
            size (int): requested size. Must be greter or equal to 0.
        """
        if self.__auto_expand is False:
            self.__max_size = size if size >= 0 else self.__max_size

    def add(self, item: CacheItem, force: bool = False) -> None:
        """Add a `CacheItem` into the cache.

        This method takes care of the cache size:
            - If it is 0, nothing is done.
            - If the addition would overfill the cache, the oldest item is removed before adding the new one.

        Args:
            item (CacheItem): the item to add.
            force (bool): force a replacement. Defaults to False.
        """

        # No cache, no cacheing
        item_name = item.get_name()
        if self.__auto_expand is False and self.__max_size == 0:
            logger.debug(f"Item '{item_name}' will not be added. The cache size is 0.Auto expand feature is off.")
            return

        # Check if item exists
        if item.get_name() in [_.get_name() for _ in self.__items]:
            if force is False:
                logger.debug(f"Item '{item_name}' is alerady in the cache. Force feature is off.")
                return
            else:
                logger.debug(f"Item '{item_name}' is alerady in the cache. It will be replaced. Force feature is on.")

        # In case of cache size limit reached, remove the oldest item
        if self.__auto_expand is False:
            if len(self.__items) + 1 > self.__max_size:
                logger.debug(f"Removing item '{self.__items[0].get_name()}' from the cache. Auto expand feature is off.")
                del self.__items[0]

        # Append the item
        logger.debug(f"Adding item '{item_name}' to the cache.")
        self.__items.append(item)
        logger.debug(f"The cache now holds {self.get_current_size()} items.")

    def get(self, resource_name: str) -> CacheItem | None:
        """Get a `CacheItem` from the cache.

        Args:
            resource_name (str): the requested resource

        Returns:
            CacheItem | None: the found `CacheItem` or None
        """
        self.__queries += 1
        try:
            index = [_.get_name() for _ in self.__items].index(resource_name)
            self.__hits += 1
            logger.debug(f"Index of item '{resource_name}' is {index}.")
        except ValueError:
            logger.debug(f"Item '{resource_name}' not found in the cache.")
            return None

        logger.debug(f"Item '{resource_name}' found in the cache.")
        return self.__items[index]
