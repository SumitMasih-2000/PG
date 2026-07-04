import sys
import os

# Add root directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import init_db, run_query
from utils.auth import hash_password

def seed_database():
    print("Initializing Database...")
    init_db()
    
    print("Generating Mock Users...")
    pw_hash = hash_password("password123")
    
    # 1. Admin
    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (1, 'admin_super', 'admin@staynest.com', ?, 'admin')", (pw_hash,))
    
    # 2. Universities
    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (2, 'du_official', 'admin@du.ac.in', ?, 'university')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO universities (user_id, name, location, domain, verified_badge) VALUES (2, 'Delhi University', 'Delhi', 'du.ac.in', 1)")
    
    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (3, 'iitb_official', 'admin@iitb.ac.in', ?, 'university')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO universities (user_id, name, location, domain, verified_badge) VALUES (3, 'IIT Bombay', 'Mumbai', 'iitb.ac.in', 1)")

    # 3. Owners
    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (4, 'owner_raj', 'raj@estates.com', ?, 'owner')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO owners (user_id, full_name, phone, company_name, is_verified) VALUES (4, 'Raj Sharma', '9876543210', 'Sharma Estates', 1)")

    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (5, 'owner_priya', 'priya@homes.com', ?, 'owner')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO owners (user_id, full_name, phone, company_name, is_verified) VALUES (5, 'Priya Desai', '9876543211', 'Cozy Homes PG', 1)")

    # 4. Students
    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (6, 'student_amit', 'amit@student.com', ?, 'student')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO students (user_id, full_name, gender, budget_min, budget_max, food_pref, university_id) VALUES (6, 'Amit Kumar', 'Boys', 5000, 15000, 'Required', 2)")

    run_query("INSERT OR IGNORE INTO users (id, username, email, password_hash, role) VALUES (7, 'student_neha', 'neha@student.com', ?, 'student')", (pw_hash,))
    run_query("INSERT OR IGNORE INTO students (user_id, full_name, gender, budget_min, budget_max, food_pref, university_id) VALUES (7, 'Neha Singh', 'Girls', 10000, 25000, 'Not Required', 3)")

    print("Generating Mock Properties...")
    properties = [
        # owner_id, title, desc, address, city, price, type, gender, food, wifi, parking, ac, laundry, security, dist, univ_id, verified
        (4, 'Premium Boys PG North Campus', 'Luxury living for students', 'Hudson Lane', 'Delhi', 12000, 'PG', 'Boys', 1, 1, 0, 1, 1, 1, 0.5, 2, 1),
        (4, 'Affordable Boys Flat', '2BHK shared flat', 'Kamla Nagar', 'Delhi', 8000, 'Flat', 'Boys', 0, 1, 1, 0, 0, 0, 1.2, 2, 1),
        (5, 'Girls Safe Haven Hostel', 'Highly secure girls hostel', 'Powai', 'Mumbai', 18000, 'Hostel', 'Girls', 1, 1, 0, 1, 1, 1, 0.8, 3, 1),
        (5, 'Cozy Studio Near IITB', 'Independent studio apartment', 'Andheri East', 'Mumbai', 24000, 'Flat', 'Any', 0, 1, 1, 1, 1, 1, 3.5, 3, 1),
        (4, 'Unverified Test Property', 'Should not show in search', 'Unknown', 'Pune', 10000, 'PG', 'Any', 1, 0, 0, 0, 0, 0, 5.0, None, 0),
    ]
    
    for p in properties:
        run_query("""
            INSERT INTO properties 
            (owner_id, title, description, address, city, price, property_type, gender_allowed, food, wifi, parking, ac, laundry, security, distance_to_univ, nearest_university_id, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    print("Mock data generated successfully!")
    print("You can log in with any of the emails (e.g., admin@staynest.com, amit@student.com) and password: password123")

if __name__ == "__main__":
    seed_database()
