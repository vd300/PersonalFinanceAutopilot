from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.router import router as alerts_router
from app.auth.router import router as auth_router
from app.bills.router import router as bills_router
from app.categories import router as categories_router
from app.core.config import get_settings
from app.core.database import SessionLocal, create_database
from app.dashboard.router import router as dashboard_router
from app.demo_seed import seed_demo_data
from app.financial_profile.router import router as financial_profile_router
from app.imports.router import router as imports_router
from app.settings.router import router as settings_router
from app.subscriptions.router import router as subscriptions_router
from app.transactions.router import router as transactions_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    create_database()
    if settings.seed_demo_data:
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(imports_router, prefix=api_prefix)
app.include_router(transactions_router, prefix=api_prefix)
app.include_router(categories_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(financial_profile_router, prefix=api_prefix)
app.include_router(subscriptions_router, prefix=api_prefix)
app.include_router(bills_router, prefix=api_prefix)
app.include_router(alerts_router, prefix=api_prefix)
app.include_router(settings_router, prefix=api_prefix)
