import streamlit as st
import pandas as pd
from utils.auth import get_current_user, is_authenticated
from database.connection import fetch_all, fetch_one, run_query
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_property_card

# ==========================================================================
# Page Configuration & Initialization
# ==========================================================================
st.set_page_config(page_title="Search Properties | StayNest", page_icon="🔍", layout="wide")

# Load Custom CSS
try:
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialize session state for property viewing
if 'viewing_property_id' not in st.session_state:
    st.session_state.viewing_property_id = None

# ==========================================================================
# Database Helpers for Search & Details
# ==========================================================================
def build_search_query(filters: dict):
    """Dynamically builds the SQL query based on active filters."""
    query = "SELECT * FROM properties WHERE is_verified = 1"
    params = []
    
    if filters.get('city') and filters['city'] != "All Cities":
        query += " AND city = ?"
        params.append(filters['city'])
        
    if filters.get('prop_type') and filters['prop_type'] != "All Types":
        query += " AND property_type = ?"
        params.append(filters['prop_type'])
        
    if filters.get('gender') and filters['gender'] != "Any":
        query += " AND gender_allowed IN (?, 'Any')"
        params.append(filters['gender'])
        
    query += " AND price <= ?"
    params.append(filters['max_price'])
    
    # Amenities filters (Booleans)
    amenities = ['food', 'wifi', 'ac', 'laundry', 'parking', 'security']
    for amenity in amenities:
        if filters.get(amenity):
            query += f" AND {amenity} = 1"
            
    query += " ORDER BY created_at DESC"
    
    return fetch_all(query, tuple(params))

def get_property_details(prop_id):
    query = """
        SELECT p.*, u.username as owner_username, o.full_name as owner_name, o.phone as owner_phone,
               un.name as university_name
        FROM properties p
        JOIN users u ON p.owner_id = u.id
        LEFT JOIN owners o ON u.id = o.user_id
        LEFT JOIN universities un ON p.nearest_university_id = un.user_id
        WHERE p.id = ?
    """
    return fetch_one(query, (prop_id,))

# ==========================================================================
# View: Detailed Property View
# ==========================================================================
def render_property_details():
    prop_id = st.session_state.viewing_property_id
    prop = get_property_details(prop_id)
    
    if not prop:
        st.error("Property not found or has been removed.")
        if st.button("← Back to Search"):
            st.session_state.viewing_property_id = None
            st.rerun()
        return

    # Navigation & Header
    if st.button("← Back to Search", type="secondary"):
        st.session_state.viewing_property_id = None
        st.rerun()
        
    st.markdown(f"<h1 class='animate-slide-up'>{prop['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"📍 **{prop['address']}, {prop['city']}** | 🏢 **{prop['property_type']}** | 👥 **For: {prop['gender_allowed']}**")
    
    # Image Gallery (Simulated with placeholders for zero-configuration)
    col_img1, col_img2, col_img3 = st.columns([2, 1, 1])
    with col_img1:
        st.markdown(f"""
        <div style="background-color: var(--border); height: 400px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: var(--text-sub);">
            📸 Main Property Image placeholder
        </div>
        """, unsafe_allow_html=True)
    with col_img2:
        st.markdown(f"""
        <div style="background-color: var(--border); height: 190px; border-radius: var(--radius-lg); margin-bottom: 20px; display: flex; align-items: center; justify-content: center; color: var(--text-sub);">📸 Interior</div>
        <div style="background-color: var(--border); height: 190px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: var(--text-sub);">📸 Room</div>
        """, unsafe_allow_html=True)
    with col_img3:
        st.markdown(f"""
        <div style="background-color: var(--border); height: 190px; border-radius: var(--radius-lg); margin-bottom: 20px; display: flex; align-items: center; justify-content: center; color: var(--text-sub);">📸 Amenities</div>
        <div style="background-color: var(--border); height: 190px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: var(--text-sub);">📸 Exterior</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Details & Actions
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.markdown("### Description")
        st.write(prop['description'] or "No detailed description provided by the owner.")
        
        st.markdown("### Amenities Provided")
        amenity_cols = st.columns(3)
        amenities_map = {
            'Food Included': prop['food'],
            'High-Speed WiFi': prop['wifi'],
            'Air Conditioning': prop['ac'],
            'Laundry Service': prop['laundry'],
            'Parking Space': prop['parking'],
            '24/7 Security': prop['security']
        }
        
        idx = 0
        for amenity, has_it in amenities_map.items():
            if has_it:
                with amenity_cols[idx % 3]:
                    st.markdown(f"✅ {amenity}")
                idx += 1
        if idx == 0:
            st.info("No specific amenities listed.")
            
        st.markdown("### Location & University")
        if prop['university_name']:
            st.markdown(f"🎓 **Nearest University:** {prop['university_name']} ({prop['distance_to_univ']} km away)")
        else:
            st.markdown("📍 No specific university linked nearby.")

    with col_side:
        # Action Card
        st.markdown(f"""
        <div class="glass-card" style="position: sticky; top: 2rem;">
            <h2 style="color: var(--accent); margin-top: 0;">₹{prop['price']:,}<span style="font-size: 1rem; font-weight: 400; color: var(--text-sub);">/month</span></h2>
            <p style="color: var(--success); font-weight: bold;">✓ 100% Brokerage Free</p>
            <p><strong>Owner:</strong> {prop['owner_name'] or prop['owner_username']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactions
        user = get_current_user()
        is_student = user and user['role'] == 'student'
        
        if st.button("📅 Book a Visit", type="primary", use_container_width=True, disabled=not is_student):
            if not is_student:
                st.toast("Only registered students can book visits.")
            else:
                st.session_state['show_booking_modal'] = True
                
        if st.button("❤️ Save to Wishlist", use_container_width=True, disabled=not is_student):
            if is_student:
                run_query("INSERT OR IGNORE INTO wishlist (student_id, property_id) VALUES (?, ?)", (user['id'], prop_id))
                st.toast("Added to your wishlist!")
            else:
                st.toast("Only registered students can save properties.")
                
        if not is_authenticated():
            st.warning("Please login to book visits or save properties.")

    # Handle Booking Modal Logic (using expander as a modal alternative in Streamlit)
    if st.session_state.get('show_booking_modal'):
        with st.expander("📅 Select Visit Date", expanded=True):
            with st.form("booking_form"):
                visit_date = st.date_input("When would you like to visit?")
                submit_booking = st.form_submit_button("Confirm Booking Request", type="primary")
                
                if submit_booking:
                    success, msg = run_query(
                        "INSERT INTO bookings (student_id, property_id, visit_date) VALUES (?, ?, ?)",
                        (user['id'], prop_id, visit_date)
                    )
                    if success:
                        st.success("Visit request sent to the owner! Check your dashboard for updates.")
                        st.session_state['show_booking_modal'] = False
                    else:
                        st.error(f"Booking failed: {msg}")

# ==========================================================================
# View: Main Search / List View
# ==========================================================================
def render_search_page():
    # Sidebar Filters
    st.sidebar.markdown("### 🔍 Filter Properties")
    
    filters = {}
    filters['city'] = st.sidebar.selectbox("City", ["All Cities", "Delhi", "Mumbai", "Bengaluru", "Pune", "Chennai"])
    filters['prop_type'] = st.sidebar.selectbox("Property Type", ["All Types", "PG", "Flat", "Hostel"])
    filters['max_price'] = st.sidebar.slider("Max Monthly Rent (₹)", min_value=2000, max_value=50000, value=25000, step=1000)
    filters['gender'] = st.sidebar.selectbox("For", ["Any", "Boys", "Girls"])
    
    st.sidebar.markdown("#### Amenities")
    filters['food'] = st.sidebar.checkbox("Food Included")
    filters['wifi'] = st.sidebar.checkbox("WiFi")
    filters['ac'] = st.sidebar.checkbox("AC")
    filters['laundry'] = st.sidebar.checkbox("Laundry")
    filters['parking'] = st.sidebar.checkbox("Parking")
    filters['security'] = st.sidebar.checkbox("Security/CCTV")
    
    st.markdown("<h2 class='animate-slide-up'>Find Your Perfect Stay</h2>", unsafe_allow_html=True)
    
    # Fetch Data
    properties = build_search_query(filters)
    
    # Header stats
    st.markdown(f"**{len(properties)} verified properties found matching your criteria.**")
    st.markdown("---")
    
    # Render Grid
    if properties:
        cols = st.columns(3)
        for idx, prop in enumerate(properties):
            with cols[idx % 3]:
                # We reuse the component built earlier. It handles the "View Details" click.
                render_property_card(prop, key_suffix=f"search_{idx}")
    else:
        st.info("No properties found matching your exact filters. Try adjusting your search criteria.")
        
        # Suggest removing some strict filters visually
        if st.button("Reset Filters"):
            st.rerun()

# ==========================================================================
# Main Execution Control
# ==========================================================================
def main():
    render_navbar()
    
    # Toggle between list view and detail view based on session state
    if st.session_state.viewing_property_id is not None:
        render_property_details()
    else:
        render_search_page()
        
    render_footer()

if __name__ == "__main__":
    main()
