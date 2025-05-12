from supabase import create_client, Client
from decouple import config


SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_KEY = config("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_unknown_message(user_message: str):
    return supabase.table("Message").insert({"user_message": user_message}).execute()


def create_ticket(issue_description: str, user_email: str):
    return (
        supabase.table("Ticket").insert(
            {"issue_description": issue_description, "user_email": user_email}
        )
    ).execute()


def create_user(fname: str, lname: str, email: str, password: str):
    return supabase.table("User").insert(
        {"fname": fname, "lname": lname, "email": email, "password": password}
    )


def get_user_by_email(email: str):
    return supabase.table("User").select("*").eq("email", email).execute()


def get_user_by_id(user_id: str):
    return supabase.table("User").select("*").eq("user_id", user_id).execute()

def get_products():
    return supabase.table("Product").select("*").execute()

def update_product_quantity(product_id: int, new_quantity: int):
    return supabase.table("Product").update({"availability": new_quantity}).eq("id", product_id).execute()

def update_product_availability(product_id: str, new_quantity: int):
    response = supabase.table("products").update({
        "availability": new_quantity
    }).eq("id", product_id).execute()

    if response.status_code != 200:
        raise Exception(f"Failed to update product: {response}")
    
    return response.data

def purchase_items(cart_items):
    updates = []
    for item in cart_items:
        product_name = item["name"]
        quantity_purchased = item["quantity"]

        result = supabase.table("Product").select("availability").eq("name", product_name).execute()
        if result.data:
            current_availability = result.data[0]["availability"]
            new_availability = max(current_availability - quantity_purchased, 0)

            updates.append(
                supabase.table("Product")
                .update({"availability": new_availability})
                .eq("name", product_name)
            )
    
    # Execute updates
    for update in updates:
        update.execute()

    return {"status": "success", "message": "Purchase completed and stock updated."}

def reduce_product_availability(product_name: str, quantity: int):
    
    product = supabase.table("Product").select("*").eq("name", product_name).single().execute()
    if not product.data:
        raise Exception(f"Product '{product_name}' not found.")

    current_availability = product.data["availability"]
    new_availability = max(current_availability - quantity, 0)

    return supabase.table("Product").update({"availability": new_availability}).eq("name", product_name).execute()

def update_product_availability(purchased_items: list[dict]):
    updates = []
    for item in purchased_items:
        name = item["name"]
        quantity = item["quantity"]
        # Hakee tuotteen nimellä.
        res = supabase.table("Product").select("*").eq("name", name).execute()
        if not res.data:
            raise ValueError(f"Product '{name}' not found.")
        
        product = res.data[0]
        new_availability = max(product["availability"] - quantity, 0)
        
        # Updatee productin määrän!
        update_res = (
            supabase.table("Product")
            .update({"availability": new_availability})
            .eq("name", name)
            .execute()
        )
        updates.append(update_res.data)
    return updates