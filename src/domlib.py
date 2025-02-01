"""Classes to encapsulate and simplify the usage of the xml.dom.minidom library."""

import re
import urllib.request
import xml.dom.minidom
from dataclasses import InitVar, dataclass, field
from typing import Dict, List, Optional, Union
from urllib.error import HTTPError, URLError
from xml.dom.minidom import parseString as xdm_parse_string
from xml.parsers.expat import ExpatError

from loguru import logger


@dataclass
class Element:
    """Representation of a DOM element."""

    xml_node: InitVar[xml.dom.minidom.Element]  # The node in the xml.dom.minidom referential

    # Internal attributes
    _xml_node: xml.dom.minidom.Element = field(init=False, default=None)
    _children: "ElementList" = field(init=False, default=None)

    def __post_init__(self, xml_node: xml.dom.minidom.Element):
        """Post initialization of the Element instance."""
        if not isinstance(xml_node, xml.dom.minidom.Element):
            return

        self._xml_node = xml_node
        self._children = DomFactory.create_element_list(self._xml_node.childNodes)

    def _get_text(self, root: xml.dom.minidom.Node, _text: str = "") -> str:
        """Get text from the root element and its children.

        Notes:
            - This method is recursive.
            - Do not call directly (private method).

        Args:
            root (xml.dom.minidom.Node): the root element
            _text (str, optional): the current text. Defaults to "".

        Returns:
            str: the full string.
        """
        child: xml.dom.minidom.Element
        for child in root.childNodes:
            match child.nodeType:
                case xml.dom.minidom.Node.TEXT_NODE:
                    _text += child.nodeValue
                case xml.dom.minidom.Node.ELEMENT_NODE:
                    # Recurse here !
                    _text = self._get_text(child, _text)
                case _:
                    # Do nothing !
                    ...

        return _text

    @property
    def is_void(self) -> bool:
        """Test if the class is fully instanciated.

        Returns:
            bool: True if the class is correctly intanciated, False otherwise.
        """
        return isinstance(self._xml_node, xml.dom.minidom.Element) is False

    @property
    def has_children(self) -> bool:
        return self._children.size > 0

    @property
    def name(self) -> Union[str, None]:
        """Get the element's name (tag name)."""
        if self.is_void:
            return None

        return self._xml_node.tagName if not self.is_void else None

    @property
    def value(self) -> Union[str, None]:
        if self.is_void:
            return None

        return self._xml_node.firstChild.nodeValue if self._xml_node.hasChildNodes() else None

    @property
    def text(self) -> Union[str, None]:
        """Returns a string with no carriage returns and duplicate spaces."""
        if self.is_void:
            return None

        text = self._get_text(self._xml_node)
        return re.sub(r"\s+", " ", text).strip() if len(text) else None

    @property
    def parent(self) -> Union["Element", None]:
        """Get the parent element.

        Returns:
            Element: an element or None
        """
        if self.is_void:
            return None

        return Element(self._xml_node.parentNode) if self._xml_node.parentNode else None

    def get_attr(self, attr: str) -> Union[str, None]:
        """Get the value of an attribute."""
        if self.is_void:
            return None

        attr = self._xml_node.getAttribute(attr)
        return attr if attr else None

    def get_children_by_tag_name(self, tag_name: Optional[str] = "") -> Union["ElementList", None]:
        """Get all child elements by tag name (or all if no tag_name is specified).

        Args:
            tag_name (str, optional): the searched tag name. Defaults to "".

        Returns:
            ElementList: an element list or None.
        """
        if self.is_void or isinstance(tag_name, str) is False:
            return None

        if tag_name.strip() == "":
            return self._children

        result = ElementList()
        child: Element
        for child in self._children.all():
            if child.name == tag_name:
                result.elements.append(child)

        return result


@dataclass
class ElementList:
    elements: List[Element] = field(default_factory=list)

    @property
    def size(self) -> int:
        """Get the number of elements."""
        return len(self.elements)

    def append(self, element: Element) -> None:
        """Add an element."""
        if element and isinstance(element, Element):
            self.elements.append(element)

    def first(self) -> Element | None:
        """Get the first element."""
        return self.elements[0] if self.size > 0 else None

    def all(self) -> List[Element]:
        """Get all elements"""
        return self.elements


@dataclass
class Document:
    """This class represents a whole xml or html document."""

    xml_node: InitVar[xml.dom.minidom.Document]

    # Internal attributes
    _xml_node: xml.dom.minidom.Element = field(init=False, default=None)

    def __post_init__(self, xml_node: xml.dom.minidom.Document):
        """Post initialization of the Document instance."""
        if not isinstance(xml_node, xml.dom.minidom.Document):
            return
        self._xml_node = xml_node

    def get_element_by_id(self, id: str) -> Union[Element, None]:
        """Get an element by its id"""
        for elt in self._xml_node.getElementsByTagName("*"):
            if elt.getAttribute("id") == id:
                return Element(xml_node=elt)
        return None

    def get_elements_by_tag_name(self, tag_name: str, filter: Dict = {}, having_parent_tag_name: str = None) -> ElementList:
        """
        Get elements by tag name.

        A filter on attributes can be specified. The form is `{"attribute_name": "attribute_value"}`.

        Since xml.minidom does a recursive search, a parent tag name can be specified to filter out unwanted elements.

        Args:
            tag_name (str): the seaerched tag name
            filter (Dict, optional): the attribute filter. Defaults to {}.
            having_parent_tag_name (str, optional): the parent tag name filter. Defaults to None.

        Returns:
            ElementList | None: the searched element (may be empty).
        """
        if self._xml_node is None:
            return ElementList()

        logger.debug(f"tag_name: {tag_name}, filter: {filter}, parent_tag_name: {having_parent_tag_name}")
        xdm_nodes = self._xml_node.getElementsByTagName(tag_name)

        # Filter data
        if having_parent_tag_name:
            xdm_node_list = []
            for xdm_element in xdm_nodes:
                if xdm_element.parentNode.tagName == having_parent_tag_name:
                    xdm_node_list.append(xdm_element)
        else:
            xdm_node_list = xdm_nodes

        # No filter : get all elements
        if len(filter.items()) == 0:
            return DomFactory.create_element_list(xdm_node_list)

        # With filtering
        result = ElementList()
        for elt in xdm_node_list:
            for k, v in filter.items():
                attr = elt.getAttribute(k)
                if attr == v:
                    result.append(Element(xml_node=elt))

        return result


class DomFactory:
    """This class holds a collection of static methods to create various class instances."""

    @staticmethod
    def create_document_from_string(string: str) -> Union[Document, None]:
        """Create a Document from a string.
        Args:
            string (str): The string to parse

        Returns:
            Document | None: a Document or None
        """
        # Type chack
        if not isinstance(string, str) or len(string) == 0:
            return None

        try:
            xdm_document = xdm_parse_string(string)
        except ExpatError as e:
            logger.error(f"An xml.minidom parsing error occurred. The code is {e.code}.")
            return None
        return Document(xml_node=xdm_document)

    @staticmethod
    def create_document_from_url(url: str) -> Union[Document, None]:
        """Create a Document from an URL.
        Args:
            url (str): The URL to parse

        Returns:
            Document | None: a Document or None
        """
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            return Document(xml_node=xdm_parse_string(data))
        except HTTPError as e:
            logger.error(f"HTTP error: {e.code} {e.reason} ({url})")
        except URLError as e:
            logger.error(f"URL error: {e.reason} ({url})")
        return None

    @staticmethod
    def create_document_from_bytes(data: bytes) -> Union[Document, bytes]:
        if not isinstance(data, bytes):
            return data

        try:
            string = data.decode("utf-8")
            return DomFactory.create_document_from_string(string)
        except UnicodeDecodeError:
            ...

        return data

    @staticmethod
    def create_element_list(xml_nodes: List[xml.dom.minidom.Element]) -> ElementList:
        """Create an Element list from a list of xml.minidom nodes.

        Args:
            nodes (List[xml.dom.minidom.Element]): an xml.minidom element list.

        Returns:
            ElementList: a list of Element
        """
        result = ElementList()
        for node in xml_nodes:
            if isinstance(node, xml.dom.minidom.Element):
                result.elements.append(Element(xml_node=node))

        return result
