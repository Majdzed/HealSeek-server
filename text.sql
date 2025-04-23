CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,  
    name VARCHAR(100) NOT NULL,
    refresh_token VARCHAR(255),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    password VARCHAR(255) NOT NULL,
    gender VARCHAR(20),
    profile_picture_url VARCHAR(255),
    role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')), 
    CONSTRAINT valid_email_format CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')  
);

CREATE TABLE IF NOT EXISTS doctors (
    user_id INT PRIMARY KEY,
    speciality VARCHAR(100),
    experience INT CHECK (experience >= 0),
    max_appointments_in_day INT CHECK (max_appointments_in_day > 0),
    appointment_duration_minutes INT DEFAULT 30 CHECK (appointment_duration_minutes > 0), 
    teleconsultation_available BOOLEAN DEFAULT FALSE,
    office_location VARCHAR(255),
    office_location_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS patients (
    user_id INT PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INT PRIMARY KEY,
    two_factor_auth_enabled BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    appointment_time TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    type VARCHAR(50) NOT NULL CHECK (type IN ('in_person', 'teleconsultation')),
    doctor_id INT,
    patient_id INT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doctor_availability (
    availability_id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    CONSTRAINT valid_time_range CHECK (start_time < end_time)
);

CREATE TABLE IF NOT EXISTS doctor_time_off (
    time_off_id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    reason VARCHAR(255),
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    CONSTRAINT valid_date_range CHECK (start_datetime < end_datetime)
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id SERIAL PRIMARY KEY,
    rating_score INT NOT NULL CHECK (rating_score BETWEEN 1 AND 5),
    review_text TEXT,
    doctor_id INT,
    patient_id INT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS insurance_types (
    insurance_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS doctor_insurance (
    doctor_id INT,
    insurance_type_id INT,
    PRIMARY KEY (doctor_id, insurance_type_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    FOREIGN KEY (insurance_type_id) REFERENCES insurance_types(insurance_type_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS languages (
    language_id SERIAL PRIMARY KEY,
    language_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS doctor_languages (
    doctor_id INT,
    language_id INT,
    PRIMARY KEY (doctor_id, language_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES languages(language_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    diagnosis TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(user_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescription_medications (
    medication_id SERIAL PRIMARY KEY,
    prescription_id INT NOT NULL,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    instructions TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE
);