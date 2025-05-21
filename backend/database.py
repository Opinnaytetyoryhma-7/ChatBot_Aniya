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

def get_tickets():
    return supabase.table("Ticket").select("*")

def create_review(clarity: str, ease_of_use: str, chatbot: str, contact_form: str):
    data = {
        "clarity": clarity,
        "ease_of_use": ease_of_use,
        "chatbot": chatbot,
        "contact_form": contact_form,
    }
    print("Creating review with data:", data)
    return supabase.table("Review").insert(data).execute()

def reduce_product_availability(product_name: str, quantity: int):
    product = supabase.table("Product").select("*").eq("name", product_name).single().execute()
    if not product.data:
        raise Exception(f"Product '{product_name}' not found.")

    current_availability = product.data["availability"]
    new_availability = max(current_availability - quantity, 0)

    return supabase.table("Product").update({"availability": new_availability}).eq("name", product_name).execute()
