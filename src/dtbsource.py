"""
Classes to represent the source of a Daisy book.

The book may be in a folder (filesystem) or in a remote location (website).

"""

import urllib.request
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError

from loguru import logger

from resourcebuffer import ResourceBuffer, ResourceBufferItem

MAX_RESOURCE_BUFFER_SIZE = 50


class DtbResource(ABC):
    def __init__(self, resource_base: str, buffer_size=0) -> None:
        """Creates a new `DtbResource`.

        Args:
            resource_base (str): a filesystem folder or a web site
            buffer_size (int, optional): the size of the resource buffer. Defaults to 0.

        Raises:
            ValueError: if the requested buffer size is less than 0 or greater than `MAX_RESOURCE_BUFFER_SIZE`.
        """

        if buffer_size < 0:
            raise ValueError("The buffer minimum cannot be negative.")
        if buffer_size > MAX_RESOURCE_BUFFER_SIZE:
            raise ValueError(f"The buffer minimum cannot be greater then {MAX_RESOURCE_BUFFER_SIZE}.")

        self.buffer_size = buffer_size
        self.resource_base = resource_base

        self.buffer: ResourceBuffer = ResourceBuffer(self.buffer_size) if self.buffer_size else None

    @abstractmethod
    def get(self, resource_name: str) -> bytes | str | None:
        """Get data and return it as a byte array or a string, or None in case of an error.

        Args:
            resource_name (str): the resource to get (typically a file name)

        Returns:
            bytes | str | None: returned data (str or bytes or None if the resource was not found)
        """
        raise NotImplementedError

    def _convert_data(self, data: bytes) -> bytes | str:
        """Convert `bytes` to a `str` if possible.

        Args:
            data (bytes): the input bytes.

        Returns:
            bytes | str: the returned str (or bytes).
        """
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data

    def _get_from_buffer(self, resource_name: str) -> ResourceBufferItem | None:
        if self.buffer is None:
            return None

        data = self.buffer.get(resource_name)
        if data is not None:
            return data

        return None

    def _add_to_buffer(self, resource_name: str, data: bytes) -> None:
        if self.buffer is None:
            return

        self.buffer.add(ResourceBufferItem(resource_name, data))


class FolderDtbResource(DtbResource):
    """This class gets data from a filesystem folder or a web location"""

    def __init__(self, resource_base: str, buffer_size=0) -> None:
        super().__init__(resource_base, buffer_size)
        self.resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"
        self.is_web_resource: bool = "://" in self.resource_base
        error = False

        if self.is_web_resource:
            try:
                urllib.request.urlopen(self.resource_base)
            except HTTPError as e:
                error = e.getcode() not in (200, 403)  # Code 403 is not necessary an error !
            except URLError:
                error = True
        else:
            if not Path(self.resource_base).exists():
                error = True

        if error:
            raise FileNotFoundError

    def get(self, resource_name: str) -> bytes | str | None:
        path = f"{self.resource_base}{resource_name}"

        # Try to get data from the buffered resources
        buffered_resource = self._get_from_buffer(resource_name)
        if buffered_resource is not None:
            return self._convert_data(buffered_resource.data)

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

        self._add_to_buffer(resource_name, data)

        return self._convert_data(data)


class ZipDtbResource(DtbResource):
    """This class gets data from a ZIP archive (from the filesystem or a web location)."""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base, 0)
        self.bytes_io: BytesIO = None
        self.is_web_resource: bool = "://" in self.resource_base
        error = False

        if self.is_web_resource:
            # Store the bytes as BytesIO to avoid multiple web requests
            try:
                with urllib.request.urlopen(self.resource_base) as response:
                    self.bytes_io = BytesIO(response.read())
            except URLError:
                error = True
        else:
            # Work in the filesystem
            if not Path(self.resource_base).exists():
                error = True

            if not zipfile.is_zipfile(self.resource_base):
                error = True

        if error:
            raise FileNotFoundError

    def get(self, resource_name: str) -> bytes | str | None:
        error = False

        # Set the correct source
        source = self.bytes_io if self.is_web_resource else self.resource_base

        with zipfile.ZipFile(source, mode="r") as archive:
            try:
                data = archive.read(resource_name)
            except KeyError:
                error = True

        if error:
            logger.error(f"Error: archive {self.resource_base} does not contain file {resource_name}")
            return None

        try:
            return data.decode("utf-8")  # str
        except UnicodeDecodeError:
            return data  # bytes
