import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'patient',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    availability TEXT NOT NULL DEFAULT 'Available',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending Payment',
    payment_status TEXT NOT NULL DEFAULT 'Unpaid',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES users(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id),
    UNIQUE(doctor_id, appointment_date, appointment_time)
);
CREATE TABLE IF NOT EXISTS support_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER UNIQUE NOT NULL,
    amount REAL NOT NULL,
    method TEXT NOT NULL,
    status TEXT NOT NULL,
    transaction_ref TEXT UNIQUE NOT NULL,
    paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(appointment_id) REFERENCES appointments(id)
);
"""


def get_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = get_db(path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def seed_database(path):
    conn = get_db(path)
    if conn.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO users(full_name,email,password_hash,role) VALUES(?,?,?,?)",
            ("System Administrator", "admin@abc-hospitals.com", generate_password_hash("Admin@123"), "admin"),
        )
    if conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO doctors(name,specialty,availability) VALUES(?,?,?)",
            [
                ("Dr. Sarah Patel", "Cardiology", "Available"),
                ("Dr. Daniel Shah", "General Medicine", "Available"),
                ("Dr. Meera Joshi", "Dermatology", "Available"),
            ],
        )
    conn.commit()
    conn.close()
