from pydantic import BaseModel

class NewCart(BaseModel):
    customer: str

class Cart():
    carts_storage = {}
    id_number = 0

    def __init__(self, new_cart: NewCart):
        self.id = Cart.id_number
        Cart.id_number += 1 #making each cart have its own unique id
        self.items = {} #holding the items
        self.customer = new_cart.customer
        Cart.carts_storage[self.id] = self

    @classmethod
    def retrieve(cls, cart_id: int):
        return cls.carts_storage.get(cart_id)

    def get_cart_items(self):
        return bool(self.items)

    def set_items(self, sku: str, quantity: int):
        if not sku in self.items:
            self.items[sku] = quantity

