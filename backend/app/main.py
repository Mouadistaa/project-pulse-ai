from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.modules.users.routes import router as users_router
from app.modules.integrations.routes import router as integrations_router
from app.modules.ingestion.routes import router as ingestion_router
from app.modules.analytics.routes import router as analytics_router
from app.modules.alerts.routes import router as alerts_router
from app.modules.forecast.routes import router as forecast_router
from app.modules.reports.routes import router as reports_router

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(users_router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(integrations_router, prefix=f"{settings.API_V1_STR}/integrations", tags=["integrations"])
app.include_router(ingestion_router, prefix=settings.API_V1_STR, tags=["ingestion"])
app.include_router(analytics_router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(alerts_router, prefix=f"{settings.API_V1_STR}/alerts", tags=["alerts"])
app.include_router(forecast_router, prefix=f"{settings.API_V1_STR}/forecast", tags=["forecast"])
app.include_router(reports_router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
