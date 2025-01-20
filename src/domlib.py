"""Classes to encapsulate and simply the usage of the xml.dom.minidom library."""

import re
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Union
from urllib.error import HTTPError, URLError
from xml.dom.minidom import Document as XdmDocument
from xml.dom.minidom import Element as XdmElement
from xml.dom.minidom import Node as XdmNode
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

from loguru import logger


@dataclass
class Element:
    """Representation of a DOM element."""

    _node: XdmElement = None  # The node in the xml.dom.minidom referential
    _children: "ElementList" = None  # 'ElementList'()  List["Element"] = field(default_factory=list)  # Child elements

    def __post_init__(self):
        """Populate the child elements list."""
        self._children = DomFactory.create_element_list(self._node.childNodes)

    def get_name(self) -> str:
        """Get the element's name (tag name)."""
        return self._node.tagName

    def get_attr(self, attr: str) -> str:
        """Get the value of an attribute."""
        return self._node.getAttribute(attr)

    def get_value(self) -> str | None:
        return self._node.firstChild.nodeValue if self._node.hasChildNodes() else None

    def _get_text(self, root: "Element", _text: str = "") -> str:
        """Get text from the root element and its children.

        Note:
            - This method is recursive.
            - Do not call directly (private method).

        Args:
            root (Element): the root element
            _text (str, optional): the current text. Defaults to "".

        Returns:
            str: the full string.
        """
        for child in root.childNodes:
            match child.nodeType:
                case XdmNode.TEXT_NODE:
                    _text += child.nodeValue
                case XdmNode.ELEMENT_NODE:
                    # Recurse here !
                    _text = self._get_text(child, _text)
                case _:
                    ...
        return _text

    def get_text(self) -> str:
        """Returns a string with no carriage returns and duplicate spaces."""
        text = self._get_text(self._node)
        return re.sub(r"\s+", " ", text).strip() if len(text) else ""

    def get_children(self, tag_name: str = None) -> "ElementList":
        """Get all child elements by tag name (or all if no tag_name is specified)."""
        if tag_name is None:
            return self._children

        result = ElementList()
        child: Element
        for child in self._children.all():
            if child.get_name() == tag_name:
                result._elements.append(child)

        return result

    def get_parent(self) -> Union["Element", None]:
        """Get the parent element."""
        return Element(self._node.parentNode)


@dataclass
class ElementList:
    _elements: List[Element] = field(default_factory=list)

    def get_size(self):
        """Get the number of elements."""
        return len(self._elements)

    def add_element(self, element: Element) -> None:
        """Add an element."""
        if element and isinstance(element, Element):
            self._elements.append(element)

    def first(self) -> Element | None:
        """Get the first element."""
        return self._elements[0] if self.get_size() > 0 else None

    def all(self) -> List[Element]:
        """Get all elements"""
        return self._elements


@dataclass
class Document:
    """This class represents a whole xml or html document."""

    _root: XdmDocument = None

    def get_element_by_id(self, id: str) -> Union[Element, None]:
        """Get an element by its id"""
        for elt in self._root.getElementsByTagName("*"):
            if elt.getAttribute("id") == id:
                return Element(_node=elt)
        return None

    def get_elements_by_tag_name(self, tag_name: str, filter: Dict = {}, having_parent_tag_name: str = None) -> Union[ElementList, None]:
        """
        Get elements by tag name.

        A filter on attributes can be specified. The form is `{"attribute_name": "attribute_value"}`.

        Since xml.minidom does a recursive search, a parent tag name can be specified to filter out unwanted elements.

        Args:
            tag_name (str): the seaerched tag name
            filter (Dict, optional): the attribute filter. Defaults to {}.
            having_parent_tag_name (str, optional): the parent tag name filter. Defaults to None.

        Returns:
            ElementList | None: the searched element (or None).
        """
        if self._root is None:
            return None
        logger.debug(f"tag_name: {tag_name}, filter: {filter}, parent_tag_name: {having_parent_tag_name}")
        nodes = self._root.getElementsByTagName(tag_name)

        node_list = []
        if having_parent_tag_name:
            for element in nodes:
                if element.parentNode.tagName == having_parent_tag_name:
                    node_list.append(element)
        else:
            node_list = nodes

        # No filter : get all elements
        if len(filter.items()) == 0:
            return DomFactory.create_element_list(node_list)

        # With filtering
        result = ElementList()
        for elt in node_list:
            for k, v in filter.items():
                attr = elt.getAttribute(k)
                if attr == v:
                    result.add_element(Element(_node=elt))
        return result


class DomFactory:
    """This class holds a collection of static methods to create class instances."""

    @staticmethod
    def create_document_from_string(string: str) -> Union[Document, None]:
        """Create a Document from a string.
        Args:
            string (str): The string to parse

        Returns:
            Document | None: a Document or None
        """
        try:
            xdm_document = parseString(string)
        except ExpatError as e:
            logger.error(f"An xml.minidom parsing error occurred. The code is {e.code}.")
            return None
        return Document(_root=xdm_document)

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
            return Document(_root=parseString(data))
        except HTTPError as e:
            logger.error(f"HTTP error: {e.code} {e.reason} ({url})")
        except URLError as e:
            logger.error(f"URL error: {e.reason} ({url})")
        return None

    @staticmethod
    def create_element_list(nodes: List[XdmElement]) -> ElementList:
        """Create an Element list from a list of xml.minidom nodes.

        Args:
            nodes (List[XdmElement]): The xml.minidom element list

        Returns:
            ElementList: a list of Element
        """
        result = ElementList()
        for node in nodes:
            if isinstance(node, XdmElement):
                result._elements.append(Element(_node=node))
        return result
