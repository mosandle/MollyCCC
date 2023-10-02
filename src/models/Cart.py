from pydantic import BaseModel

class NewCart(BaseModel):
    customer: str


class Cart():
    carts_storage = {}
    id_number = 0

    def __init__(self, new_cart: NewCart):
        self.id = Cart.id_number
        Cart.id_number += 1
        self.items = {}
        self.customer = new_cart.customer
        Cart.carts_storage[self.id] = self

    def retrieve(cart_id: int):
        return Cart.carts_storage.get(cart_id)

    def get_cart_items(self):
        if self.items.items() == 1:
            return { "total_potions_bought": 1, "total_gold_paid": 50 }
        else:
            return { "total_potions_bought": 0, "total_gold_paid": 0 }


    
