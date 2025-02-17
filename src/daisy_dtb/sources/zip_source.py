import zipfile
from io import BytesIO
from typing import Union

from loguru import logger

from ..utilities.domlib import Document
from ..utilities.fetcher import Fetcher
from .source import DtbSource


class ZipDtbSource(DtbSource):
    """This class gets data from a ZIP archive (from the filesystem or a web location)."""

    def __init__(self, base_path) -> None:
        super().__init__(base_path, 0)
        self.bytes_io: BytesIO = None

        if Fetcher.is_available(base_path) is False:
            raise FileNotFoundError

        # Get the zip data
        self.bytes_io = BytesIO(Fetcher.fetch(base_path))

        # Check if we have a good ZIP file
        if zipfile.is_zipfile(self.bytes_io):
            logger.debug(f"{base_path} is a valid ZIP archive.")
        else:
            raise FileNotFoundError

    def get(self, resource_name: str) -> Union[bytes, Document, None]:
        # Try to get data from the cached resources
        cached_data = self._cache.get(resource_name)
        if cached_data is not None:
            return cached_data

        # Retrieve the resource fron the ZIP file
        resource_path = ""
        with zipfile.ZipFile(self.bytes_io, mode="r") as archive:
            # Build a search path list from the ZIP directories
            for info in archive.infolist():
                if info.is_dir():
                    continue
                if resource_name in info.filename:
                    resource_path = info.filename
                    break

            # Search the resource
            try:
                data = archive.read(resource_path)
            except KeyError:
                logger.error(f"Error: archive {self._base_path} does not contain resource '{resource_name}'.")
                return None

        # Try to create a Document
        doc = DtbSource.convert_to_document(data)

        # Eventualy cache the resource
        self.do_cache(resource_name, doc)

        return doc
