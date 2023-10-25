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
            sql_statement = text("SELECT SUM(potion_delta) AS potion FROM potion_ledger_items")
            result = connection.execute(sql_statement)
            row = result.first()
            total_potion_count = row[0]

            sql_statement2 = text("SELECT SUM(red_ml_delta) + SUM(green_ml_delta) + SUM(blue_ml_delta) + SUM(dark_ml_delta) AS mills FROM barrel_ledger_items")
            result2 = connection.execute(sql_statement2)
            row2 = result2.first()
            total_ml_count = row2[0]

            sql_statement3 = text("SELECT SUM(gold_delta) AS gold FROM gold_ledger_items")
            result3 = connection.execute(sql_statement3)
            row3 = result3.first()
            total_gold_count = row3[0]

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
