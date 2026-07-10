import logging
import os

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from core.errors import ApiError
from core.security import get_current_user
from services import gcal

router = APIRouter(prefix="/calendar", tags=["calendar"])

logger = logging.getLogger("arohi.gcal")


@router.get("/oauth/start")
def start_oauth(current_user: dict = Depends(get_current_user)) -> dict:
    return {"auth_url": gcal.build_auth_url(current_user["sub"])}


@router.get("/oauth/callback")
def oauth_callback(code: str = Query(...), state: str = Query(...)) -> RedirectResponse:
    # Google redirects the browser here directly — no Supabase JWT is (or
    # can be) attached, so this route is deliberately excluded from main.py's
    # router-level auth dependency. `state` (see gcal.build_auth_url) is how
    # this call gets tied back to the Arohi user who started the flow.
    #
    # Any failure redirects back into the app with an error flag rather than
    # returning raw JSON — this is a full-page browser navigation target,
    # not something a frontend fetch() call is consuming.
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    try:
        gcal.handle_oauth_callback(code, state)
    except Exception:
        logger.exception("gcal oauth callback failed")
        return RedirectResponse(f"{frontend_url}/settings?gcal=error")

    return RedirectResponse(f"{frontend_url}/settings?gcal=connected")


@router.post("/sync")
def sync_calendar(current_user: dict = Depends(get_current_user)) -> dict:
    try:
        gcal.sync_all(current_user["sub"])
    except gcal.GoogleCalendarNotConnected as exc:
        raise ApiError(400, "gcal_not_connected", "Connect Google Calendar first.") from exc
    except gcal.GoogleCalendarAccessRevoked as exc:
        raise ApiError(
            409, "gcal_access_revoked", "Google Calendar access was revoked. Please reconnect."
        ) from exc
    return {"status": "synced"}
