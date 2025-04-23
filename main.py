from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv
from app.database.database import db
from app.routes.main_route import router

# Check if .env file exists
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    raise FileNotFoundError(
        "The .env file is missing. Please create a .env file in the root directory of the project. "
        "You can use the .env.example file as a template."
    )

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# List of required environment variables
REQUIRED_ENV_VARS = [
    "JWT_PUBLIC_KEY",
    "JWT_PRIVATE_KEY",
    "JWT_ALGORITHM",
    "REFRESH_TOKEN_EXPIRES_IN",
    "ACCESS_TOKEN_EXPIRES_IN",
    "TWOFACTOR_SECRET",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "MY_MAIL",
    "MY_PASS",
    "CLOUD_NAME",
    "API_KEY",
    "API_SECRET",
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
]

# Check if all required environment variables are present and non-empty
missing_or_empty_vars = []
for var in REQUIRED_ENV_VARS:
    value = os.getenv(var)
    if not value:
        missing_or_empty_vars.append(var)

if missing_or_empty_vars:
    raise ValueError(
        f"The following required environment variables are missing or empty in the .env file: {', '.join(missing_or_empty_vars)}. "
        "Please ensure all required variables are defined and have valid values."
    )

class Settings(BaseSettings):
    # Basic Settings
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # JWT Settings
    jwt_public_key: str
    jwt_private_key: str
    jwt_algorithm: str
    refresh_token_expires_in: int
    access_token_expires_in: int
    
    # 2FA Settings
    twofactor_secret: str
    
    # Google OAuth Settings
    google_client_id: str
    google_client_secret: str
    
    # Email Settings
    my_mail: str
    my_pass: str
    
    # Cloud Settings
    cloud_name: str
    api_key: str
    api_secret: str

    # Database Settings
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

settings = Settings()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Your API Title",
        description="Your API Description",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS
    origins: List[str] = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://localhost:8080",
        "https://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://healseek.vercel.app",
        "https://healseek.vercel.app/en",
        "https://healseek.vercel.app/ar",
        "https://healseek.vercel.app/fr",
        "https://healseek.onrender.com/",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        max_age=600,
    )

    async def init_db():
        """Initialize database connection and execute setup scripts."""
        try:
            db.connect()
            
            sql_path = Path(__file__).parent / "text.sql"
            if sql_path.exists():
                with open(sql_path, "r") as file:
                    sql_script = file.read()
                    if hasattr(db, 'execute_query_sync'):
                        db.execute_query_sync(sql_script)
                    else:
                        db.execute_query(sql_script) 
            else:
                print(f"Warning: SQL file not found at {sql_path}")
                
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            if hasattr(db, 'close'):
                db.close()
            raise HTTPException(
                status_code=500,
                detail=f"Database initialization failed: {str(e)}"
            )

    @app.on_event("startup")
    async def startup():
        """Startup event handler."""
        print("Starting application...")
        try:
            await init_db()
            print("Application started successfully")
        except Exception as e:
            print(f"Startup error: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown():
        """Shutdown event handler."""
        try:
            if hasattr(db, 'close'):
                db.close()
            print("Database connection closed")
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
        finally:
            print("Application shutdown complete")

    api_router = APIRouter(
        prefix='/api',
        tags=["api"]
    )

    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to the API",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }

    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        try:
            is_connected = db.is_connected() if hasattr(db, 'is_connected') else True
            return {
                "status": "healthy",
                "database": "connected" if is_connected else "disconnected"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
    app.include_router(api_router)
    app.include_router(router)
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )