from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, bookings, customers, driver, pricing
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title="Global Courier Platform API",
    version="0.3.0",
    description="Backend API for authentication, profiles, bookings, pickup management, parcel inspection, and pricing.",
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
app.include_router(pricing.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(driver.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
