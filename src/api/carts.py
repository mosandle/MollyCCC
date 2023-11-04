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

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    
    # Define the number of results per page
    results_per_page = 5

    # Calculate the offset for pagination
    if search_page and search_page.isdigit():
        page = int(search_page)
        offset = (page - 1) * results_per_page
    else:
        page = 1
        offset = 0

    order_by = None

    if sort_col == search_sort_options.timestamp:
        order_by = db.carts.c.created_at

    if sort_order == "desc":
        reverse_sort = True
    else:
        reverse_sort = False

    stmt = (
        sqlalchemy.select(
            db.cart_items.c.id,
            db.potions_inventory.c.sku,
            db.carts.c.customer_name,
            db.potions_inventory.c.price,
            db.cart_items.c.quantity,
            db.carts.c.created_at,
        )
        .select_from(
            db.cart_items
            .join(
                db.carts,
                db.cart_items.c.cart_id == db.carts.c.cart_id
            )
            .join(
                db.potions_inventory,
                db.cart_items.c.potion_id == db.potions_inventory.c.id
            )
        )
        .offset(offset)  # Apply offset for pagination
        .limit(results_per_page)  # Limit results per page
    )

    if customer_name != "":
        stmt = stmt.where(db.carts.c.customer_name.ilike(f"%{customer_name}%"))
    if potion_sku != "":
        stmt = stmt.where(db.potions_inventory.c.sku.ilike(f"%{potion_sku}%"))

    # Apply the sorting
    if order_by is not None: 
        if reverse_sort:
            stmt = stmt.order_by(order_by.desc())
        else:
            stmt = stmt.order_by(order_by.asc())

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
            {
                "line_item_id": row.id,
                "item_sku": f"{row.quantity} {row.sku}",
                "customer_name": row.customer_name,
                "line_item_total": row.price * row.quantity, 
                "timestamp": row.created_at,
            }
            )

    # Calculate "previous" and "next" page tokens
    previous_page = page - 1 if page > 1 else None

    # Check if there are more results on the next page
    next_page = page + 1 if len(json) > 0 else None

    return {
        "previous": previous_page,
        "next": next_page,
        "results": json
    }

    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items. 
"""

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
                    INSERT INTO cart_items (cart_id, quantity, potion_id) 
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
                SELECT quantity, potion_id
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
                        [{"potion_id": row.potion_id, "potion_delta": -row.quantity,}])
                
            result = connection.execute(sqlalchemy.text(
                    """
                    SELECT SUM(potions_inventory.price * cart_items.quantity) AS gold_paid,
                    SUM(cart_items.quantity) AS potions_bought
                    
                    FROM potions_inventory JOIN cart_items
                    ON potions_inventory.id = cart_items.potion_id
                    WHERE cart_items.cart_id = :cart_id;
                    """),
                    [{"cart_id": cart_id}])
            

            row = result.first()
            gold_paid = row.gold_paid
            potions_bought = row.potions_bought

            connection.execute(sqlalchemy.text("""
                            INSERT INTO gold_ledger_items (gold_delta) VALUES (:gold_paid)
                            """), {"gold_paid": gold_paid})

            """
                except Exception as e:
                    # If an error occurs, roll back the transaction to revert changes
                raise e
                connection.rollback()
                
            except Exception as e:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text(
                            DELETE FROM cart_items
                            WHERE cart_id = :cart_id),
                            {"cart_id": cart_id})
            return {"rollback error"}
            """
    return {"total_potions_bought": potions_bought, "gold_paid": gold_paid}