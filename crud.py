from typing import List
from operator import and_
from sqlalchemy import and_
from sqlalchemy.orm import Session

import models, schemas

# function that takes a card id as input and returns the card object from the scraped_card_list table
def get_card(db: Session, card_id: int):
    return db.query(models.Card).filter(models.Card.card_id == card_id).first()

# function that takes a card id as input and returns the fusion object from the fusion_list table
def get_fusion(db: Session, fusion_id: int):
    return db.query(models.Fusion).filter(models.Fusion.fusion_id == fusion_id).first()

# function that takes a list of up to 5 card ids, and returns all possible fusions as fusion ids from the fusion_list table
def fusion_calc(db: Session, user_hand: List[int]):
    fusion_list = []
    # hand_count selects the current card in hand
    hand_count = 1
    # while we're not selecting the last card in our hand...
    while hand_count < len(user_hand):
        # our first material is our currently selected card
        material_one = user_hand[hand_count - 1]
        # and for each subsequent card in our hand...
        for card in user_hand[hand_count:]:
            # search for fusions!
            material_two = card
            fusion = db.query(models.Fusion.fusion_id).filter(
                and_(models.Fusion.material_one == material_one, models.Fusion.material_two == material_two)).first()
            # if we find a fusion and it isn't already in our list...
            if fusion and fusion not in fusion_list:
                # then add it to our list
                fusion_list.append(fusion)
        # select the next card in hand for our first material
        hand_count += 1
    # return our full list of fusions
    return fusion_list