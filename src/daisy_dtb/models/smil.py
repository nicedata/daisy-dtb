from dataclasses import dataclass, field
from typing import List

from loguru import logger

from ..utilities.domlib import Document
from .audio import Audio
from .reference import Reference
from .section import Section
from .text import Text
from ..sources.source import DtbSource


@dataclass
class Smil:
    """This class represents a SMIL file."""

    source: DtbSource
    reference: Reference

    # Internal attributes (dynamically populated)
    _title: str = field(init=False, default="")
    _total_duration: float = field(init=False, default=0.0)
    _is_parsed: bool = field(init=False, default=False)
    _sections: List[Section] = field(init=False, default_factory=list)

    def __post_init__(self): ...

    @property
    def title(self) -> str:
        if not self._is_parsed:
            self._parse()
        return self._title

    @property
    def total_duration(self) -> str:
        if not self._is_parsed:
            self._parse()
        return self._total_duration

    @property
    def sections(self) -> List[Section]:
        if not self._is_parsed:
            self._parse()
        return self._sections

    def get_full_text(self) -> str:
        result = []
        if self._is_parsed is False:
            self._parse()
        for par in self._sections:
            result.append(par.text._parse())

        return "\n".join(result)

    def _parse(self) -> None:
        """Load a the SMIL file (if not already loaded) and parse it."""
        if self._is_parsed:
            logger.debug(f"SMIL '{self.reference.resource}' is already loaded.")
            return

        # Get the resource data
        data = self.source.get(self.reference.resource)

        if data is None:
            logger.debug(f"Could not get SMIL '{self.reference.resource}'.")
            return

        if not isinstance(data, Document):
            logger.debug(f"No Document to process ({self.reference.resource}).")
            return

        # Title
        elt = data.get_elements_by_tag_name("meta", {"name": "dc:title"}).first()
        if elt:
            self._title = elt.get_attr("content")
            logger.debug(f"SMIL '{self.reference.resource}' title set : '{self._title}'.")

        # Total duration
        elt = data.get_elements_by_tag_name("meta", {"name": "ncc:timeInThisSmil"}).first()
        if elt:
            duration = elt.get_attr("content")
            h, m, s = duration.split(":")
            self._total_duration = float(h) * 3600 + float(m) * 60 + float(s)
            logger.debug(f"SMIL {self.reference.resource} duration set : {self._total_duration}s.")

        # Process sequences in body
        for body_seq in data.get_elements_by_tag_name("seq", having_parent_tag_name="body").all():
            # Process the <par/> element in the sequence
            for par in body_seq.get_children_by_tag_name("par").all():
                par_id = par.get_attr("id")

                # Handle the <text/>
                text = par.get_children_by_tag_name("text").first()
                id = text.get_attr("id")
                reference = Reference.create_href_or_src(text.get_attr("src"))
                current_text = Text(self.source, id, reference)
                current_par = Section(self.source, par_id, current_text)

                # Handle the <audio/> clip
                for par_seq in par.get_children_by_tag_name("seq").all():
                    for audio in par_seq.get_children_by_tag_name("audio").all():
                        id = audio.get_attr("id")
                        src = audio.get_attr("src")
                        begin = float(audio.get_attr("clip-begin")[4:-1])
                        end = float(audio.get_attr("clip-end")[4:-1])
                        current_par._clips.append(Audio(self.source, id, src, begin, end))
                    logger.debug(f"SMIL {self.reference.resource}, par: {current_par.id} contains {len(current_par._clips)} clip(s).")

                # Add to the list of Parallel
                self._sections.append(current_par)

        self._is_parsed = True
        logger.debug(f"SMIL {self.reference.resource} contains {len(self._sections)} pars.")
        logger.debug(f"SMIL {self.reference.resource} sucessfully loaded.")
