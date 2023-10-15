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
        for row in rows:
            total_potion_count += row
        
        sql_statement = text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory")
        result = connection.execute(sql_statement)
        rows = result.fetchall()
        red = rows[0]
        green = rows[1]
        blue = rows[2]
        total_ml_count = red + green + blue

        sql_statement = text("SELECT gold FROM global_inventory")
        result = connection.execute(sql_statement)
        rows = result.fetchall()
        gold = rows[0]
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
