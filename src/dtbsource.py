"""
Classes to represent the source of a Daisy book.

The book may be in a folder (filesystem) or in a remote location (website).

"""

import urllib.request
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Union
from urllib.error import HTTPError, URLError

from loguru import logger

from cache import Cache, _CacheItem
from domlib import Document


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

    @property
    def cache_size(self) -> int:
        return self._cache.get_max_size()

    @cache_size.setter
    def cache_size(self, size: int) -> None:
        """Resize the resource cache.

        Args:
            new_size (int): the new size.
        """
        self._cache.resize(size)

    def activate_stats(self, value: bool) -> None:
        self._cache.activate_stats_collection(value)


class FolderDtbResource(DtbResource):
    """This class gets data from a filesystem folder or a web location"""

    def __init__(self, resource_base: str, initial_cache_size=0) -> None:
        resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"
        self.is_web_resource: bool = "://" in resource_base
        super().__init__(resource_base, initial_cache_size)
        error = False

        if self.is_web_resource:
            try:
                urllib.request.urlopen(self._resource_base)
            except HTTPError as e:
                error = e.getcode() not in (200, 403)  # Code 403 is not necessary an error !
            except URLError:
                error = True
        else:
            if not Path(self._resource_base).exists():
                error = True

        if error:
            raise FileNotFoundError

    def get(self, resource_name: str) -> Union[bytes, str, Document, None]:
        path = f"{self._resource_base}{resource_name}"

        # Try to get data from the cached resources
        cached_resource = self._cache.get(resource_name)
        if cached_resource is not None:
            return cached_resource.data

        if self.is_web_resource:  # Get the data from the web
            try:
                response = urllib.request.urlopen(path)
                data: bytes = response.read()
            except HTTPError as e:
                logger.error(f"HTTP error: {e.code} {e.reason} ({path})")
                return None
            except URLError as e:
                logger.error(f"URL error: {e.reason} ({path})")
                return None
        else:  # Get the data from the filesystem
            try:
                with open(path, "rb") as resource_to_buffer:
                    data: bytes = resource_to_buffer.read()
            except FileNotFoundError as e:
                logger.error(f"Error: {e.strerror} ({path})")
                return None

        # Buffer the resource
        item = _CacheItem(resource_name, data)
        self._cache.add(item)

        return item.data


class ZipDtbResource(DtbResource):
    """This class gets data from a ZIP archive (from the filesystem or a web location)."""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base, 0)
        self.bytes_io: BytesIO = None
        self.is_web_resource: bool = "://" in self._resource_base
        error = False

        if self.is_web_resource:
            # Store the bytes as BytesIO to avoid multiple web requests
            try:
                with urllib.request.urlopen(self._resource_base) as response:
                    self.bytes_io = BytesIO(response.read())
            except URLError:
                error = True
        else:
            # Work in the filesystem
            if not Path(self._resource_base).exists():
                error = True

            if not zipfile.is_zipfile(self._resource_base):
                error = True

        if error:
            raise FileNotFoundError

    def set_cache_size(self, new_size: int) -> None:
        """Resize the resource buffer.

        In the `ZipDtbResource` class, this method does nothing sice the ZIP archive is already loaded internally.

        Args:
            new_size (int): the new size.
        """
        return

    def get(self, resource_name: str) -> bytes | str | None:
        error = False

        # Set the correct source
        source = self.bytes_io if self.is_web_resource else self._resource_base

        with zipfile.ZipFile(source, mode="r") as archive:
            try:
                data = archive.read(resource_name)
            except KeyError:
                error = True

        if error:
            logger.error(f"Error: archive {self._resource_base} does not contain file {resource_name}")
            return None

        # Try to return decoded data
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data
