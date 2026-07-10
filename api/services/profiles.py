"""Business logic for the profiles table. Routers stay thin; this does the work."""

from core.supabase import get_supabase
from models.schemas import Profile


def get_profile(user_id: str) -> Profile:
    # No existence check: the auth.users trigger guarantees a profiles row
    # for every signed-up user (see CLAUDE.md's database invariants).
    supabase = get_supabase()
    response = supabase.table("profiles").select("*").eq("id", user_id).limit(1).execute()
    return Profile(**response.data[0])
