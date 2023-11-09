from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
import json
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
    print(barrels_delivered)
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            # Define the SQL statement with dynamic columns
            sql_statement = text("""
                INSERT INTO barrel_ledger_items (red_ml_delta, green_ml_delta, blue_ml_delta, dark_ml_delta)
                VALUES (
                    CASE WHEN :potion_type = ARRAY[1, 0, 0, 0] THEN :ml_per_barrel * :quantity ELSE 0 END,
                    CASE WHEN :potion_type = ARRAY[0, 1, 0, 0] THEN :ml_per_barrel * :quantity ELSE 0 END,
                    CASE WHEN :potion_type = ARRAY[0, 0, 1, 0] THEN :ml_per_barrel * :quantity ELSE 0 END,
                    CASE WHEN :potion_type = ARRAY[0, 0, 0, 1] THEN :ml_per_barrel * :quantity ELSE 0 END
                )
            """)

            # Execute the statement with the appropriate parameters
            result = connection.execute(sql_statement, {
                "ml_per_barrel": barrel.ml_per_barrel,
                "quantity": barrel.quantity,
                "potion_type": barrel.potion_type
            })

            # Handle other operations, if necessary
            # For example, inserting values into gold_ledger_items
            sql_statement_gold = text("INSERT INTO gold_ledger_items (gold_delta) VALUES (:price * :quantity * -1)")
            #print(barrel.quantity)
            
            #print(barrel.price)
            result_gold = connection.execute(sql_statement_gold, {"price": barrel.price, "quantity": barrel.quantity})

        return "OK"



# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    return []
    with db.engine.begin() as connection:
        sql_statement = text("SELECT SUM(gold_delta) AS gold FROM gold_ledger_items")
        result = connection.execute(sql_statement)
        row = result.first()
        gold_count = row[0] #gets my current gold count.

        final_purchase_plan = []

        # Loop through barrels in the catalog
        for barrel in wholesale_catalog:
            modified_list = [100 if x == 1 else x for x in barrel.potion_type]
            barrel.potion_type = modified_list


            # Get the ID of the potion in potion_ledger_items based on the potion_type
            sql_get_potion_id = text("SELECT id FROM potions_inventory WHERE type = :type")
            result_get_potion_id = connection.execute(sql_get_potion_id, {"type": modified_list})
            potion_id = result_get_potion_id.scalar()

            if potion_id is not None:
                # Calculate the sum of potion_delta for the specific potion type
                sql_statement2 = text("SELECT SUM(potion_delta) FROM potion_ledger_items WHERE potion_id = :potion_id")
                result2 = connection.execute(sql_statement2, {"potion_id": potion_id})
                quantity = result2.scalar()
                #print(gold_count)

            # Determine if you need to purchase this barrel
            needed_num = gold_count - (barrel.price * barrel.quantity)
            if quantity < 100 and needed_num >= 8000:
                final_purchase_plan.append({
                    "sku": barrel.sku,
                    "quantity": barrel.quantity,
                    "ml_per_barrel": barrel.ml_per_barrel,
                    "potion_type": barrel.potion_type, 
                    "price": barrel.price,
                })
                gold_count = gold_count - (barrel.price * barrel.quantity)
    print(final_purchase_plan)

    return final_purchase_plan