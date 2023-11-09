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
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # Get the potion_id of the delivered potion based on its type
            sql_statement_potion_id = text("SELECT id FROM potions_inventory WHERE type = :type")
            result_potion_id = connection.execute(sql_statement_potion_id, {"type": potion.potion_type})
            row_potion_id = result_potion_id.first()
            if row_potion_id:
                potion_id = row_potion_id[0]
            else:
                return "Potion type not found in inventory, something went wrong"

            # Update the quantity for the retrieved potion_id
            sql_statement_quantity = text("""
            INSERT INTO potion_ledger_items (potion_id, potion_delta)
            VALUES (:potion_id, :quantity)
            """)
            result_quantity = connection.execute(sql_statement_quantity, {"potion_id": potion_id, "quantity": potion.quantity})

            if not result_quantity.rowcount:
                return "Failed to update potion quantity, something went wrong"

            red_mL, green_mL, blue_mL, dark_mL = potion.potion_type  # Assuming [red, green, blue, dark]

            # Update the ml values in barrel_ledger_items using potion_id
            sql_statement_mL = text(
                """
                INSERT INTO barrel_ledger_items (red_ml_delta, green_ml_delta, blue_ml_delta, dark_ml_delta)
                VALUES (:quantity * :red_mL * -1, :quantity * :green_mL * -1, :quantity * :blue_mL * -1, :quantity * :dark_mL * -1)
                """
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
        sql_statement_potions = text("SELECT SUM(potion_delta) AS potion FROM potion_ledger_items")
        result = connection.execute(sql_statement_potions)
        row = result.first()
        total_potion_count = row[0]        
        
        sql_statement = text("""SELECT SUM(red_ml_delta) FROM barrel_ledger_items""")
        sql_statement2 = text("""SELECT SUM(green_ml_delta) FROM barrel_ledger_items """)        
        sql_statement3 = text("""SELECT SUM(blue_ml_delta) FROM barrel_ledger_items""")        
        sql_statement4 = text("""SELECT SUM(dark_ml_delta) FROM barrel_ledger_items""")
        result = connection.execute(sql_statement)
        row = result.first()
        num_red_ml = row[0]
        
        result2= connection.execute(sql_statement2)
        row2 = result2.first()
        num_green_ml = row2[0]
        
        result3 = connection.execute(sql_statement3)
        row3 = result3.first()
        num_blue_ml = row3[0]
        
        result4 = connection.execute(sql_statement4)
        row4 = result4.first()
        num_dark_ml = row4[0]

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
                        total_potion_count = total_potion_count + 1
                        #print(total_potion_count)

                        # Subtract the used mL from inventory
                        num_red_ml -= red_mL
                        num_green_ml -= green_mL
                        num_blue_ml -= blue_mL
                        num_dark_ml -= dark_mL
                    
                        found_valid_potion = True

                        if total_potion_count > 298:
                            found_valid_potion = False

            if not found_valid_potion:
                break


        return final_bottle_plan