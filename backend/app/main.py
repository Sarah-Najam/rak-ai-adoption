"""Application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, config, dashboard, departments, waves
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Measures how effectively each department is adopting AI, and whether "
        "training changes that. Survey responses in, department scores out."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, dashboard.router, departments.router, waves.router, config.router):
    app.include_router(router, prefix=settings.API_V1)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness check for the platform. No database call, so it stays honest
    about the process being up rather than about the database being reachable."""
    return {"status": "ok"}
