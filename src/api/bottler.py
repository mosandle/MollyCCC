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
            if potion.potion_type == [100, 0, 0, 0]: #red potions
                sql_statement = text("UPDATE global_inventory SET num_red_potions = num_red_potions + :quantity")
                sql_statement2 = text("UPDATE global_inventory SET num_red_ml = num_red_ml - (:quantity * 100)")
                result = connection.execute(sql_statement, {"quantity": potion.quantity})
                result2 = connection.execute(sql_statement2, {"quantity": potion.quantity})
            
            elif potion.potion_type == [0, 100, 0, 0]: #green potions
                sql_statement = text("UPDATE global_inventory SET num_green_potions = num_green_potions + :quantity")
                sql_statement2 = text("UPDATE global_inventory SET num_green_ml = num_green_ml - (:quantity * 100)")
                result = connection.execute(sql_statement, {"quantity": potion.quantity})
                result2 = connection.execute(sql_statement2, {"quantity": potion.quantity})

            elif potion.potion_type == [0, 0, 100, 0]: #blue potions
                sql_statement = text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :quantity")
                sql_statement2 = text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - (:quantity * 100)")
                result = connection.execute(sql_statement, {"quantity": potion.quantity})
                result2 = connection.execute(sql_statement2, {"quantity": potion.quantity})
            else:
                 return "something is wrong"

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
        #only bottles if there is an amount of mL divisible by 100 available, otherwise waits
        sql_statement = text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()   
        num_red_ml = row[0]
        num_green_ml = row[1]
        num_blue_ml = row[2]

        final_bottler_plan = []
        
        if num_red_ml != 0:
            if num_red_ml % 100 == 0:
                    final_bottler_plan.append(
                        {
                            "potion_type": [100, 0, 0, 0],
                            "quantity": int(num_red_ml / 100),
                        })
                    
        if num_green_ml != 0:
            if num_green_ml % 100 == 0:
                    final_bottler_plan.append(
                        {
                            "potion_type": [0, 100, 0, 0],
                            "quantity": int(num_green_ml / 100),
                        })
                    
        if num_blue_ml != 0:
            if num_blue_ml % 100 == 0:
                    final_bottler_plan.append(
                        {
                            "potion_type": [0, 0, 100, 0],
                            "quantity": int(num_blue_ml / 100),
                        })
        return final_bottler_plan
