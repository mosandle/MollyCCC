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
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            sql_statement = text("UPDATE global_inventory SET gold = gold - (:price * :quantity)")
            sql_statement2 = text("UPDATE global_inventory SET num_red_ml = num_red_ml + (:ml_per_barrel * :quantity)")
            sql_statement3 = text("UPDATE global_inventory SET num_green_ml = num_green_ml + (:ml_per_barrel * :quantity)")
            sql_statement4 = text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + (:ml_per_barrel * :quantity)")


            if barrel.potion_type == [1, 0, 0, 0]:
                result2 = connection.execute(sql_statement2, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})
            if barrel.potion_type == [0, 1, 0, 0]:
                result3 = connection.execute(sql_statement3, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})
            if barrel.potion_type == [0, 1, 0, 0]:
                result4 = connection.execute(sql_statement4, {"ml_per_barrel": barrel.ml_per_barrel, "quantity": barrel.quantity})
            
            result = connection.execute(sql_statement, {"price": barrel.price, "quantity": barrel.quantity})

        return "OK"
        
    print(barrels_delivered)    

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

#get my amount of gold
#get the amount of potions i have in each color
#if i have the least amount of red, i will buy red barrels
#same for other colors

    with db.engine.begin() as connection:
        sql_statement = text("SELECT gold, num_red_potions, num_green_potions, num_blue_potions FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()  
        
        gold_count = row[0] 
        num_red_potions = row[1]
        num_green_potions = row[2]
        num_blue_potions = row[3]
        final_purchase_plan = []
        
        if num_red_potions < 1:
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
                        gold_count = gold_count - (barrel.price * barrel.quantity)
                        print(gold_count)

        """         
        #if we have the least amount of green potions in our inventory comparably
               elif num_green_potions <= num_red_potions and num_green_potions <= num_blue_potions:
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
                        gold_count = gold_count - barrel.price"""
        if num_green_potions < 1:
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
                        gold_count = gold_count -  (barrel.price * barrel.quantity)


        #defaulting to blue if same amount of mL, so will probably end up with hella blue potions
        if num_blue_potions < 3:
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
                        gold_count = gold_count -  (barrel.price * barrel.quantity)

        return final_purchase_plan


        