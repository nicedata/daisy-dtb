"""
Classes to represent the source of a Daisy book.

The book may be in a folder (filesystem) or in a remote location (website).

"""

from io import BytesIO
import urllib.request
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.error import HTTPError, URLError

from loguru import logger


class DtbResource(ABC):
    def __init__(self, resource_base: str) -> None:
        """Creates a new `DtbResource`.

        Args:
            resource_base (str): a filesystem folder or a web site

        Raises:
            FileNotFoundError when the resource is not accessible

        """
        self.resource_base = resource_base

    @abstractmethod
    def get(self, resource_name: str) -> bytes | str | None:
        """Get data and return it as a byte array or a string, or None in case of an error.

        Args:
            resource_name (str): the resource to get (typically a file name)

        Returns:
            bytes | str | None: returned data (str or bytes or None if the resource was not found)
        """


# class FileDtbResource(DtbResource):
#     """This class gets data from the file system"""

#     def __init__(self, resource_base) -> None:
#         super().__init__(resource_base)
#         self.resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"

#         if not Path(self.resource_base).exists():
#             raise FileNotFoundError

#     def get(self, resource_name: str) -> bytes | str | None:
#         path = Path(f"{self.resource_base}{resource_name}")
#         try:
#             with open(path, "rb") as resource:
#                 data: bytes = resource.read()
#         except FileNotFoundError as e:
#             logger.error(f"Error: {e.strerror} ({path})")
#             return None

#         try:
#             return data.decode("utf-8")
#         except UnicodeDecodeError:
#             return data


# class WebDtbResource(DtbResource):
#     """This class gets data from the web"""

#     def __init__(self, resource_base) -> None:
#         super().__init__(resource_base)
#         self.resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"
#         error = False
#         try:
#             urllib.request.urlopen(self.resource_base)
#         except HTTPError as e:
#             error = e.getcode() not in (200, 403)  # Code 403 is not necessary an error !
#         except URLError:
#             error = True

#         if error:
#             raise FileNotFoundError

#     def get(self, resource_name: str) -> bytes | str | None:
#         url = f"{self.resource_base}{resource_name}"
#         try:
#             response = urllib.request.urlopen(url)
#             data: bytes = response.read()
#         except HTTPError as e:
#             logger.error(f"HTTP error: {e.code} {e.reason} ({url})")
#             return None
#         except URLError as e:
#             logger.error(f"URL error: {e.reason} ({url})")
#             return None

#         try:
#             return data.decode("utf-8")
#         except UnicodeDecodeError:
#             return data


class FolderDtbResource(DtbResource):
    """This class gets data from a filesystem folder or a web location"""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base)
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

        if self.is_web_resource:
            # Get the data from the web
            try:
                response = urllib.request.urlopen(path)
                data: bytes = response.read()
            except HTTPError as e:
                logger.error(f"HTTP error: {e.code} {e.reason} ({path})")
                return None
            except URLError as e:
                logger.error(f"URL error: {e.reason} ({path})")
                return None
        else:
            # Get the data from the filesystem
            try:
                with open(path, "rb") as resource:
                    data: bytes = resource.read()
            except FileNotFoundError as e:
                logger.error(f"Error: {e.strerror} ({path})")
                return None

        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data


class ZipDtbResource(DtbResource):
    """This class gets data from a ZIP archive (from the filesystem or a web location)."""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base)
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
