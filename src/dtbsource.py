"""
Classes to represent the source of a Daisy book.

The book may be in a folder (filesystem) or in a remote location (website).

"""

import zipfile
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Union

from loguru import logger

from cache import Cache
from domlib import Document, DomFactory
from fetcher import Fetcher


class DtbResource(ABC):
    def __init__(self, resource_base: str, initial_cache_size=0) -> None:
        """Creates a new `DtbResource`.

        Args:
            resource_base (str): a filesystem folder or a web site
            initial_cache_size (int, optional): the size of the resource buffer. Defaults to 0.

        Raises:
            ValueError: if the requested cache size is less than 0.
        """
        if initial_cache_size < 0:
            raise ValueError("The cache size cannot be negative.")

        self._resource_base = resource_base
        self._cache = Cache(max_size=initial_cache_size)

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
        if self.cache_size > 0:
            self._cache.add(key, data)
            logger.debug(f"Resource {key} added to the cache as {type(data)}.")

    def enable_stats(self, value: bool) -> None:
        self._cache.enable_stats(value)


class FolderDtbResource(DtbResource):
    """This class gets data from a filesystem folder or a web location"""

    def __init__(self, resource_base: str, initial_cache_size=0) -> None:
        resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"
        super().__init__(resource_base, initial_cache_size)

        if Fetcher.is_available(resource_base) is False:
            raise FileNotFoundError

    def get(self, resource_name: str) -> Union[bytes, str, Document, None]:
        path = f"{self._resource_base}{resource_name}"

        # Try to get data from the cached resources
        if self.cache_size > 0:
            cached_data = self._cache.get(resource_name)
            if cached_data is not None:
                return cached_data

        data = Fetcher.fetch(path)

        # Try to create a Document
        doc = DtbResource.convert_to_document(data)

        # Eventualy cache the resource
        self.do_cache(resource_name, doc)

        return doc


class ZipDtbResource(DtbResource):
    """This class gets data from a ZIP archive (from the filesystem or a web location)."""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base, 0)
        self.bytes_io: BytesIO = None

        if Fetcher.is_available(resource_base) is False:
            raise FileNotFoundError

        # Get the zip data
        self.bytes_io = BytesIO(Fetcher.fetch(resource_base))

        # Check if we have a good ZIP file
        if zipfile.is_zipfile(self.bytes_io):
            logger.debug(f"{resource_base} is a valid ZIP archive.")
        else:
            raise FileNotFoundError

    def get(self, resource_name: str) -> bytes | str | None:
        # Try to get data from the cached resources
        cached_data = self._cache.get(resource_name)
        if cached_data is not None:
            return cached_data

        # Retrieve the resource fron the ZIP file
        with zipfile.ZipFile(self.bytes_io, mode="rb") as archive:
            try:
                data = archive.read(resource_name)
            except KeyError:
                logger.error(f"Error: archive {self._resource_base} does not contain file {resource_name}")
                return None

        # Try to create a Document
        doc = DtbResource.convert_to_document(data)

        # Eventualy cache the resource
        self.do_cache(resource_name, doc)

        return doc
