from operator import and_
from sqlalchemy import and_
from sqlalchemy.orm import Session

import models, schemas

def get_card(db: Session, card_id: int):
    return db.query(models.Card).filter(models.Card.card_id == card_id).first()

def get_fusion(db: Session, fusion_id: int):
    return db.query(models.Fusion).filter(models.Fusion.fusion_id == fusion_id).first()

def fusion_calc(db: Session, user_hand: str):
    card_list = []
    fusion_list = []

    hand_count = 0

    while hand_count < 5:
        user_card = db.query(models.Card).filter(models.Card.card_name == user_hand.split(',')[hand_count]).first()
        card_list.append(user_card.card_id)

        hand_count += 1
    
    hand_count = 1

    while hand_count < 5:
        material_one = card_list[hand_count - 1]
        for card in card_list[hand_count:]:
            material_two = card
            fusion = db.query(models.Fusion.fusion_id).filter(
                and_(models.Fusion.material_one == material_one, models.Fusion.material_two == material_two)).first()
            if fusion and fusion not in fusion_list:
                fusion_list.append(fusion)
        hand_count += 1

    return fusion_list