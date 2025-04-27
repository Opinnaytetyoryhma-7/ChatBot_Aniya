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
