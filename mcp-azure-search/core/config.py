# Centrilized Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, Field

class Settings(BaseSettings):
    """
    Centralized configuration mapping.
    Validates environment variables on startup.
    """
    # HttpUrl ensures the endpoint is a valid URL, not just any string
    azure_search_endpoint: HttpUrl = Field(..., description="Azure AI Search Endpoint URL")
    azure_search_index: str = Field(..., description="Name of the vector index")
    
    # Defaults to INFO, but can be set to DEBUG via environment variable
    log_level: str = Field("INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Safely ignores extra variables in the .env file
    )

# Singleton instance to be imported across the application
settings = Settings()