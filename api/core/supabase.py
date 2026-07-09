import os
from functools import lru_cache

from supabase import Client, create_client


@lru_cache
def get_supabase() -> Client:
    """A single service-role client, created lazily on first use.

    Uses the service-role key (bypasses RLS), so every query in services/
    must filter by user_id explicitly — RLS is defense in depth here, not
    the enforcement mechanism.
    """
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
