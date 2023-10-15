from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db
from sqlalchemy import *
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """"""
    total_potion_count = 0
    total_ml_count = 0
    total_gold_count = 0

    with db.engine.begin() as connection:
        sql_statement = text("SELECT quantity FROM potions_inventory")
        result = connection.execute(sql_statement)
        rows = result.fetchall()
        print(rows)
        for row in rows:
            total_potion_count += row[0]  # Access the actual value

        sql_statement = text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()
        num_red_ml = row[0]
        num_green_ml = row[1]
        num_blue_ml = row[2]
        total_ml_count = num_red_ml + num_green_ml + num_blue_ml

        sql_statement3 = text("SELECT gold FROM global_inventory")
        result3 = connection.execute(sql_statement3)
        rows3 = result3.first()
        gold = rows3[0]  # Unpack the value directly
        total_gold_count = gold

    return {"number_of_potions": total_potion_count, "ml_in_barrels": total_ml_count, "gold": total_gold_count}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
