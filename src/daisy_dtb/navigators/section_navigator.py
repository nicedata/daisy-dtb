from typing import List
from ..models import Section
from .base_navigator import BaseNavigator


class SectionNavigator(BaseNavigator):
    def first(self) -> Section:
        return super().first()

    def last(self) -> Section:
        return super().last()

    def next(self) -> Section:
        return super().next()

    def prev(self) -> Section:
        return super().prev()

    def current(self) -> Section:
        return super().current()

    def all(self) -> List[Section]:
        return super().all()

    def navigate_to(self, item_id) -> Section:
        return super().current()
