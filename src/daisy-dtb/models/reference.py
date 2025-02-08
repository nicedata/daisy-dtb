from dataclasses import dataclass
from typing import Union


@dataclass
class Reference:
    """This class represents a reference to a fragment in a file."""

    resource: str
    fragment: str

    @staticmethod
    def create_href_or_src(string: str) -> Union["Reference", None]:
        """Create a Reference from a string.

        Example:
        - "dijn0159.smil#mxhp_0001" will return Reference(resource="dijn0159.smil", fragment="mxhp_0001").


        Returns:
            Union[Reference, None]: the Reference.
        """
        if "#" not in string:
            return None
        source, fragment = string.split("#")
        return Reference(source, fragment)
