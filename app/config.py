from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    MY_MAIL:str
    MY_PASS:str
    JWT_ALGORITHM: str 
    TWOFACTOR_SECRET: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD : str



    # CLIENT_ORIGIN: str

    # EMAIL_HOST: str
    # EMAIL_PORT: int
    # EMAIL_USERNAME: str
    # EMAIL_PASSWORD: str
    # EMAIL_FROM: EmailStr

    class Config:
        env_file = './.env'


settings = Settings()