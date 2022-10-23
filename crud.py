from typing import List
from operator import and_
from sqlalchemy import and_
from sqlalchemy.orm import Session

import models, schemas

def get_card(db: Session, card_id: int):
    return db.query(models.Card).filter(models.Card.card_id == card_id).first()

def get_fusion(db: Session, fusion_id: int):
    return db.query(models.Fusion).filter(models.Fusion.fusion_id == fusion_id).first()

def fusion_calc(db: Session, user_hand: List[int]):
    fusion_list = []
    
    hand_count = 1

    while hand_count < len(user_hand):
        material_one = user_hand[hand_count - 1]
        for card in user_hand[hand_count:]:
            material_two = card
            fusion = db.query(models.Fusion.fusion_id).filter(
                and_(models.Fusion.material_one == material_one, models.Fusion.material_two == material_two)).first()
            if fusion and fusion not in fusion_list:
                fusion_list.append(fusion)
        hand_count += 1

    return fusion_list