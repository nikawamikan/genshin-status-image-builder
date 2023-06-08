from pydantic import BaseModel
from typing import Union


class Status(BaseModel):
    attack: str
    element_charge: str
    critical: str
    critical_per: str
    diffence: str
    element: str
    hp: str


class Icon(BaseModel):
    status: Status
    element: dict[Union[None, str], str]


class Assets(BaseModel):
    artufact_bg: list[str]
    background_base: str
    background_shadow: str
    backgroundo_elements: dict[Union[None, str], str]
    icon: Icon
    star: str
