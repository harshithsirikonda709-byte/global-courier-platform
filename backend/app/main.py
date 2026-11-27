from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, bookings, customers
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title="Global Courier Platform API",
    version="0.2.0",
    description="Backend API for customer authentication, profiles, and courier booking operations.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
