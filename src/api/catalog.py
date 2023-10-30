from fastapi import APIRouter
import sqlalchemy
from sqlalchemy import *
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():

    """
    Each unique item combination must have only a single price.
    """
    # Can return a max of 6 items.
    
    with db.engine.begin() as connection:
        #need sku, name, quantity, price, type          
        sql_statement = text("""
                                SELECT sku, name, SUM(potion_ledger_items.potion_delta) AS quantity, type, price
                                FROM potions_inventory
                                JOIN potion_ledger_items ON potions_inventory.id = potion_ledger_items.potion_id
                                GROUP BY potions_inventory.id
                                HAVING SUM(potion_ledger_items.potion_delta) > 0
                                LIMIT 6""")
                             
        result = connection.execute(sql_statement)
        rows = result.fetchall()
        final_catalog = []
        
        for row in rows:
            sku, name, quantity, type, price, = row
            catalog_entry = {
                "sku": sku,
                "name": name,
                "quantity": quantity,
                "price": price,
                "potion_type": type
                }
            final_catalog.append(catalog_entry)
    return final_catalog




