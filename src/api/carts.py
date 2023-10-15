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
    "RED_POTION_0": 55,
    "GREEN_POTION_0": 55,
    "BLUE_POTION_0": 55,
    "PURPLE_POTION_0": 55,
    "YELLOW_POTION_0": 55,
}

@router.post("/{cart_id}/items/{item_sku}") #confused by this function! pls review w professor
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cart = Cart.retrieve(cart_id)
    with db.engine.begin() as connection:
        sql_statement = text("SELECT sku, quantity FROM potions_inventory WHERE quantity > 0 ORDER by id")
        result = connection.execute(sql_statement)
        row = result.first()   
        num_red_potions = row[0]
        num_green_potions = row[1]
        num_blue_potions = row[2]
        num_purple_potions = row[4]
        num_yellow_potions = row[5]


        if num_red_potions:
            if item_sku == "RED_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_green_potions:
            if item_sku == "GREEN_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_blue_potions:
            if item_sku == "BLUE_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_purple_potions:
            if item_sku == "PURPLE_POTION_0":
                cart.set_items(item_sku, cart_item.quantity)
        if num_yellow_potions:
            if item_sku == "YELLOW_POTION_0":
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
                    sql_statement = text("UPDATE potions_inventory SET quantity = quantity - :item_count_red WHERE sku == :sku")
                    quantity += red_potion_quantity
                    result = connection.execute(sql_statement, {"sku": "RED_POTION_0", "item_count_red": cart.items["RED_POTION_0"]})

                if "GREEN_POTION_0" in cart.items:
                    green_potion_quantity = cart.items["GREEN_POTION_0"]
                    sql_statement2 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_green WHERE sku == :sku")
                    quantity += green_potion_quantity
                    result2 = connection.execute(sql_statement2, {"sku": "GREEN_POTION_0", "item_count_green": cart.items["GREEN_POTION_0"]})
            
                if "BLUE_POTION_0" in cart.items:
                    blue_potion_quantity = cart.items["BLUE_POTION_0"]
                    sql_statement3 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_blue WHERE sku == :sku")
                    quantity += blue_potion_quantity
                    result3 = connection.execute(sql_statement3, {"sku": "BLUE_POTION_0", "item_count_blue": cart.items["BLUE_POTION_0"]})
                
                if "PURPLE_POTION_0" in cart.items:
                    purple_potion_quantity = cart.items["PURPLE_POTION_0"]
                    sql_statement4 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_purple WHERE sku == :sku")
                    quantity += purple_potion_quantity
                    result3 = connection.execute(sql_statement4, {"sku": "PUPRLE_POTION_0", "item_count_purple": cart.items["PURPLE_POTION_0"]})

                if "YELLOW_POTION_0" in cart.items:
                    yellow_potion_quantity = cart.items["YELLOW_POTION_0"]
                    sql_statement5 = text("UPDATE potions_inventory SET quantity = quantity - :item_count_yellow WHERE sku == :sku")
                    quantity += yellow_potion_quantity
                    result3 = connection.execute(sql_statement5, {"sku": "YELLOW_POTION_0", "item_count_yellow": cart.items["YELLOW_POTION_0"]})
            

                sql_statement_gold = text("UPDATE global_inventory SET gold = gold + :gold_amount")
                gold_amount = quantity * 55
                result_gold = connection.execute(sql_statement_gold, {"gold_amount": gold_amount})
                
                return { "total_potions_bought": quantity, "total_gold_paid": gold_amount }
       
        else:
            return { "total_potions_bought": 0, "total_gold_paid": 0 }
    return {"Error. Cart not found"}