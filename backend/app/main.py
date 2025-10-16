from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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


@app.get("/api/version")
async def version():
	return {"name": app.title, "version": app.version}


# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
	return JSONResponse(
		status_code=exc.status_code,
		content={
			"error": {
				"type": "http_exception",
				"status": exc.status_code,
				"detail": exc.detail,
				"path": str(request.url.path),
			},
		},
	)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(
		status_code=422,
		content={
			"error": {
				"type": "validation_error",
				"status": 422,
				"detail": exc.errors(),
				"path": str(request.url.path),
			},
		},
	)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
	return JSONResponse(
		status_code=500,
		content={
			"error": {
				"type": "internal_error",
				"status": 500,
				"detail": "An unexpected error occurred.",
				"path": str(request.url.path),
			},
		},
	)


# Routers will be included after modules are created to avoid circular imports
try:
	from .routers import jobs, alerts

	app.include_router(jobs.router, prefix="/api")
	app.include_router(alerts.router, prefix="/api")
except Exception:
	# During first-run scaffolding, routers may not exist yet.
	pass
