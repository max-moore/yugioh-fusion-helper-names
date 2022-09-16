from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Card(Base):
    __tablename__ = "scraped_card_list"

    card_id = Column(Integer, primary_key=True, index=True)
    card_name = Column(String, unique=True)
    atk_points = Column(Integer)

class Fusion(Base):
    __tablename__ = "fusion_list"

    fusion_id = Column(Integer, primary_key=True, index=True)
    material_one = Column(Integer)
    material_two = Column(Integer)
    result = Column(Integer)