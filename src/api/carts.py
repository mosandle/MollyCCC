from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from sqlalchemy import *
from ..models.Cart import Cart
from ..models.Cart import NewCart
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    customer: str

@router.post("/") #works
def create_cart(new_cart: NewCart):
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                INSERT INTO carts (customer_name) VALUES 
                                (:customer_name)
                                RETURNING cart_id
                                """),
                                  ({"customer_name": new_cart.customer}))
    cart_id = result.scalar()
    return {"cart_id": cart_id}


@router.get("/{cart_id}") #does not get used so can ignore?
def get_cart(cart_id: int):
    """ """
    return {}

class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}") 
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
                    INSERT INTO cart_items (cart_id, quantity, id) 
                    SELECT :cart_id, :quantity, id
                    FROM potions_inventory WHERE potions_inventory.sku = :item_sku """),
                    [{"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku}])
        #print("current cart:" item_sku, "current items:", cart_item.quantity)
    return "OK"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    gold_paid = 0
    potions_bought = 0

    with db.engine.begin() as connection:
        stuff = connection.execute(sqlalchemy.text(
            """
            SELECT id, quantity 
            FROM cart_items
            WHERE cart_items.cart_id = :cart_id
            """), 
            [{"cart_id": cart_id}])
        
        for row in stuff:
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO potion_ledger_items (potion_delta, potion_id) 
            VALUES (:potion_delta, :potion_id)
            """), 
            [{"potion_delta": -row.quantity, "potion_id": row.id}])
        
        result = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(potions_inventory.price * cart_items.quantity) AS gold_paid,
            SUM(cart_items.quantity) AS potions_bought 
            FROM cart_items

            JOIN potions_inventory ON cart_items.id = potions_inventory.id 
            WHERE cart_items.cart_id = :cart_id;

            """),
            [{"cart_id": cart_id}])
    
        row = result.first()
        gold_paid = row.gold_paid
        potions_bought = row.potions_bought

        connection.execute(sqlalchemy.text("""
            INSERT INTO gold_ledger_items (gold_delta) VALUES (:gold_paid)
            """ ),
            [{"gold_paid": gold_paid}])

    return {"total_potions_bought": potions_bought, "gold_paid": gold_paid}