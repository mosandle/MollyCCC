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
            sql_statement2 = text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml_per_barrel")
            sql_statement3 = text("UPDATE global_inventory SET num_red_potions = num_red_potions + (:ml_per_barrel / 100)")

            result = connection.execute(sql_statement, {"price": barrel.price})
            result2 = connection.execute(sql_statement2, {"ml_per_barrel": barrel.ml_per_barrel})
            result3 = connection.execute(sql_statement3, {"ml_per_barrel": barrel.ml_per_barrel})

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

    amount_bought = len(wholesale_catalog) #length of list aka how many barrels are available to buy
    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_potions FROM global_inventory")
        sql_statement2 = text("SELECT gold FROM global_inventory")
        
        result = connection.execute(sql_statement)
        row = result.first()      
        if row[0] < 10:
            result2 = connection.execute(sql_statement2)
            for barrel in wholesale_catalog:
                row2 = result2.first()
                if row2[0] >= barrel.price:
                    return [
                                {
                                    "sku": "SMALL_RED_BARREL",
                                    "quantity": 1,
                                }            
                            ]
        return "OK"


        