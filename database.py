# # database.py
# import sqlite3
# import datetime

# DB_NAME = "scan_history.db"

# # Create table if not exists
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS scans (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     filename TEXT,
#                     grade_a INTEGER,
#                     grade_b INTEGER,
#                     final_grade TEXT,
#                     timestamp TEXT
#                 )''')
#     conn.commit()
#     conn.close()

# # Insert a scan record
# def insert_scan(filename, grade_a, grade_b, final_grade):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("INSERT INTO scans (filename, grade_a, grade_b, final_grade, timestamp) VALUES (?, ?, ?, ?, ?)",
#               (filename, grade_a, grade_b, final_grade, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
#     conn.commit()
#     conn.close()

# # Get all scan records
# def get_all_scans():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute("SELECT * FROM scans ORDER BY timestamp DESC")
#     rows = c.fetchall()
#     conn.close()
#     return rows

# # Initialize DB on import
# init_db()



import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "scan_history.db"

# Create tables if not exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Existing scans table
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    grade_a INTEGER,
                    grade_b INTEGER,
                    final_grade TEXT,
                    timestamp TEXT
                )''')
    
    # New users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT
                )''')
    
    conn.commit()
    conn.close()

# Insert a scan record (existing function)
def insert_scan(filename, grade_a, grade_b, final_grade):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scans (filename, grade_a, grade_b, final_grade, timestamp) VALUES (?, ?, ?, ?, ?)",
              (filename, grade_a, grade_b, final_grade, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# Get all scan records (existing function)
def get_all_scans():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ------------------ NEW FUNCTIONS FOR AUTH ------------------ #
def create_user(username, email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = generate_password_hash(password)
    c.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
              (username, email, hashed_pw, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def verify_user(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user[3], password):  # user[3] = password_hash
        return user
    return None

def update_password(email, new_password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = generate_password_hash(new_password)
    c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_pw, email))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
