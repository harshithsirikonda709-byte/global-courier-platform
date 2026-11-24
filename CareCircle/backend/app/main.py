from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401
from .routers import auth, parents


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareCircle API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(parents.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "carecircle"}
