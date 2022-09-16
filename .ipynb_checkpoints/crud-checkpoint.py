from sqlalchemy.orm import Session

import models, schemas

def get_card(db: Session, card_id: list):
    return db.query(models.Card).filter(models.Card.card_id == card_id[0]).first()

def get_fusion(db: Session, fusion_id: list):
    return db.query(models.Fusion).filter(models.Fusion.fusion_id == fusion_id[0]).first()