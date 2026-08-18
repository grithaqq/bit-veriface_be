from typing import List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Msg(BaseModel):
    msg: str


class Pagination(BaseModel):
    total_item: int
    total_page: int
    page_size: int
    curr_page: int
    prev_page: int
    next_page: int
    has_prev: bool
    has_next: bool


class BaseListResponse(BaseModel):
    status: int
    message: str
    data: List[T]
    pagination: Pagination


class BaseResponse(BaseModel):
    status: int
    message: str
    data: T
