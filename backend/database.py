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
