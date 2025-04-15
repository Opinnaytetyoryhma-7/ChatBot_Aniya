from supabase import create_client, Client
from decouple import config

SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_KEY = config("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_unknown_message(user_message: str):
    return supabase.table("Message").insert({"user_message": user_message}).execute()
