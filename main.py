from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv
from app.database.database import db
from app.routes.main_route import router

# Check for .env file and load it if exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("Loaded .env file")
else:
    print("No .env file found, using environment variables directly")

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

if missing_or_empty_vars and os.getenv("ENVIRONMENT") != "production":
    print(f"Warning: The following environment variables are missing or empty: {', '.join(missing_or_empty_vars)}")

# For Heroku's DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku uses postgres:// but psycopg2 expects postgresql://
    os.environ['DATABASE_URL'] = database_url.replace('postgres://', 'postgresql://')
    print("Converted DATABASE_URL from postgres:// to postgresql://")

class Settings(BaseSettings):
    # Basic Settings
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    WORKERS: int = int(os.getenv("WEB_CONCURRENCY", 1))

    # JWT Settings
    jwt_public_key: str = os.getenv("JWT_PUBLIC_KEY", "")
    jwt_private_key: str = os.getenv("JWT_PRIVATE_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    refresh_token_expires_in: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", "60"))
    access_token_expires_in: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", "15"))
    
    # 2FA Settings
    twofactor_secret: str = os.getenv("TWOFACTOR_SECRET", "")
    
    # Google OAuth Settings
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Email Settings
    my_mail: str = os.getenv("MY_MAIL", "")
    my_pass: str = os.getenv("MY_PASS", "")
    
    # Cloud Settings
    cloud_name: str = os.getenv("CLOUD_NAME", "")
    api_key: str = os.getenv("API_KEY", "")
    api_secret: str = os.getenv("API_SECRET", "")

    # Database Settings
    database_host: str = os.getenv("DATABASE_HOST", "")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "")
    database_user: str = os.getenv("DATABASE_USER", "")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

settings = Settings()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="HealSeek API",
        description="Healthcare Provider API",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS - fix trailing slashes
    origins: List[str] = [
        "http://localhost.tiangolo.com",
        "https://healseek-0b244fb67ca5.herokuapp.com",
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
        "https://healseek.onrender.com",
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
            print("Connecting to database...")
            db.connect()
            print("Database connected successfully")
            
            sql_path = Path(__file__).parent / "text.sql"
            if sql_path.exists():
                with open(sql_path, "r") as file:
                    sql_script = file.read()
                    print("Executing SQL script...")
                    if hasattr(db, 'execute_query_sync'):
                        db.execute_query_sync(sql_script)
                    else:
                        db.execute_query(sql_script)
                    print("SQL script executed successfully")
            else:
                print(f"Warning: SQL file not found at {sql_path}")
                
        except Exception as e:
            print(f"Database initialization error: {str(e)}")
            if hasattr(db, 'close'):
                db.close()
            # Don't raise an exception, log it and continue
            print(f"Database initialization failed: {str(e)}")

    @app.on_event("startup")
    async def startup():
        """Startup event handler."""
        print("Starting application...")
        try:
            await init_db()
            print("Application started successfully")
        except Exception as e:
            print(f"Startup error: {str(e)}")
            # Don't raise an exception, allow app to start even with DB issues
            print("App starting with database issues. Some features may be limited.")

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
            "message": "Welcome to HealSeek API",
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