import streamlit as st
import bcrypt
import logging
from database.connection import run_query, fetch_one

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================================================
# Security Helpers
# ==========================================================================

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

# ==========================================================================
# Authentication & Registration
# ==========================================================================

def authenticate_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email and password.
    Returns the user record (dict) if successful, None otherwise.
    """
    query = "SELECT * FROM users WHERE email = ?"
    user = fetch_one(query, (email,))
    
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def register_user(username: str, email: str, password: str, role: str, profile_data: dict) -> tuple:
    """
    Register a new user and create their respective profile.
    Returns (success_boolean, message).
    """
    # Check if user already exists
    existing_user = fetch_one("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
    if existing_user:
        return False, "Email or Username already exists."

    hashed_pw = hash_password(password)
    
    # Insert into main users table
    insert_user_query = "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)"
    success, user_id_or_err = run_query(insert_user_query, (username, email, hashed_pw, role))
    
    if not success:
        return False, f"Failed to create user: {user_id_or_err}"
    
    user_id = user_id_or_err
    
    # Insert into respective role table
    try:
        if role == 'student':
            q = "INSERT INTO students (user_id, full_name, phone) VALUES (?, ?, ?)"
            run_query(q, (user_id, profile_data.get('full_name'), profile_data.get('phone')))
        elif role == 'owner':
            q = "INSERT INTO owners (user_id, full_name, phone, company_name) VALUES (?, ?, ?, ?)"
            run_query(q, (user_id, profile_data.get('full_name'), profile_data.get('phone'), profile_data.get('company_name', '')))
        elif role == 'university':
            q = "INSERT INTO universities (user_id, name, domain) VALUES (?, ?, ?)"
            run_query(q, (user_id, profile_data.get('name'), profile_data.get('domain')))
        
        return True, "Registration successful! Please login."
    except Exception as e:
        logging.error(f"Profile creation failed for user {user_id}: {e}")
        # In a strict environment, you would rollback the user creation here
        return False, "User created but profile initialization failed."

# ==========================================================================
# Session State Management
# ==========================================================================

def init_session_state():
    """Initialize necessary Streamlit session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

def login_user(user_dict: dict):
    """Set session state to log a user in."""
    st.session_state.authenticated = True
    # Remove sensitive info before storing in session state
    safe_user = {k: v for k, v in user_dict.items() if k != 'password_hash'}
    st.session_state.current_user = safe_user

def logout_user():
    """Clear session state to log a user out."""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def is_authenticated() -> bool:
    """Check if a user is currently logged in."""
    return st.session_state.get('authenticated', False)

def get_current_user() -> dict:
    """Retrieve the currently logged-in user's details."""
    return st.session_state.get('current_user', None)

def require_role(role: str):
    """Utility to stop rendering if the user doesn't have the required role."""
    if not is_authenticated():
        st.warning("You must be logged in to view this page.")
        st.stop()
    
    current_user = get_current_user()
    if current_user['role'] != role and current_user['role'] != 'admin':
        st.error(f"Access Denied. This page requires {role.capitalize()} privileges.")
        st.stop()
