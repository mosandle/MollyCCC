from fastapi import APIRouter
import sqlalchemy
from sqlalchemy import *
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    """
    Each unique item combination must have only a single price.
    """
    # Can return a max of 6 items. (currently returning 3)
    #should be listing all available potions of red, green, and blue
    
    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()
        num_red = row[0]
        num_green = row[1]
        num_blue = row[2]
        final_catalog = []
        if num_red > 0:
                final_catalog.append ({
                    "sku": "RED_POTION_0",  # Basic sku
                    "name": "red potion",  # Basic name
                    "quantity": num_red,  #listing the actual amount of red potions I have
                    "price": 55,  # Price hardcoded at $40.
                    "potion_type": [100, 0, 0, 0],  # Red potion rgb value
                }
                )
        if num_green > 0:
            final_catalog.append (
                {
                    "sku": "GREEN_POTION_0",  # Basic sku
                    "name": "green potion",  # Basic name
                    "quantity": num_green,  #listing the actual amount of green potions I have
                    "price": 55,  # Price hardcoded at $40.
                    "potion_type": [0, 100, 0, 0],  # green potion rgb value
                }
                )
        if num_blue > 0:
            final_catalog.append (
                {
                    "sku": "BLUE_POTION_0",  # Basic sku
                    "name": "blue potion",  # Basic name
                    "quantity": num_blue,  #listing the actual amount of blue potions I have
                    "price": 55,  # Price hardcoded at $40.
                    "potion_type": [0, 0, 100, 0],  # blue potion rgb value
                }
            )
    return final_catalog





