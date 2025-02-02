"""Resources operations"""

from dataclasses import dataclass, field
from http.client import HTTPResponse
from pathlib import Path
from urllib.error import HTTPError, URLError
import urllib.request
from loguru import logger
import urllib


@dataclass
class Fetcher:
    """This class provides static methods to
    - check resource availability
    - fetch resources

    It automatically handles the location of the resource (file system or web).
    """

    fetched_bytes: int = field(init=False, default=0)
    access_count: int = field(init=False, default=0)

    @staticmethod
    def get_stats() -> dict:
        """Get the fetcher statistics.

        Returns:
            dict: a dict with following keys:
            - "access_count" : the number of times the fetcher was used.
            - "fetched_bytes" : the number of retrieved bytes.
        """
        return {
            "access_count": Fetcher.access_count,
            "fetched_bytes": Fetcher.fetched_bytes,
        }

    @staticmethod
    def is_on_web(resource_path: str) -> bool:
        """Test if the resource is located on the web.

        Args:
            resource (str): the resource (full path).

        Returns:
            bool: True if there is '://' in the full resource path, False otherwise.
        """
        return "://" in resource_path

    @staticmethod
    def is_available(resource_path: str) -> bool:
        """Checks the availability of a resource.

        Args:
            resource (str): the resource (folder or web location).

        Returns:
            bool: True if the resource is found, False otherwise.
        """
        logger.debug(f"Checking availability of '{resource_path}'.")

        # Check
        if not isinstance(resource_path, str):
            logger.debug("No valid data supplied.")
            return False

        Fetcher.access_count += 1
        if Fetcher.is_on_web(resource_path):
            # Check web availability
            try:
                response = urllib.request.urlopen(resource_path)
                if isinstance(response, HTTPResponse) and response.getcode() == 200:
                    logger.debug("Web check success. Error code is 200.")
                    return True
                else:
                    logger.debug("Web check failed. Response is not of type HTTPResponse or error code is not 200.")
                    return False
            except HTTPError as e:
                error_code = e.getcode()
                if error_code in (200, 403):  # Code 403 is not necessarily an error !
                    logger.debug(f"Web check success. Error code is {error_code}. Codes 200 and 403 are OK.")
                    return True
                logger.debug(f"Web check fails. Error code is {error_code}.")
                return False
            except URLError:
                logger.debug(f"Web check fails wit an URL error. The failing URL is {resource_path}.")
                return False
        else:
            # Check file system availability
            if Path(resource_path).exists():
                logger.debug("File check success.")
                return True
            else:
                logger.debug(f"File check fails. The Path is {resource_path}")
                return False

    @staticmethod
    def fetch(resource_path: str) -> bytes:
        """Fetch a given resource

        Args:
            resource (str): the resource to fetch (full path).

        Returns:
            bytes: the fetched bytes (or b'').
        """
        Fetcher.access_count += 1

        logger.debug(f"Fetching '{resource_path}'.")
        # Check
        if not isinstance(resource_path, str):
            logger.debug("No valid data supplied.")
            return b""

        if Fetcher.is_on_web(resource_path):
            # Get data from web
            try:
                response = urllib.request.urlopen(resource_path)
                if isinstance(response, HTTPResponse) and response.getcode() == 200:
                    data = response.read()
                    Fetcher.fetched_bytes += len(data)
                    logger.debug(f"Fetched {len(data)} bytes from {resource_path}.")
                    return data
                else:
                    logger.debug(f"Nothing fetched from {resource_path}.")
                    return b""
            except URLError:
                logger.debug(f"URL error: {resource_path}.")
                return b""
        else:
            # Get data from file system
            try:
                with open(resource_path, "rb") as file:
                    data = file.read()
                    Fetcher.fetched_bytes += len(data)
                    logger.debug(f"Fetched {len(data)} bytes from {resource_path}.")
                    return data
            except FileNotFoundError:
                logger.debug(f"Nothing fetched from {resource_path} (not found).")
            except IsADirectoryError:
                logger.debug(f"Nothing fetched from {resource_path} (the resource is a folder).")

            return b""
