"""Classes to encapsulate `xml.dom.minidom`."""

import re
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List
from urllib.error import HTTPError, URLError
from xml.dom.minidom import Document as XdmDocument
from xml.dom.minidom import Element as XdmElement
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

from loguru import logger


@dataclass
class Element(XdmElement):
    _node: XdmElement = None
    _children: List["Element"] = field(default_factory=list)

    def __post_init__(self):
        self._children = DomFactory.create_element_list(self._node.childNodes)

    def get_attr(self, attr: str) -> str:
        return self._node.getAttribute(attr)

    def get_value(self) -> str:
        if self._node.hasChildNodes():
            return self._node.firstChild.nodeValue
        return "???"

    def get_text(self) -> str:
        """Returns a string with no carriage returns and duplicate spaces."""
        node_value = self._node.firstChild.nodeValue
        return re.sub(r"\s+", " ", node_value) if node_value else ""

    def get_children(self, tag_name: str = None) -> "ElementList":

        if tag_name is None:
            return self._children

        result = ElementList()
        for child in self._children.all():
            if child.name == tag_name:
                result._elements.append(child)

        return result

    @property
    def name(self) -> str:
        return self._node.tagName


@dataclass
class ElementList:
    _elements: List[Element] = field(default_factory=list)

    def add_element(self, element: Element) -> None:
        if element and isinstance(element, Element):
            self._elements.append(element)

    def first(self) -> Element | None:
        return self._elements[0] if len(self._elements) > 0 else None

    def all(self) -> List[Element]:
        return self._elements


@dataclass
class Document:
    _root: XdmDocument = None

    def get_element_by_id(self, id: str) -> Element | None:
        for elt in self._root.getElementsByTagName("*"):
            if elt.getAttribute("id") == id:
                return Element(_node=elt)
        return None

    def get_elements(self, tag_name: str, filter: Dict = {}) -> ElementList | None:
        """Get elements by attribute."""
        if self._root is None:
            return None

        if len(filter.items()) == 0:
            return DomFactory.create_element_list(self._root.getElementsByTagName(tag_name))

        result = ElementList()
        for elt in self._root.getElementsByTagName(tag_name):
            for k, v in filter.items():
                attr = elt.getAttribute(k)
                if attr == v:
                    result.add_element(Element(_node=elt))
        return result


class DomFactory:
    @staticmethod
    def create_document_from_string(string: str) -> Document | None:
        try:
            xdm_document = parseString(string)
        except ExpatError as e:
            logger.error(f"An xml.minidom parsing error occurred. The code is {e.code}.")
            return None
        return Document(_root=xdm_document)

    @staticmethod
    def create_document_from_url(url: str) -> Document | None:
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            return Document(_root=parseString(data))
        except HTTPError as e:
            logger.error(f"HTTP error: {e.code} {e.reason}")
        except URLError as e:
            logger.error(f"URL error: {e.reason}")
        return None

    @staticmethod
    def create_element_list(nodes: List[XdmElement]) -> ElementList:
        result = ElementList()
        for node in nodes:
            if isinstance(node, XdmElement):
                result._elements.append(Element(_node=node))
        return result
