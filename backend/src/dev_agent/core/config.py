from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    app_name: str = "Dev Agent"
    secret_key: str
    environment: str = "development"
    
    mongodb_url: str
    database_name: str = "devagent"
    
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_search_model: str = "groq/compound-mini"
    groq_search_model_live: str = "groq/compound"
    groq_search_country: str | None = None
    local_repo_root: str | None = None
    
    resend_api_key: str
    from_email: str
    
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    frontend_url: str = "http://localhost:3000"
    
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7 
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()