from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine
from .scheduler import start_scheduler

app = FastAPI(title="LinkedIn Job Scraper & Alert System", version="1.0.0")

# CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Create tables (simple approach for SQLite). For production, prefer Alembic migrations.
Base.metadata.create_all(bind=engine)

# Start scheduler
start_scheduler()


@app.get("/api/health")
async def health():
	return {"status": "ok"}


# Routers will be included after modules are created to avoid circular imports
try:
	from .routers import jobs, alerts

	app.include_router(jobs.router, prefix="/api")
	app.include_router(alerts.router, prefix="/api")
except Exception:
	# During first-run scaffolding, routers may not exist yet.
	pass
