from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from src import database as db

    #plan is a vision, doesnt actually change anything
    #his system calls the plan, and then as long as the plan is actually feasible then deliver gets called. 

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            sql_statement = text("UPDATE global_inventory SET num_red_potions = num_red_potions + :quantity")
            sql_statement2 = text("UPDATE global_inventory SET num_red_ml = num_red_ml - (:quantity * 100)")
            result = connection.execute(sql_statement, {"quantity": potion.quantity})
            result2 = connection.execute(sql_statement2, {"quantity": potion.quantity})


    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_potions, num_red_ml FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()   
        num_red_potions = row[0]
        num_red_ml = row[1]
        if num_red_ml != 0:
            if num_red_ml % 100 == 0:
                    return [
                        {
                            "potion_type": [100, 0, 0, 0],
                            "quantity": (num_red_ml / 100),
                        }
                ]
        return []
