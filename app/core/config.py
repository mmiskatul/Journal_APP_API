from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Mental Wellness API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "dev"

    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/wellness"

    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_basic: str = ""
    stripe_price_premium: str = ""
    frontend_success_url: str = "http://localhost:3000/subscription/success"
    frontend_cancel_url: str = "http://localhost:3000/subscription/cancel"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"


settings = Settings()
