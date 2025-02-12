from typing import Union

from ..utilities.domlib import Document
from ..utilities.fetcher import Fetcher
from .source import DtbSource


class FolderDtbSource(DtbSource):
    """This class gets data from a filesystem folder or a web location"""

    def __init__(self, base_path: str, initial_cache_size=0) -> None:
        base_path = base_path if base_path.endswith("/") else f"{base_path}/"
        super().__init__(base_path, initial_cache_size)

        if Fetcher.is_available(base_path) is False:
            raise FileNotFoundError

    def get(self, resource_name: str) -> Union[bytes, Document, None]:
        path = f"{self._base_path}{resource_name}"

        # Try to get data from the cached resources
        cached_data = self._cache.get(resource_name)
        if cached_data is not None:
            return cached_data

        data = Fetcher.fetch(path)

        # Try to create a Document
        doc = DtbSource.convert_to_document(data)

        # Eventualy cache the resource
        self.do_cache(resource_name, doc)

        return doc
