from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, analytics, agent
from app.services.analytics_service import AnalyticsService
from app.services.monday_service import get_monday_service
from app.database import create_tables, SessionLocal, User
from app.utils.security import get_password_hash

app = FastAPI(title="Skylark BI API", version="1.0.0")

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(agent.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    settings = get_settings()
    mode = "mock" if settings.USE_MOCK_MONDAY else "live"
    openai_enabled = bool(settings.OPENAI_API_KEY)
    return {"status": "healthy", "mode": mode, "openai_enabled": openai_enabled}


@app.on_event("startup")
async def startup_event():
    # 1. Create DB tables
    create_tables()

    # 2. Seed default founder account if it doesn't exist
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.FOUNDER_USERNAME).first()
        if not existing:
            founder = User(
                username=settings.FOUNDER_USERNAME,
                hashed_password=get_password_hash(settings.FOUNDER_PASSWORD),
                full_name="Founder",
                email="",
                role="founder",
                is_active=True,
            )
            db.add(founder)
            db.commit()
            print(f"[Startup] Created default founder account: {settings.FOUNDER_USERNAME}")
        else:
            print(f"[Startup] Founder account already exists: {settings.FOUNDER_USERNAME}")
    finally:
        db.close()

    # 3. Pre-warm analytics cache
    analytics_svc = AnalyticsService()
    monday_svc = get_monday_service()
    await analytics_svc.get_full_dashboard(monday_svc)
    print("[Startup] Analytics cache warmed up.")
