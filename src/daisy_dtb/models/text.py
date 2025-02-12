from dataclasses import dataclass, field

from loguru import logger

from ..utilities.domlib import Document

from ..models.reference import Reference
from ..sources.source import DtbSource


@dataclass
class Text:
    """Representation of a text fragment in a text source file."""

    source: DtbSource
    id: str
    reference: Reference

    # Internal attributes
    _content: str = field(init=False, default=None)

    @property
    def content(self) -> str:
        """Get the text fragment identified by the reference.

        Note:
        - To avoid multiple resource accesses, the text is loaded from the source only once.

        Returns:
            str: the text fragment
        """
        if self._content is None:
            self._parse()
        return self._content

    def _parse(self) -> None:
        """Get the text from a resource.

        Notes:
        - If the text has already been retrieved, return the instances text content.


        Returns:
            str: the text.
        """
        # Check if text already here
        if self._content is not None:
            logger.debug(f"Content {self.reference.resource}/{self.reference.fragment} is already present.")
            return self._content

        # Get it from the source
        logger.debug(f"Loading text from {self.reference.resource}, fragment id is {self.reference.fragment}.")
        data = self.source.get(self.reference.resource)

        # The fetched data must be a Document
        if isinstance(data, Document) is False:
            logger.error(f"The retrieval attempt of {self.reference.resource} as Document failed.")
            self._content = ""
            return

        # Find the text identified by its id
        element = data.get_element_by_id(self.reference.fragment)
        if element is not None:
            self._content = element.text
            logger.debug(f"Text with id {self.reference.fragment} found in {self.reference.resource}.")
            return
        else:
            logger.error(f"Could not retrieve element {self.reference.fragment} in the {self.reference.resource} Document.")

        self._content = ""
