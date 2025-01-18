from dataclasses import dataclass, field
from typing import List, Union

from loguru import logger

from domlib import Document, DomFactory


@dataclass(frozen=True)
class DocBufferItem:
    """This class represents a buffered resource."""

    name: str
    document: Document = None

    def __post_init__(self): ...


@dataclass
class DocBuffer:
    # Internal attributes
    _items: List[DocBufferItem] = field(default_factory=list)

    def add(self, name: str, data: str) -> Union[Document, None]:
        if not isinstance(data, str):
            message = "Only str elements can be added."
            logger.error(message)
            raise TypeError(message)

        # Do not add if name exists
        if name in [_.name for _ in self._items]:
            logger.debug(f"Document {name} already exists in the buffer.")
            return None

        document = DomFactory.create_document_from_string(data)
        if document is None:
            return None

        self._items.append(DocBufferItem(name, document))
        return document

    def get(self, name: str) -> Union[Document, None]:
        try:
            index = [_.name for _ in self._items].index(name)
            logger.debug(f"Index of item {name} is {index}.")
        except ValueError:
            logger.debug(f"Item {name} not found in buffer.")
            return None

        logger.debug(f"Item {name} found in the buffer.")
        return self._items[index]
