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
        sql_statement = text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory LIMIT 20")
        result = connection.execute(sql_statement)
        row = result.first()
        num_red = row[0]
        num_green = row[1]
        num_blue = row[2]
        if num_red > 0:
            return [
                {
                    "sku": "RED_POTION_0",  # Basic sku
                    "name": "red potion",  # Basic name
                    "quantity": num_red,  #listing the actual amount of red potions I have
                    "price": 55,  # Price hardcoded at $55.
                    "potion_type": [100, 0, 0, 0],  # Red potion rgb value
                }
            ]
        if num_green > 0:
            return [
                {
                    "sku": "GREEN_POTION_0",  # Basic sku
                    "name": "green potion",  # Basic name
                    "quantity": num_green,  #listing the actual amount of green potions I have
                    "price": 55,  # Price hardcoded at $55.
                    "potion_type": [0, 100, 0, 0],  # green potion rgb value
                }
            ]
        if num_blue > 0:
            return [
                {
                    "sku": "BLUE_POTION_0",  # Basic sku
                    "name": "blue potion",  # Basic name
                    "quantity": num_blue,  #listing the actual amount of green potions I have
                    "price": 55,  # Price hardcoded at $55.
                    "potion_type": [0, 0, 100, 0],  # blue potion rgb value
                }
            ]
        else:
            return [] #no potions of any color available





