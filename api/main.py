from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.security import get_current_user
from routers import (
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
