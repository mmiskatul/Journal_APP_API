from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.middleware.auth_middleware import AuthContextMiddleware
from app.middleware.error_middleware import ErrorHandlingMiddleware

# Create tables (dev only). Use Alembic migrations for production.
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, openapi_url=f"{settings.api_v1_prefix}/openapi.json")

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(AuthContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
