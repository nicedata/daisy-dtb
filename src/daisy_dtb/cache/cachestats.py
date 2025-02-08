"""Cache statistics"""

from dataclasses import dataclass, field
from typing import List, cast


@dataclass
class _CacheStatItem:
    """This classe represents cache statistics item.

    It is intended for internal use.
    """

    name: str = field(init=True)
    hits: int = field(init=False, default=0)
    queries: int = field(init=False, default=1)

    @property
    def efficiency(self) -> float:
        return self.hits / self.queries


@dataclass
class CacheStats:
    # Private attributs
    _items: List[_CacheStatItem] = field(init=False, default_factory=list)

    def hit(self, resource_name: str) -> None:
        item = _CacheStatItem(resource_name)
        item.hits = 1
        self._add(item)

    def miss(self, resource_name: str) -> None:
        item = _CacheStatItem(resource_name)
        item.hits = 0
        self._add(item)

    def _add(self, item: _CacheStatItem) -> None:
        """Add a statistics item to the cache

        Args:
            item (CacheStatItem): the item to add
        """
        try:
            item_index = [_.name for _ in self._items].index(item.name)
            cache_stat_item = self._items[item_index]
            cache_stat_item.queries += 1
            cache_stat_item.hits = cache_stat_item.hits + item.hits
        except ValueError:
            self._items.append(item)

    def get_stats(self) -> dict:
        """Get the cache statistics.

        Returns:
            dict: a dictionary holding the global stats and the details
        """
        hit_count = sum([_.hits for _ in self._items])
        query_count = sum([_.queries for _ in self._items])
        result = {
            "cached_items": len(self._items),
            "total_queries": query_count,
            "total_hits": hit_count,
            "cache_efficiency": hit_count / query_count if query_count else 0,
            "details": [],
        }

        self._items.sort(key=lambda x: x.name)
        for item in self._items:
            detail = {
                "item_name": item.name,
                "queries": item.queries,
                "hits": item.hits,
                "efficiency": item.efficiency,
            }
            cast(list, result["details"]).append(detail)
        return result
