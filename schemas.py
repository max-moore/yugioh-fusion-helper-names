from typing import List, Union

from pydantic import BaseModel

class CardBase(BaseModel):
    card_name: str
    atk_points: int

class Card(CardBase):
    card_id: int

    class Config:
        orm_mode = True

class FusionBase(BaseModel):
    material_one: int
    material_two: int
    result: int

class Fusion(FusionBase):
    fusion_id: int

    class Config:
        orm_mode = True