import datetime

from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    user_id: int
    tag: str
    devices: list[int]
    device_counter: int
    active: bool
    create_time: datetime.datetime


class UserUpdate(BaseModel):
    active: Optional[bool] = None
    devices: Optional[list[int]] = None
    device_counter: Optional[list[int]] = None


class UserCreate(BaseModel):
    user_id: int
    tag: str
    create_time: datetime.datetime
