import pandas as pd
from database.connection import fetch_all, fetch_one

def calculate_match_score(student: dict, prop: dict) -> float:
    """
    Calculates a compatibility score (0-100) between a student and a property.
    """
    score = 0.0
    
    # 1. Dealbreakers (Hard Constraints)
    # Gender matching
    student_gender = student.get('gender', 'Any')
    if prop['gender_allowed'] != 'Any' and student_gender != 'Any' and prop['gender_allowed'] != student_gender:
        return 0.0
        
    # 2. Budget Scoring (Max 40 points)
    budget_max = student.get('budget_max', 999999)
    budget_min = student.get('budget_min', 0)
    
    if budget_min <= prop['price'] <= budget_max:
        score += 40.0
    elif prop['price'] < budget_min:
        # slightly cheaper is still okay, but maybe lacks premium features
        score += 20.0
    else:
        # Too expensive drops the score heavily
        score += max(0, 40.0 - ((prop['price'] - budget_max) / 1000))
        
    # 3. Distance Scoring (Max 30 points)
    distance = prop.get('distance_to_univ')
    if distance is not None:
        if distance <= 2.0:
            score += 30.0
        elif distance <= 5.0:
            score += 20.0
        elif distance <= 10.0:
            score += 10.0

    # 4. Amenities & Preferences (Max 30 points)
    food_pref = student.get('food_pref', '')
    if food_pref == 'Required' and prop.get('food'):
        score += 15.0
    elif food_pref == 'Not Required' and not prop.get('food'):
        score += 10.0 # Prefers cooking themselves
        
    if prop.get('wifi'): score += 5.0
    if prop.get('security'): score += 5.0
    if prop.get('laundry'): score += 5.0

    return min(score, 100.0)

def get_ai_recommendations(student_id: int, limit: int = 3) -> list:
    """
    Returns the top N recommended properties for a specific student.
    """
    # Fetch student profile
    student = fetch_one("SELECT * FROM students WHERE user_id = ?", (student_id,))
    if not student:
        return []
        
    # Fetch all verified properties
    properties = fetch_all("SELECT * FROM properties WHERE is_verified = 1")
    if not properties:
        return []
        
    # Calculate scores
    scored_properties = []
    for prop in properties:
        score = calculate_match_score(student, prop)
        if score > 20.0: # Minimum threshold to be considered a "match"
            prop['match_score'] = round(score, 1)
            scored_properties.append(prop)
            
    # Sort by score descending and return top matches
    scored_properties.sort(key=lambda x: x['match_score'], reverse=True)
    return scored_properties[:limit]
