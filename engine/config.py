from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    database_url: str
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    embedding_provider: str = "gemini"
    embedding_model: str = "text-embedding-004"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()