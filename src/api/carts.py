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

@router.post("/")
def create_cart(new_cart: NewCart):
    newCart = Cart(new_cart)
    return {"cart_id": newCart.id} 


@router.get("/{cart_id}") #does not get used so can ignore?
def get_cart(cart_id: int):
    """ """
    return {}

class CartItem(BaseModel):
    quantity: int

#prices dictionary
ITEM_PRICES = {
    "RED_POTION_0": 40,
    "GREEN_POTION_0": 40,
    "BLUE_POTION_0": 40,
}

@router.post("/{cart_id}/items/{item_sku}") #confused by this function! pls review w professor
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cart = Cart.retrieve(cart_id)
    with db.engine.begin() as connection:
        sql_statement = text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory")
        result = connection.execute(sql_statement)
        row = result.first()   
        num_red_potions = row[0]
        num_green_potions = row[1]
        num_blue_potions = row[2]

        if num_red_potions != 0:
            if item_sku == "RED_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_green_potions != 0:
            if item_sku == "GREEN_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_blue_potions != 0:
            if item_sku == "BLUE_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        else:
            return {"error. please try again later"}
        
        return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    cart = Cart.retrieve(cart_id)
    quantity = 0
    if cart:
        if cart.get_cart_items():
            #print(cart.items)
            with db.engine.begin() as connection:
                if "RED_POTION_0" in cart.items:
                    red_potion_quantity = cart.items["RED_POTION_0"]
                    sql_statement = text("UPDATE global_inventory SET num_red_potions = num_red_potions - :item_count_red")
                    quantity += red_potion_quantity
                    result = connection.execute(sql_statement, {"item_count_red": cart.items["RED_POTION_0"]})

                if "GREEN_POTION_0" in cart.items:
                    green_potion_quantity = cart.items["GREEN_POTION_0"]
                    sql_statement2 = text("UPDATE global_inventory SET num_green_potions = num_green_potions - :item_count_green")
                    quantity += green_potion_quantity
                    result2 = connection.execute(sql_statement2, {"item_count_green": cart.items["GREEN_POTION_0"]})
                   

                if "BLUE_POTION_0" in cart.items:
                    blue_potion_quantity = cart.items["BLUE_POTION_0"]
                    sql_statement3 = text("UPDATE global_inventory SET num_blue_potions = num_blue_potions - :item_count_blue")
                    quantity += blue_potion_quantity
                    result3 = connection.execute(sql_statement3, {"item_count_blue": cart.items["BLUE_POTION_0"]})
            

                sql_statement_gold = text("UPDATE global_inventory SET gold = gold + :gold_amount")
                gold_amount = quantity * 40
                result_gold = connection.execute(sql_statement_gold, {"gold_amount": gold_amount})
                
                return { "total_potions_bought": quantity, "total_gold_paid": gold_amount }
       
        else:
            return { "total_potions_bought": 0, "total_gold_paid": 0 }
    return {"Error. Cart not found"}
    

