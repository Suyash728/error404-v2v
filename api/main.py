from dotenv import load_dotenv

# Must run before any of these imports touch os.environ (core.security and
# core.supabase both read env vars, some at call time not import time, but
# loading here up front means every path — including `uvicorn --reload`'s
# subprocess — sees .env consistently).
load_dotenv()

from fastapi import Depends, FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from core.security import get_current_user  # noqa: E402
from routers import (  # noqa: E402
    account,
    calendar,
    cycles,
    export,
    fit,
    gamification,
    logs,
    qa,
    recommendations,
    reproductive,
    risk,
    tts,
)

app = FastAPI(title="Arohi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

authenticated = [Depends(get_current_user)]

app.include_router(cycles.router, dependencies=authenticated)
app.include_router(logs.router, dependencies=authenticated)
app.include_router(risk.router, dependencies=authenticated)
app.include_router(recommendations.router, dependencies=authenticated)
app.include_router(qa.router, dependencies=authenticated)
app.include_router(tts.router, dependencies=authenticated)
app.include_router(calendar.router, dependencies=authenticated)
app.include_router(reproductive.router, dependencies=authenticated)
app.include_router(gamification.router, dependencies=authenticated)
app.include_router(fit.router, dependencies=authenticated)
app.include_router(export.router, dependencies=authenticated)
app.include_router(account.router, dependencies=authenticated)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
