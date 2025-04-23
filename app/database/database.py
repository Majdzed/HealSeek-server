import psycopg2
from psycopg2 import sql, errors
from datetime import datetime
import inflection
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
import logging
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass
class Database:
    def __init__(self, host: str, port: str, dbname: str, user: str, password: str):
        self.host = host
        self.dbname = dbname
        self.port = port
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None
        self._connection_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password
        }

    def connect(self) -> None:
        """Establish database connection with error handling"""
        try:
            logger.info("Connecting to the database...")
            self.conn = psycopg2.connect(**self._connection_params)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT version()")
            db_version = self.fetch_one()
            logger.info(f"Successfully connected to database: {db_version}")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise DatabaseError(f"Database connection failed: {str(e)}")

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
        """Execute a query with optional parameters and error handling"""
        if not self.cursor:
            raise DatabaseError("Database connection not established")
        
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.Error as e:
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