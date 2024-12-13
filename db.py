import sqlite3
import hashlib
from datetime import datetime


DATABASE_PATH = './fitness.db'

# Initialize the database
def init_db():
    """
    Create the database and `user_info`, `login` and `log` table if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            sex TEXT,
            weight REAL,
            height REAL,
            activity_level TEXT,
            goal TEXT,
            health TEXT,
            food TEXT,
            FOREIGN KEY(email) REFERENCES login(email)
        )
    ''')

    # Create login table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    
    # Create log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            bp TEXT NOT NULL,
            food TEXT NOT NULL,
            FOREIGN KEY(email) REFERENCES login(email)
        )
    ''')

    conn.commit()
    conn.close()

from datetime import datetime

def insert_log(email, daily_bp, daily_food):
    """
    Insert user log data (daily_bp, daily_food) along with the current date, time, and user email into the `log` table.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Get the current date and time
        current_date = datetime.now().date()  # YYYY-MM-DD format
        current_time = datetime.now().strftime("%H:%M:%S")  # Convert time to HH:MM:SS string

        # Insert into the log table
        cursor.execute('''
            INSERT INTO log (email, date, time, bp, food)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, current_date, current_time, daily_bp, daily_food))
        conn.commit()
        return True, "Log inserted successfully!"
    except Exception as e:
        return False, f"Error inserting log: {e}"
    finally:
        conn.close()


def insert_login(data):
    """Insert user login data (email, password, and name) into the `login` table."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO login (name, email, password)
            VALUES (?, ?, ?)
        ''', (data['name'], data['email'], data['password']))

        conn.commit()
        conn.close()

    except sqlite3.IntegrityError as e:
        raise Exception(f"Error: User with email {data['email']} already exists.")
    except Exception as e:
        raise Exception(f"Database error: {e}")

def insert_user(data, email):
    """
    Insert user data into the `user_info` table.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Make sure email exists in login table (foreign key constraint check)
        cursor.execute('''SELECT email FROM login WHERE email = ?''', (email,))
        if not cursor.fetchone():
            return False, "Email does not exist in the login table."

        cursor.execute('''
            INSERT INTO user_info (email, age, sex, weight, height, activity_level, goal, health, food)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, data['age'], data['sex'], data['weight'], data['height'], data['activity_level'], data['goal'], data['health'], data['food']))

        conn.commit()
        conn.close()
        return True, "Profile created successfully."
    except sqlite3.IntegrityError as e:
        return False, f"IntegrityError: {e}"
    except Exception as e:
        return False, f"Database error: {e}"
    
def validate_login(email, password):
    """
    Validate the user's login credentials.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM login WHERE email = ? AND password = ?
        ''', (email, hashlib.sha256(password.encode()).hexdigest()))  # Check hashed password

        user = cursor.fetchone()
        conn.close()
        if user:
            return True
        else:
            return False
    except Exception as e:
        raise Exception(f"Error validating login: {e}")
    
def get_user_data(email):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Fetch user info
    cursor.execute('''
        SELECT height/weight as BMI, activity_level, goal, food
        FROM user_info
        WHERE email = ?
    ''', (email,))
    user_info = cursor.fetchone()

    # Fetch latest log entry
    cursor.execute('''
        SELECT date, bp, food
        FROM log
        WHERE email = ? AND date = DATE('now', '-1 day')
        ORDER BY time DESC
        LIMIT 1
    ''', (email,))
    log_info = cursor.fetchone()

    conn.close()

    return user_info, log_info
