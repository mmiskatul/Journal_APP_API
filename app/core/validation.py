from app.core.config import settings


def validate_settings() -> None:
    missing = []
    if not settings.mongodb_uri:
        missing.append("MONGODB_URI")
    if not settings.mongodb_dbname:
        missing.append("MONGODB_DBNAME")
    if not settings.secret_key or settings.secret_key == "change-me":
        missing.append("SECRET_KEY")

    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variables: {missing_list}")
