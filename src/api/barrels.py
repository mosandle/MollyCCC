from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int

@router.post("/deliver") #only modify in deliver
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
    #only need to modify for one small red barrel bc thats the maximum that can be purchased at once. 

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            sql_statement = text("UPDATE global_inventory SET gold = gold - :price")
            sql_statement2 = text("UPDATE global_inventory SET num_red_ml = num_red_ml + (:ml_per_barrel * :quantity)")
            sql_statement3 = text("UPDATE global_inventory SET num_green_ml = num_green_ml + (:ml_per_barrel * :quantity)")
            sql_statement4 = text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + (:ml_per_barrel * :quantity)")


            if barrel.potion_type == [1, 0, 0, 0]:
                result2 = connection.execute(sql_statement2, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})
            if barrel.potion_type == [0, 1, 0, 0]:
                result3 = connection.execute(sql_statement3, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})
            if barrel.potion_type == [0, 1, 0, 0]:
                result4 = connection.execute(sql_statement4, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})

            result = connection.execute(sql_statement, {"price": barrel.price})

        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    #get my amount of gold
    #if my amount of gold is greater than the cost of one barrel, and i havee less than 10 potions, 
    #then i will buy one barrel
    #otherwise, i will buy 0

    with db.engine.begin() as connection:
        sql_statement = text("SELECT gold, num_red_potions, num_green_potions, num_blue_potions FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()  
        
        gold_count = row[0] 
        num_red_potions = row[1]
        num_green_potions = row[2]
        num_blue_potions = row[3]

        final_purchase_plan = []
        
        #if we have the least amount of red potions in our inventory comparably
        if num_red_potions < num_green_potions and num_red_potions < num_blue_potions:
            for barrel in wholesale_catalog:
                if gold_count >= (barrel.price * barrel.quantity):
                    if barrel.potion_type == [1, 0, 0, 0]:
                        final_purchase_plan.append({
                                    "sku": barrel.sku,
                                    "quantity": barrel.quantity,
                                    "ml_per_barrel": barrel.ml_per_barrel,
                                    "potion_type": barrel.potion_type,
                                    "price": barrel.price
                                })

                        gold_count = gold_count - barrel.price

        #if we have the least amount of green potions in our inventory comparably
        if num_green_potions < num_red_potions and num_green_potions < num_blue_potions:
            for barrel in wholesale_catalog:
                if gold_count >= (barrel.price * barrel.quantity):
                    if barrel.potion_type == [0, 1, 0, 0]:
                        final_purchase_plan.append({
                                    "sku": barrel.sku,
                                    "quantity": barrel.quantity,
                                    "ml_per_barrel": barrel.ml_per_barrel,
                                    "potion_type": barrel.potion_type,
                                    "price": barrel.price
                                })
                        gold_count = gold_count - barrel.price

        #defaulting to blue if same amount of mL, so will probably end up with hella blue potions
        else:
            for barrel in wholesale_catalog:
                if gold_count >= (barrel.price * barrel.quantity):
                    if barrel.potion_type == [0, 0, 1, 0]:
                        final_purchase_plan.append({
                                    "sku": barrel.sku,
                                    "quantity": barrel.quantity,
                                    "ml_per_barrel": barrel.ml_per_barrel,
                                    "potion_type": barrel.potion_type,
                                    "price": barrel.price
                                })
                        gold_count = gold_count - barrel.price

        return final_purchase_plan


        