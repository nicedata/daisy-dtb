from abc import ABC, abstractmethod
from typing import Any, Union

from loguru import logger

from ..cache.cache import Cache
from ..utilities.domlib import Document, DomFactory


class DtbSource(ABC):
    def __init__(self, base_path: str, initial_cache_size=0) -> None:
        """Creates a new `DtbSource`.

        Args:
            base_path (str): a filesystem folder or a web site
            initial_cache_size (int, optional): the size of the resource cache. Defaults to 0.

        Raises:
            ValueError: if the requested cache size is less than 0.
        """
        if initial_cache_size < 0:
            raise ValueError("The cache size cannot be negative.")

        self._base_path = base_path
        self._cache = Cache(max_size=initial_cache_size)

    @property
    def base_path(self) -> str:
        return self._base_path

    @property
    def cache_size(self) -> int:
        return self._cache.maxlen

    @cache_size.setter
    def cache_size(self, size: int) -> None:
        """Resize the resource cache.

        Args:
            new_size (int): the new size.
        """
        self._cache.resize(size)

    @abstractmethod
    def get(self, resource_name: str) -> Union[bytes, str, Document, None]:
        """Get data and return it as a byte array or a string, or None in case of an error.

        When the resource is buffered
            - the method gets it from the buffer
            - if not found in the buffer, it is added to it

        Args:
            resource_name (str): the resource to get (typically a file name)

        Returns:
            bytes | str | None: returned data (str or bytes or None if the resource was not found)
        """
        raise NotImplementedError

    @staticmethod
    def convert_to_document(data: bytes) -> Union[Document | bytes]:
        """Try a conversion of the data to a Document.

        Args:
            data (bytes): the data bytes.

        Returns:
            Union[Document | bytes]: a document or the original bytes.
        """
        # Try to create a Document
        doc = DomFactory.create_document_from_bytes(data)
        if type(doc) is not type(data):
            logger.debug(f"Converted {type(data)} to {type(doc)}.")
        else:
            logger.debug("No conversion happened.")

        return doc

    def do_cache(self, key: str, data: Any) -> None:
        """Store the data into the cache.

        If the cache size is 0, nothing is done.

        Args:
            key (str): the key.
            data (Any): the data to cache.
        """
        self._cache.add(key, data)

    def enable_stats(self, value: bool) -> None:
        self._cache.enable_stats(value)
