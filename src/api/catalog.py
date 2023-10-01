from fastapi import APIRouter
import sqlalchemy
from sqlalchemy import *
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"]) #endpoint one
def get_catalog():

    """
    Each unique item combination must have only a single price.
    """
    # Can return a max of 20 items.
    #currently lists one single red potion no matter the quantity, if 0 in possession lists 0
    
    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_potions FROM global_inventory LIMIT 20")
        result = connection.execute(sql_statement)
        row = result.first()
        if row[0] > 0:
            return [
                {
                    "sku": "RED_POTION_0",  # Basic sku
                    "name": "red potion",  # Basic name
                    "quantity": 1,  # Will only ever list one red potion for $50 right now
                    "price": 50,  # Price hardcoded at $50.
                    "potion_type": [100, 0, 0, 0],  # Red potion rgb value
                }
            ]
        else:
            return [
                {
                    "sku": "RED_POTION_0",  # Basic sku
                    "name": "red potion",  # Basic name
                    "quantity": 0,  # 0 potions if we have 0 available
                    "price": 50,  # Price hardcoded at 50.
                    "potion_type": [100, 0, 0, 0],  # Red potion rgb value
                }
            ]





