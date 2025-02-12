"""Resource cacheing classes"""

from collections import deque
from dataclasses import InitVar, dataclass, field
from typing import Any

from loguru import logger

from .cachestats import CacheStats


@dataclass
class _CacheItem:
    """This class represents a cached resource.

    Note:
    - It is intended for internal use.
    """

    key: str
    data: Any

    def __post_init__(self):
        """Class post initilization."""
        logger.debug(f"The cache item '{self.key}' has been created. Its type is {type(self.data)}.")

    @property
    def type(self) -> type:
        """Get the cached data type.

        Returns:
            type: the data type
        """
        return type(self.data)


@dataclass
class Cache:
    """Representation of resource cache"""

    max_size: InitVar[int] = 0
    with_stats: InitVar[bool] = False

    # Internal attributes
    _items: deque[_CacheItem] = field(init=False, default_factory=deque)
    _with_stats: bool = field(init=False, default=False)
    _stats: CacheStats = field(init=False, default_factory=CacheStats)

    def __post_init__(self, max_size: int, with_stats: bool) -> None:
        """Cache post initialize.

        Args:
            max_size (int): the cache size.
        """

        if max_size < 0:
            logger.warning(f"The cache size must be positive. {max_size} was supplied: cache size set to 0.")
            max_size = 0

        self._items = deque(maxlen=max_size)
        self._with_stats = with_stats
        logger.debug(f"Cache created. Size: {max_size}. Statistics collection is {'active' if self._with_stats else 'inactive'}.")

    @property
    def maxlen(self) -> int:
        return self._items.maxlen

    def get_stats(self) -> dict:
        """Get the cache statistics.

        Returns:
            dict: a dict with the statistics.
        """
        return self._stats.get_stats()

    def enable_stats(self, value: bool) -> None:
        """Enable or disable statistics collection.

        Args:
            value (bool): True -> enable, False -> disable.
        """
        self._with_stats = value
        logger.debug(f"Cache statistics collection is {'active' if self._with_stats else 'inactive'}.")

    def resize(self, new_size: int) -> None:
        """Resize the cache.

        Args:
            new_size (int): the new size
        """
        # Checks
        if not isinstance(new_size, int) or (new_size < 0) or (new_size == self._items.maxlen):
            return

        # Cache migration
        logger.debug(f"Resizing the cache from {self._items.maxlen} to {new_size}.")
        new_cache = deque(maxlen=new_size)
        self._items.reverse()
        if new_cache.maxlen > 0:
            for index, item in enumerate(self._items):
                if index > new_cache.maxlen - 1:
                    break
                new_cache.appendleft(item)

        self._items = new_cache
        logger.debug(f"The cache size now is {self._items.maxlen}.")

    def add(self, key: str, data: Any) -> None:
        """Add data into the cache.

        Notes :
            - If the cache max. length is 0, nothing is done.
            - If the kex exists in the cache, data is updated.
            - If the addition would overfill the cache, the oldest item is removed before adding the new one.

        Args:
            key (str): the key.
            data (Any): the data.
        """

        # Checks
        if self._items.maxlen == 0:
            return

        try:
            # Check if item exists and update the current data
            item_index = [_.key for _ in self._items].index(key)
            self._items[item_index].data = data
            logger.debug(f"Resource '{key}' in the cache (index={item_index}) has been updated.")
            return
        except ValueError:
            # Otherwise append the item
            self._items.append(_CacheItem(key, data))
            logger.debug(f"Item '{key}' added into the cache as {type(data)}.")

    def get(self, key: str) -> Any | None:
        """Get data from the cache.

        Args:
            resource_name (str): the requested resource

        Returns:
            Any | None: the found data or None
        """
        # No cache, no data
        if self._items.maxlen == 0:
            logger.debug("There is no cache size defined. Returning 'None'.")
            return None

        try:
            # Try to find the key
            item_index = [_.key for _ in self._items].index(key)
            logger.debug(f"Item '{key}' found in the cache (index={item_index}).")
            if self._with_stats:
                self._stats.hit(key)
            return self._items[item_index].data
        except ValueError:
            # Key not found
            logger.debug(f"Item '{key}' not found in the cache.")
            if self._with_stats:
                self._stats.miss(key)
            return None
