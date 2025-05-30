import psycopg2
from psycopg2 import sql, errors
from datetime import datetime
import inflection
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
import logging
import os
import urllib.parse
import time
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

class Database:
    def __init__(self, host: str = None, port: str = None, dbname: str = None, user: str = None, password: str = None):
        # Check if DATABASE_URL is available (Heroku provides this)
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            logger.info("Using DATABASE_URL from environment")
            # Convert postgres:// to postgresql:// (psycopg2 expects this)
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://')
                logger.info("Converted postgres:// to postgresql:// in DATABASE_URL")
            
            # Parse the URL
            parsed_url = urllib.parse.urlparse(database_url)
            
            self.host = parsed_url.hostname
            self.port = parsed_url.port or 5432
            self.dbname = parsed_url.path[1:]  # Remove leading slash
            self.user = parsed_url.username
            self.password = parsed_url.password
            
            logger.info(f"Parsed database connection from URL: host={self.host}, port={self.port}, dbname={self.dbname}, user={self.user}")
        else:
            # Fall back to individual parameters
            logger.info("Using individual database connection parameters")
            self.host = host
            self.port = port
            self.dbname = dbname
            self.user = user
            self.password = password
        
        self.conn = None
        self.cursor = None
        self.last_connection_attempt = 0
        self.reconnect_delay = 5  # seconds between reconnection attempts
        self.max_retries = 3  # maximum number of connection retry attempts
        
        # Get SSL mode from environment or use 'require' as default for Neon
        self.sslmode = os.getenv('DATABASE_SSLMODE', 'require')
        logger.info(f"Using SSL mode: {self.sslmode}")
        
        self._connection_params = {
            'host': self.host,
            'port': self.port,
            'dbname': self.dbname,
            'user': self.user,
            'password': self.password,
            'sslmode': self.sslmode
        }

    def connect(self) -> bool:
        """Establish database connection with error handling"""
        try:
            self.last_connection_attempt = time.time()
            logger.info(f"Connecting to database at {self.host}:{self.port}/{self.dbname} with sslmode={self.sslmode}")
            self.conn = psycopg2.connect(**self._connection_params)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT version()")
            db_version = self.fetch_one()
            logger.info(f"Successfully connected to database: {db_version}")
            return True
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            if "could not connect to server" in str(e):
                logger.error("Database server connection failed. Check network and credentials.")
            elif "database" in str(e) and "does not exist" in str(e):
                logger.error("Database does not exist. It may need to be created.")
            elif "connection is insecure" in str(e):
                logger.error("Connection requires SSL. Set DATABASE_SSLMODE=require")
            self.conn = None
            self.cursor = None
            return False
    
    def ensure_connection(self) -> bool:
        """Ensure database connection is active, reconnect if needed"""
        # If enough time has passed since last connection attempt, try to reconnect
        now = time.time()
        if not self.is_connected() and (now - self.last_connection_attempt) > self.reconnect_delay:
            logger.info("Connection lost or not established. Attempting to reconnect...")
            return self.connect()
        return self.is_connected()
    
    def reconnect_if_needed(self, max_retries=3) -> bool:
        """Try to reconnect to the database with multiple attempts if needed"""
        if self.is_connected():
            return True
            
        for attempt in range(max_retries):
            logger.info(f"Reconnection attempt {attempt + 1}/{max_retries}")
            if self.connect():
                return True
            time.sleep(self.reconnect_delay)
        
        logger.error(f"Failed to reconnect after {max_retries} attempts")
        return False
    
    def is_connected(self) -> bool:
        """Check if database connection is active"""
        if self.conn is None:
            return False
        try:
            # Try a simple query to test connection
            self.cursor.execute("SELECT 1")
            return True
        except (psycopg2.Error, AttributeError):
            self.conn = None
            self.cursor = None
            return False

    def close(self) -> None:
        """Safely close database connections"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed successfully")
        except psycopg2.Error as e:
            logger.error(f"Error closing database connection: {str(e)}")
            raise DatabaseError(f"Failed to close database connection: {str(e)}")

    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            yield
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Transaction failed, rolling back: {str(e)}")
            raise

    def execute_query(self, query: Union[str, sql.Composed], params: Optional[tuple] = None) -> None:
        """Execute a query with optional parameters, error handling, and automatic reconnection"""
        # Try to ensure we have a connection
        if not self.ensure_connection():
            # If we're still not connected after trying, reconnect with retries
            if not self.reconnect_if_needed(self.max_retries):
                raise DatabaseError("Database connection could not be established")
        
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.OperationalError as e:
            # Connection might have been lost
            logger.warning(f"Operational error during query: {str(e)}. Attempting to reconnect...")
            if self.reconnect_if_needed():
                # Retry the query once reconnected
                try:
                    self.cursor.execute(query, params)
                    self.conn.commit()
                except psycopg2.Error as retry_e:
                    self.conn.rollback()
                    logger.error(f"Query failed after reconnection: {str(retry_e)}")
                    raise DatabaseError(f"Query execution failed after reconnection: {str(retry_e)}")
            else:
                raise DatabaseError("Could not reconnect to database")
        except psycopg2.Error as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Query execution failed: {str(e)}\nQuery: {query}")
            raise DatabaseError(f"Query execution failed: {str(e)}")

    def fetch_one(self) -> Optional[tuple]:
        """Fetch a single row with error handling"""
        try:
            return self.cursor.fetchone()
        except psycopg2.Error as e:
            logger.error(f"Error fetching row: {str(e)}")
            raise DatabaseError(f"Failed to fetch row: {str(e)}")

    def fetch_all(self) -> List[tuple]:
        """Fetch all rows with error handling"""
        try:
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error fetching all rows: {str(e)}")
            raise DatabaseError(f"Failed to fetch all rows: {str(e)}")

class BaseModel:
    table_name = None

    @classmethod
    def create_table(cls):
        if not cls.table_name:
            raise ValueError(f"Table name for {cls.__name__} not defined")
        
        columns = cls.__annotations__  # Using Python type annotations as columns
        columns_def = ", ".join([f"{column} {dtype}" for column, dtype in columns.items()])

        query = f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({columns_def});"
        return query

    @classmethod
    def insert(cls, **kwargs):
        kwargs = {inflection.underscore(k): v for k, v in kwargs.items()}
        keys = kwargs.keys()
        values = kwargs.values()
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(cls.table_name),
            fields=sql.SQL(',').join(map(sql.Identifier, keys)),
            values=sql.SQL(',').join(map(sql.Literal, values))
        )
        return query

    @classmethod
    def select(cls, **kwargs):
        query = f"SELECT * FROM {cls.table_name} WHERE "
        condition = " AND ".join([f"{key} = %s" for key in kwargs.keys()])
        query += condition
        return query

    @classmethod
    def update(cls, **kwargs):
        query = f"UPDATE {cls.table_name} SET "
        set_clause = ", ".join([f"{key} = %s" for key in list(kwargs.keys())[:-1]])
        query += set_clause 
        last_item = list(kwargs.keys())[-1]
        query += f" WHERE {last_item} = %s"
        return query 

    @classmethod
    def delete(cls, **kwargs):
        query = f"DELETE FROM {cls.table_name} WHERE "
        condition = " AND ".join([f"{key} = %s" for key in kwargs.keys()])
        query += condition
        return query
    # display the attributes of the class
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

class User(BaseModel):
    table_name = "users"
    user_id: int
    name: str
    email: str
    phone_number: str
    date_of_birth: str
    password: str
    gender: str
    profile_picture_url: str
    role: str
    refresh_token: str

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Doctor(BaseModel):
    table_name = "doctors"
    user_id: int
    speciality: str
    experience: int
    max_appointments_in_day: int
    appointment_duration_minutes: int 
    teleconsultation_available: bool
    office_location: str
    office_location_url: str

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Patient(BaseModel):
    table_name = "patients"
    user_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Admin(BaseModel):
    table_name = "admins"
    user_id: int
    two_factor_auth_enabled: bool
    last_login: datetime

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Notification(BaseModel):
    table_name = "notifications"
    notification_id: int
    content: str
    is_read: bool
    created_at: datetime
    user_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Appointment(BaseModel):
    table_name = "appointments"
    appointment_id: int
    appointment_time: datetime
    status: str
    doctor_id: int
    patient_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Rating(BaseModel):
    table_name = "ratings"
    rating_id: int
    rating_score: int
    review_text: str
    doctor_id: int
    patient_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class InsuranceType(BaseModel):
    table_name = "insurance_types"
    insurance_type_id: int
    type_name: str

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class DoctorInsurance(BaseModel):
    table_name = "doctor_insurance"
    doctor_id: int
    insurance_type_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class DoctorLanguage(BaseModel):
    table_name = "doctor_languages"
    doctor_id: int
    language_id: int

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Language(BaseModel):
    table_name = "languages"
    language_id: int
    language_name: str

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

class Prescription(BaseModel):
    table_name = "prescriptions"
    prescription_id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    diagnosis: str
    notes: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

    @classmethod
    def update(cls, **kwargs):
        # Update the updated_at timestamp
        kwargs['updated_at'] = datetime.now()
        query = super().update(**kwargs)
        return query

class PrescriptionMedication(BaseModel):
    table_name = "prescription_medications"
    medication_id: int
    prescription_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str

    @classmethod
    def create(cls, **kwargs):
        query = cls.insert(**kwargs)
        return query

    @classmethod
    def find(cls, **kwargs):
        query = cls.select(**kwargs)
        return query

db = Database(settings.DATABASE_HOST, settings.DATABASE_PORT ,settings.DATABASE_NAME, settings.DATABASE_USER, settings.DATABASE_PASSWORD)