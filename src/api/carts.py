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

@router.post("/{cart_id}/items/{item_sku}") #confused by this function! pls review w professor
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

    """
    cart = Cart.retrieve(cart_id)
    with db.engine.begin() as connection:
        sql_statement = text("SELECT quantity FROM potions_inventory")
        result = connection.execute(sql_statement)
        row = result.fetchall()   
        num_red_potions = row[0]
        num_green_potions = row[1]
        num_blue_potions = row[2]
        num_purple_potions = row[3]
        num_yellow_potions = row[4]


        if num_red_potions != 0:
            if item_sku == "RED_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_green_potions != 0:
            if item_sku == "GREEN_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_blue_potions != 0:
            if item_sku == "BLUE_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_purple_potions!= 0:
            if item_sku == "PURPLE_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_yellow_potions!= 0:
            if item_sku == "YELLOW_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        else:
            return {"error. please try again later"}
        
        return "OK"
"""

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    gold_paid = 0
    potions_bought = 0

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """ UPDATE potions_inventory
            SET quantity = potions_inventory.quantity - cart_items.quantity
            FROM cart_items
            WHERE potions_inventory.id = cart_items.id and cart_items.cart_id = :cart_id;"""),
            [{"cart_id": cart_id}])
        
        result = connection.execute(sqlalchemy.text("SELECT SUM(potions_inventory.price * cart_items.quantity)\
                                    AS gold_paid, SUM(cart_items.quantity) AS potions_bought FROM potions_inventory\
                                    JOIN cart_items ON potions_inventory.id = cart_items.id WHERE cart_items.cart_id = :cart_id"),
                                    [{"cart_id": cart_id}])
    
        row = result.first()
        gold_paid = row.gold_paid
        potions_bought = row.potions_bought

        connection.execute(sqlalchemy.text("""
            UPDATE global_inventory
            SET gold = gold + :gold_paid,
            total_potions = total_potions - :potions_bought
            """ ),
            {"gold_paid": gold_paid, "potions_bought": potions_bought})

    return {"total_potions_bought": potions_bought, "gold_paid": gold_paid}


"""
    cart = Cart.retrieve(cart_id)
    quantity = 0
    if cart:
        if cart.get_cart_items():
            #print(cart.items)
            with db.engine.begin() as connection:
                if "RED_POTION_0" in cart.items:
                    red_potion_quantity = cart.items["RED_POTION_0"]
                    sql_statement = text("UPDATE potions_inventory SET quantity = quantity - :item_count_red WHERE sku = :sku")
                    quantity += red_potion_quantity
                    result = connection.execute(sql_statement, {"sku": "RED_POTION_0", "item_count_red": cart.items["RED_POTION_0"]})

                if "GREEN_POTION_0" in cart.items:
                    green_potion_quantity = cart.items["GREEN_POTION_0"]
                    sql_statement2 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_green WHERE sku = :sku")
                    quantity += green_potion_quantity
                    result2 = connection.execute(sql_statement2, {"sku": "GREEN_POTION_0", "item_count_green": cart.items["GREEN_POTION_0"]})
            
                if "BLUE_POTION_0" in cart.items:
                    blue_potion_quantity = cart.items["BLUE_POTION_0"]
                    sql_statement3 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_blue WHERE sku = :sku")
                    quantity += blue_potion_quantity
                    result3 = connection.execute(sql_statement3, {"sku": "BLUE_POTION_0", "item_count_blue": cart.items["BLUE_POTION_0"]})
                
                if "PURPLE_POTION_0" in cart.items:
                    purple_potion_quantity = cart.items["PURPLE_POTION_0"]
                    sql_statement4 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_purple WHERE sku = :sku")
                    quantity += purple_potion_quantity
                    result3 = connection.execute(sql_statement4, {"sku": "PURPLE_POTION_0", "item_count_purple": cart.items["PURPLE_POTION_0"]})

                if "YELLOW_POTION_0" in cart.items:
                    yellow_potion_quantity = cart.items["YELLOW_POTION_0"]
                    sql_statement5 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_yellow WHERE sku = :sku")
                    quantity += yellow_potion_quantity
                    result3 = connection.execute(sql_statement5, {"sku": "YELLOW_POTION_0", "item_count_yellow": cart.items["YELLOW_POTION_0"]})
            

                sql_statement_gold = text("UPDATE global_inventory SET gold = gold + :gold_amount")
                gold_amount = quantity * 55
                result_gold = connection.execute(sql_statement_gold, {"gold_amount": gold_amount})
                
                return { "total_potions_bought": quantity, "total_gold_paid": gold_amount }
       
        else:
            return { "total_potions_bought": 0, "total_gold_paid": 0 }
    return {"Error. Cart not found"}
    """