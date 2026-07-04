import sqlite3
import os
import logging
import pandas as pd

# Configure logging for database operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'staynest.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

def get_connection():
    """Establish and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize the database by executing the schema.sql file."""
    conn = get_connection()
    if conn is not None:
        try:
            with open(SCHEMA_PATH, 'r') as f:
                schema_script = f.read()
            cursor = conn.cursor()
            cursor.executescript(schema_script)
            conn.commit()
            logging.info("Database initialized successfully.")
        except IOError as e:
            logging.error(f"Error reading schema file: {e}")
        except sqlite3.Error as e:
            logging.error(f"Error executing schema script: {e}")
        finally:
            conn.close()

def run_query(query, params=()):
    """Execute a query (INSERT, UPDATE, DELETE) and commit changes."""
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            return True, last_id
        except sqlite3.Error as e:
            logging.error(f"Query execution error: {e}")
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection failed"

def fetch_all(query, params=(), as_dataframe=False):
    """Fetch multiple records from the database. Optionally return as Pandas DataFrame."""
    conn = get_connection()
    if conn is not None:
        try:
            if as_dataframe:
                df = pd.read_sql_query(query, conn, params=params)
                return df
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Fetch all error: {e}")
            return [] if not as_dataframe else pd.DataFrame()
        finally:
            conn.close()
    return [] if not as_dataframe else pd.DataFrame()

def fetch_one(query, params=()):
    """Fetch a single record from the database."""
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logging.error(f"Fetch one error: {e}")
            return None
        finally:
            conn.close()
    return None
