"""Resource cacheing classes"""

from collections import deque
from dataclasses import InitVar, dataclass, field
from typing import Any, Union

from loguru import logger

from cachestats import CacheStats
from domlib import DomFactory


@dataclass
class _CacheItem:
    """This class represents a cached resource.

    It is intended for internal use.

    This class tries to be smart:
    - If the input bytes can be converted to a string, they will
    - It a string conversion happened, a conversion to a `Document` will be tried

    This is done this way since the project mainly deals with XML/HTML documents and binary audio files.
    """

    resource_name: InitVar[str] = None
    resource_data: InitVar[Any] = None

    # Internal attributes
    __name: str = field(init=False, default=None)
    __data: str = field(init=False, default=None)

    def __post_init__(self, resource_name, resource_data):
        """
        Class post initilization :
        - try to convert the data to a `str`
        - try to convert the string to a `Document`
        """
        self.__name = resource_name

        self.__data = self._convert_data(resource_data)
        if isinstance(self.__data, str):
            document = DomFactory.create_document_from_string(self.__data)
            self.__data = document if document is not None else self.__data
        logger.debug(f"The cache item '{self.__name}' has been created. Its type is {self.type}.")

    @property
    def type(self) -> type:
        return type(self.__data)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def data(self) -> str:
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


# @dataclass
@dataclass(kw_only=True)
class Cache:
    """Representation of resource cache"""

    max_size: InitVar[int] = 0
    with_stats: InitVar[bool] = False

    # Internal attributes
    __items: deque[_CacheItem] = field(init=False, default_factory=deque)
    __with_stats: bool = field(init=False, default=False)
    __stats: CacheStats = field(init=False, default_factory=CacheStats)

    def __post_init__(self, max_size: int, with_stats: bool) -> None:
        """Cache post initialize.

        Args:
            max_size (int): the maximum cache items number.
        """

        if max_size < 0:
            logger.warning(f"The cache size must be positive. {max_size} was supplied: cache size set to 0.")
            max_size = 0

        self.__items = deque(maxlen=max_size)
        self.__with_stats = with_stats
        logger.debug(f"Cache created. Size: {max_size}. Statistic collections is {'active' if self.__with_stats else 'inactive'}.")

    def get_stats(self) -> dict:
        return self.__stats.get_stats()

    def activate_stats_collection(self, value: bool) -> None:
        self.__with_stats = value

    def get_max_size(self) -> int:
        """Get the max. cache size.

        Returns:
            int: the actual cache size.
        """
        return self.__items.maxlen

    def resize(self, new_size: int) -> None:
        """Resize the cache.

        Args:
            new_size (int): the new size
        """
        # Checks
        if not isinstance(new_size, int) or new_size < 0:
            return

        # Size check
        if new_size == self.__items.maxlen:
            return

        # Cache migration
        new_cache = deque(maxlen=new_size)
        self.__items.reverse()
        if new_cache.maxlen > 0:
            for index, item in enumerate(self.__items):
                if index > new_cache.maxlen - 1:
                    break
                new_cache.appendleft(item)

        self.__items = new_cache

    def add(self, item: _CacheItem) -> None:
        """Add a `CacheItem` into the cache.

        This method takes care of the cache size:
            - If it is 0, nothing is done unless auto_expand is true.
            - If the addition would overfill the cache, the oldest item is removed before adding the new one.

        Args:
            item (CacheItem): the item to add.
        """
        # Checks
        if self.__items.maxlen == 0 or not isinstance(item, _CacheItem):
            return

        # Check if item exists
        try:
            item_index = [_.name for _ in self.__items].index(item.name)
            self.__items[item_index] = item
            logger.debug(f"Item '{item.name}' in the cache (index={item_index}) has been updated.")
            return
        except ValueError:
            # Append the item
            self.__items.append(item)
            logger.debug(f"Item '{item.name}' added into the cache.")

    def get(self, resource_name: str) -> _CacheItem | None:
        """Get a `CacheItem` from the cache.

        Args:
            resource_name (str): the requested resource

        Returns:
            CacheItem | None: the found `CacheItem` or None
        """

        try:
            item_index = [_.name for _ in self.__items].index(resource_name)
            logger.debug(f"Item '{resource_name}' found in the cache (index={item_index}).")
            if self.__with_stats:
                self.__stats.hit(resource_name)
            return self.__items[item_index]
        except ValueError:
            logger.debug(f"Item '{resource_name}' not found in the cache.")
            if self.__with_stats:
                self.__stats.miss(resource_name)
            return None
