from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, companions, parents, visits


app = FastAPI(
    title="CareCircle API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(parents.router)
app.include_router(companions.router)
app.include_router(companions.admin_router)
app.include_router(visits.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "carecircle"}
