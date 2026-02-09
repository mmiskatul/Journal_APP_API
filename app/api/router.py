from fastapi import APIRouter

from app.api.routes import admin, ai, auth, goals, journals, moods, pages, settings, subscriptions, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(journals.router, prefix="/journals", tags=["journals"])
api_router.include_router(moods.router, prefix="/moods", tags=["moods"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(pages.router, prefix="/pages", tags=["pages"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
