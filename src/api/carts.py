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


@router.get("/{cart_id}") #does not get used so can ignore
def get_cart(cart_id: int):
    """ """
    return {}


class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}") #confused by this function! pls review w professor
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cart = Cart.retrieve(cart_id)
    if item_sku == "RED_POTION_0":
        cart_item.quantity = 1 #hard coding in one. will only ever buy one red potion for $50 
    else:
        cart_item.quantity = 0 #hard coding in 0. will be 0 if not one red potion
    
    return "OK"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #if cart is not empty, return 1 bought and 50 paid
    #if empty, return nothing

    cart = Cart()
    if cart.get_cart_items():
        with db.engine.begin() as connection:
            sql_statement = text("UPDATE global_inventory SET num_red_potions = num_red_potions - 1")
            sql_statement2 = text("UPDATE global_inventory SET gold = gold + 50")
            result = connection.execute(sql_statement)
            result2 = connection.execute(sql_statement2)
            return { "total_potions_bought": 1, "total_gold_paid": 50 }
    return { "total_potions_bought": 0, "total_gold_paid": 0 }
 

