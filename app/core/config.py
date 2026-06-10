from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    # app info
    APP_NAME: str = "HireFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings()