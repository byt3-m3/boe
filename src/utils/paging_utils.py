from dataclasses import dataclass
from typing import Any


@dataclass
class PaginationPage:
    cursor: Any
    next_page: int
    current_page: int
    item_count: int

    def __iter__(self):
        return self.cursor


@dataclass
class NewPage:
    cursor: Any
    last_id: str
    total_items: int

    def __iter__(self):
        return self.cursor


class Paginator:
    def __init__(self):
        self._page_map = {}
        self._page_list = []

        self._active_page = None
        self._total_pages = None
        self.total_records = 0

    def add_page(self, page: PaginationPage):
        self._page_map[page.current_page] = page
        self._page_list.append(page)

    def get_page(self, page_number) -> NewPage:
        self._active_page = self._page_map.get(page_number)
        return self._active_page

    @property
    def pages(self):
        return self._page_list

    @property
    def page_count(self):
        return len(self._page_map.keys())

    def __iter__(self):
        _i = iter(self._page_list)
        for i in _i:
            yield i.cursor

    def paginate(self):
        cur_page = 0
        total_pages = 10
        while cur_page <= total_pages:
            pass
