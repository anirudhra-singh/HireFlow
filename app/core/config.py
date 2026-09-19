#all env variable and settings
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    # app info
    APP_NAME: str = "HireFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SHOW_DOCS: bool = True 

    # database
    DATABASE_URL: str

     # jwt configuration
    SECRET_KEY: str          
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GEMINI_API_URL: str 
    GEMINI_API_KEY: str 


    class Config:
        env_file = ".env"
        case_sensitive = True
        



settings = Settings()