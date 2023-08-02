from pydantic import BaseModel
from model.util_model import Position


class CharacterPosition(BaseModel):
    id: str
    name: str
    costume_id: str
    costume_icon_url: str
    english_name: str
    position: Position
