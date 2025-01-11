"""
Classes to represent the source of a Daisy book.

The book may be in a folder (filesystem) or in a remote location (website).

"""

import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError
from abc import ABC, abstractmethod
from loguru import logger


class DtbResource(ABC):
    def __init__(self, resource_base: str) -> None:
        """Creates a new `DtbResource`.

        Args:
            resource_base (str): a filesystem folder or a web site

        Raises:
            FileNotFoundError when the resource is not accessible

        """
        self.resource_base = resource_base if resource_base.endswith("/") else f"{resource_base}/"

    @abstractmethod
    def get(self, resource_name: str, convert_to_str: bool = True) -> bytes | str | None:
        """Get data and return it as a byte array or a string, or None in case of an error.

        Args:
            resource_name (str): the resource to get (typically a file name)
            convert_to_str (bool, optional): it True, return a str. If False return bytes. Defaults to True.

        Raises:
            FileNotFoundError when the resource is not accessible

        Returns:
            bytes | str | None: returned data (str or bytes or None if the resource was not found)
        """


class FileDtbResource(DtbResource):
    """This class gets data from the file system"""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base)
        if not Path(self.resource_base).exists():
            raise FileNotFoundError

    def get(self, resource_name: str, convert_to_str: bool = True) -> bytes | str | None:
        path = Path(f"{self.resource_base}{resource_name}")
        try:
            with open(path, "rb") as resource:
                data = resource.read()
                return data.decode("utf-8") if convert_to_str else data
        except FileNotFoundError as e:
            logger.error(f"Error: {e.strerror} ({path})")
            return None


class WebDtbResource(DtbResource):
    """This class gets data from the web"""

    def __init__(self, resource_base) -> None:
        super().__init__(resource_base)
        error = False
        try:
            urllib.request.urlopen(self.resource_base)
        except HTTPError as e:
            error = e.getcode() not in (200, 403)  # Code 403 is not necessary an error !
        except URLError:
            error = True

        if error:
            raise FileNotFoundError

    def get(self, resource_name: str, convert_to_str: bool = True) -> bytes | str | None:
        """Get the resource and return it as string"""
        url = f"{self.resource_base}{resource_name}"
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            return data.decode("utf-8") if convert_to_str else data
        except HTTPError as e:
            logger.error(f"HTTP error: {e.code} {e.reason} ({url})")
        except URLError as e:
            logger.error(f"URL error: {e.reason} ({url})")
        return None
