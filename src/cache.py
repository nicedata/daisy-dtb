"""Resource cacheing classes"""

from collections import deque
from dataclasses import InitVar, dataclass, field
from typing import Any, List, Set, Union

from loguru import logger

from domlib import DomFactory


@dataclass
class CacheStatItem:
    name: str = field(init=True)
    hits: int = 0
    queries: int = field(init=False, default=1)

    @property
    def efficiency(self) -> float:
        return self.hits / self.queries


@dataclass
class CacheStats:
    _item_names: Set[str] = field(init=False, default_factory=set)
    _items: List[CacheStatItem] = field(init=False, default_factory=list)

    def add(self, item: CacheStatItem) -> None:
        if item.name in self._item_names:
            item_index = [_.name for _ in self._items].index(item.name)
            cache_stat_item = self._items[item_index]
            cache_stat_item.queries += 1
            cache_stat_item.hits = cache_stat_item.hits + item.hits
        else:
            self._item_names.add(item.name)
            self._items.append(item)

    def get_stats(self) -> str:
        result = ["Cache statistics"]
        self._items.sort(key=lambda x: x.name)
        for item in self._items:
            result.append(f"{item.name:10s} :: queries: {item.queries:4}, hits: {item.hits:4}, efficiency: {item.efficiency*100:.2f} %")
        return "\n".join(result)


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


# @dataclass
@dataclass(kw_only=True)
class Cache:
    """Representation of resource cache"""

    max_size: InitVar[int] = 0
    with_stats: InitVar[bool] = False

    # Internal attributes
    __items: deque[CacheItem] = field(init=False, default_factory=deque)
    __with_stats: bool = field(init=False, default=False)
    __queries: int = field(init=False, default=0)
    __hits: int = field(init=False, default=0)
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

    @property
    def queries(self) -> int:
        """Get the number of cache queries.

        Returns:
            int: the number of queries
        """
        return self.__queries

    @property
    def hits(self) -> int:
        """Get the number of cache hits.

        Returns:
            int: the number of hits
        """
        return self.__hits

    @property
    def efficiency(self) -> float:
        """Get the cache efficiency

        Returns:
            float: a number between 0 (0%) and 1 (100%)
        """
        return self.__hits / self.__queries if self.__queries > 0 else 0.0

    def stats(self):
        return self.__stats.get_stats()

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
        # Type check
        if not isinstance(new_size, int):
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

    def add(self, item: CacheItem) -> None:
        """Add a `CacheItem` into the cache.

        This method takes care of the cache size:
            - If it is 0, nothing is done unless auto_expand is true.
            - If the addition would overfill the cache, the oldest item is removed before adding the new one.

        Args:
            item (CacheItem): the item to add.

        """
        # Checks
        if self.__items.maxlen == 0 or not isinstance(item, CacheItem):
            return

        item_name = item.get_name()

        # Check if item exists
        try:
            item_index = [_.get_name() for _ in self.__items].index(item_name)
            self.__items[item_index] = item
            logger.debug(f"Item '{item_name}' in the cache (index={item_index}) has been updated.")
            return
        except ValueError:
            ...

        # Append the item
        self.__items.append(item)
        logger.debug(f"Item '{item_name}' added into the cache.")

    def get(self, resource_name: str) -> CacheItem | None:
        """Get a `CacheItem` from the cache.

        Args:
            resource_name (str): the requested resource

        Returns:
            CacheItem | None: the found `CacheItem` or None
        """
        self.__queries += 1
        result = None
        stat_item = CacheStatItem(resource_name) if self.__with_stats else None

        try:
            item_index = [_.get_name() for _ in self.__items].index(resource_name)
            if stat_item:
                stat_item.hits = 1
            self.__hits += 1
            logger.debug(f"Item '{resource_name}' found in the cache (index={item_index}).")
            result = self.__items[item_index]
        except ValueError:
            logger.debug(f"Item '{resource_name}' not found in the cache.")

        if self.__with_stats:
            self.__stats.add(stat_item)
        return result
