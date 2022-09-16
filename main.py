# Yu-Gi-Oh! Forbidden Memories Fusion Helper (PlayStation 1)
# Based on https://yugipedia.com data
# Ignacio Rodriguez Abraham (nacho.rodriguez.a@gmail.com)
# Edited and updated by Maxwell Moore-Billings (maxwell.moorebillings@gmail.com)

from gc import get_debug
import os, sys, requests
from bs4 import BeautifulSoup
from fastapi import Query

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title='Yu-Gi-Oh Fusion Finder API',
    docs_url='/'
)

@app.get("/testcard", response_model=schemas.Card)
async def test_card(card_id: int, db: Session = Depends(get_db)):
    db_card = crud.get_card(db, card_id=card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return db_card

@app.get("/testfusion", response_model=schemas.Fusion)
async def test_fusion(fusion_id: int, db: Session = Depends(get_db)):
    db_fusion = crud.get_fusion(db, fusion_id=fusion_id)
    if db_fusion is None:
        raise HTTPException(status_code=404, detail="Fusion not found")
    return db_fusion

@app.get("/testfusionlist")
async def test_fusionlist(user_hand: str, db: Session = Depends(get_db)):
    db_fusionlist = crud.fusion_calc(db, user_hand=user_hand)
    if db_fusionlist is None and db_fusionlist != []:
        raise HTTPException(status_code=404, detail="Fusion list not found")
    return db_fusionlist