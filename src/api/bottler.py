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
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # Get the SKU of the delivered potion based on its type
            sql_statement_sku = text("SELECT sku FROM potions_inventory WHERE type = :type")
            result_sku = connection.execute(sql_statement_sku, {"type": potion.potion_type})
            row_sku = result_sku.first()
            if row_sku:
                sku = row_sku[0]
            else:
                return "Potion type not found in inventory, something went wrong"

            # Update the quantity for the retrieved SKU
            sql_statement_quantity = text("UPDATE potions_inventory SET quantity = quantity + :quantity WHERE sku = :sku")
            result_quantity = connection.execute(sql_statement_quantity, {"sku": sku, "quantity": potion.quantity})

            if not result_quantity.rowcount:
                return "Failed to update potion quantity, something went wrong"

            red_mL, green_mL, blue_mL, dark_mL = potion.potion_type  # Assuming [red, green, blue, dark]

            sql_statement_mL = text(
                "UPDATE global_inventory "
                "SET num_red_ml = num_red_ml - (:quantity * :red_mL), "
                "num_green_ml = num_green_ml - (:quantity * :green_mL), "
                "num_blue_ml = num_blue_ml - (:quantity * :blue_mL), "
                "num_dark_ml = num_dark_ml - (:quantity * :dark_mL) "
                "WHERE :quantity > 0"
            )
            result_mL = connection.execute(
                sql_statement_mL,
                {
                    "quantity": potion.quantity,
                    "red_mL": red_mL,
                    "green_mL": green_mL,
                    "blue_mL": blue_mL,
                    "dark_mL": dark_mL,
                },
            )
            if not result_mL.rowcount:
                return "Failed to update inventory ml, something went wrong"

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
            """
    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()
        num_red_ml = row[0]
        num_green_ml = row[1]
        num_blue_ml = row[2]
        num_dark_ml = row[3]

        final_bottle_plan = []

        sql_statement2 = text("SELECT type FROM potions_inventory ORDER by quantity")
        result = connection.execute(sql_statement2)
        rows = result.fetchall()

        while True:
            found_valid_potion = False
            for potion_type in rows:
                red_mL, green_mL, blue_mL, dark_mL = potion_type[0]

                if red_mL <= num_red_ml and green_mL <= num_green_ml and blue_mL <= num_blue_ml and dark_mL <= num_dark_ml:
                    if red_mL + blue_mL + green_mL + dark_mL != 100:
                        return "error occurred, improper mixing proportions"
                    else:
                        potion_entry = {
                            "potion_type": [red_mL, green_mL, blue_mL, dark_mL],
                            "quantity": 1,
                        }

                        final_bottle_plan.append(potion_entry)
                        # Subtract the used mL from inventory
                        num_red_ml -= red_mL
                        num_green_ml -= green_mL
                        num_blue_ml -= blue_mL
                        num_dark_ml -= dark_mL

                        found_valid_potion = True

            if not found_valid_potion:
                break

        return final_bottle_plan