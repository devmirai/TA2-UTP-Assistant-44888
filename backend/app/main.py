from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import files, runs, stream, threads, tools

app = FastAPI(title="UTP Assistant")

_origins = ["http://localhost:5173"]
if settings.FRONTEND_URL:
    _origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health():
    return {"status": "ok", "model": settings.GROQ_MODEL}


# Placeholder: feature routers (chat, upload, etc.) mount here, e.g.
# from app.api import chat
# router.include_router(chat.router)
router.include_router(threads.router)
router.include_router(runs.router)
router.include_router(tools.router)
router.include_router(files.router)
router.include_router(stream.router)

app.include_router(router)
