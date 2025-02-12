from typing import List
from ..models import Audio
from .base_navigator import BaseNavigator


class ClipNavigator(BaseNavigator):
    def first(self) -> Audio:
        return super().first()

    def next(self) -> Audio:
        return super().next()

    def prev(self) -> Audio:
        return super().prev()

    def last(self) -> Audio:
        return super().last()

    def current(self) -> Audio:
        return super().current()

    def all(self) -> List[Audio]:
        return super().all()

    def navigate_to(self, item_id) -> Audio:
        return super().current()
