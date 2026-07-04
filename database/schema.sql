-- Users Table (Central Authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'owner', 'university', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students Profile Table
CREATE TABLE IF NOT EXISTS students (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT,
    gender TEXT,
    university_id INTEGER,
    budget_min INTEGER DEFAULT 0,
    budget_max INTEGER DEFAULT 50000,
    food_pref TEXT,
    lifestyle_pref TEXT, -- Used for AI recommendations
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Owners Profile Table
CREATE TABLE IF NOT EXISTS owners (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone TEXT,
    company_name TEXT,
    is_verified BOOLEAN DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Universities Profile Table
CREATE TABLE IF NOT EXISTS universities (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    location TEXT,
    domain TEXT UNIQUE,
    verified_badge BOOLEAN DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Properties Table
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    price INTEGER NOT NULL,
    property_type TEXT NOT NULL CHECK(property_type IN ('PG', 'Flat', 'Hostel')),
    gender_allowed TEXT NOT NULL,
    -- Amenities (Booleans)
    food BOOLEAN DEFAULT 0,
    wifi BOOLEAN DEFAULT 0,
    parking BOOLEAN DEFAULT 0,
    ac BOOLEAN DEFAULT 0,
    laundry BOOLEAN DEFAULT 0,
    security BOOLEAN DEFAULT 0,
    -- Matchmaking metrics
    distance_to_univ REAL, -- Distance in km
    nearest_university_id INTEGER,
    is_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_id) REFERENCES users(id),
    FOREIGN KEY(nearest_university_id) REFERENCES universities(user_id)
);

-- Bookings & Visits
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    visit_date DATE NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected', 'Completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id),
    FOREIGN KEY(property_id) REFERENCES properties(id)
);

-- Wishlist / Saved Properties
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id),
    FOREIGN KEY(property_id) REFERENCES properties(id),
    UNIQUE(student_id, property_id)
);

-- Property Reviews & Ratings
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES users(id),
    FOREIGN KEY(property_id) REFERENCES properties(id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
