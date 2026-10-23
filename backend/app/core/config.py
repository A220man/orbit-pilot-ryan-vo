from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "orbit-pilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./orbit_pilot.db"

    # LLM Providers
    LLM_PROVIDER: str = "openai-compatible"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_TIMEOUT: float = 30.0
    LLM_MAX_RETRIES: int = 2

    # Keycloak OIDC
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "orbit-pilot"
    KEYCLOAK_CLIENT_ID: str = "orbit-pilot-frontend"
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    KEYCLOAK_ADMIN_USER: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"

    # Frontend (for CORS)
    FRONTEND_URL: str = "http://localhost:5173"

    # Demo mode
    DEMO_MODE: bool = True

    @property
    def KEYCLOAK_ISSUER(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"

    @property
    def KEYCLOAK_JWKS_URL(self) -> str:
        return f"{self.KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

    @property
    def KEYCLOAK_AUTH_URL(self) -> str:
        return f"{self.KEYCLOAK_ISSUER}/protocol/openid-connect/auth"

    @property
    def KEYCLOAK_TOKEN_URL(self) -> str:
        return f"{self.KEYCLOAK_ISSUER}/protocol/openid-connect/token"

    @property
    def KEYCLOAK_LOGOUT_URL(self) -> str:
        return f"{self.KEYCLOAK_ISSUER}/protocol/openid-connect/logout"


settings = Settings()