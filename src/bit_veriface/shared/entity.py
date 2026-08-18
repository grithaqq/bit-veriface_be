from dataclasses import dataclass, field
from typing import List, TypeVar

T = TypeVar("T")


@dataclass
class Msg:
    msg: str = field(default=None)


@dataclass
class Pagination:
    total_item: int = field(default=None)
    total_page: int = field(default=None)
    page_size: int = field(default=None)
    curr_page: int = field(default=None)
    prev_page: int = field(default=None)
    next_page: int = field(default=None)
    has_prev: bool = field(default=None)
    has_next: bool = field(default=None)


@dataclass
class BaseListResponse:
    status: int = field(default=None)
    message: str = field(default=None)
    data: List[T] = field(default=None)
    pagination: Pagination = field(default=None)


@dataclass
class BaseResponse:
    status: int = field(default=None)
    message: str = field(default=None)
    data: T = field(default=None)
