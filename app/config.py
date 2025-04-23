from pydantic import EmailStr
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Provide default values for environment variables or make them optional
    ACCESS_TOKEN_EXPIRES_IN: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", "604800"))
    JWT_PUBLIC_KEY: str = os.getenv("JWT_PUBLIC_KEY", "")
    JWT_PRIVATE_KEY: str = os.getenv("JWT_PRIVATE_KEY", "")
    REFRESH_TOKEN_EXPIRES_IN: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", "3600"))
    MY_MAIL: str = os.getenv("MY_MAIL", "")
    MY_PASS: str = os.getenv("MY_PASS", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    TWOFACTOR_SECRET: str = os.getenv("TWOFACTOR_SECRET", "")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    CLOUD_NAME: str = os.getenv("CLOUD_NAME", "")
    API_KEY: str = os.getenv("API_KEY", "")
    API_SECRET: str = os.getenv("API_SECRET", "")
    
    # Database settings
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_SSLMODE: str = os.getenv("DATABASE_SSLMODE", "require")

    # If DATABASE_URL is provided (Heroku provides this), it will take precedence
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    class Config:
        env_file = './.env'
        # Don't error if .env file is missing - important for Heroku
        env_file_encoding = 'utf-8'
        case_sensitive = False
        # Make sure Heroku can find the environment variables
        env_prefix = ''


settings = Settings()