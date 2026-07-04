import streamlit as st
import pandas as pd
from database.connection import init_db, fetch_one, fetch_all
from utils.auth import init_session_state
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_property_card, render_metric_card
from components.forms import render_login_form, render_registration_form

# ==========================================================================
# Application Configuration & Initialization
# ==========================================================================
st.set_page_config(
    page_title="StayNest | Verified Student Housing",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def load_css():
    try:
        with open("assets/css/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file not found. Falling back to default Streamlit styling.")

load_css()
init_session_state()

# Initialize Database on first run
@st.cache_resource
def setup_database():
    init_db()

setup_database()

# ==========================================================================
# Hero Section
# ==========================================================================
def render_hero():
    hero_html = """
    <div class="animate-slide-up" style="text-align: center; padding: 4rem 1rem; background: linear-gradient(135deg, var(--background) 0%, #E2E8F0 100%); border-radius: var(--radius-lg); margin-bottom: 3rem;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; color: var(--primary);">
            Find Your Perfect <span style="color: var(--accent);">Student Home</span>
        </h1>
        <p style="font-size: 1.25rem; color: var(--text-sub); max-width: 600px; margin: 0 auto 2rem auto;">
            Zero Brokerage. 100% Verified Properties. Official University Partnerships.
        </p>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # Quick Search Bar (Simulated via columns for UI layout)
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        st.selectbox("City", ["Delhi", "Mumbai", "Bengaluru", "Pune", "Chennai"], label_visibility="collapsed", index=None, placeholder="Select City")
    with col2:
        st.selectbox("University", ["Delhi University", "JNU", "IIT Bombay", "Christ University"], label_visibility="collapsed", index=None, placeholder="Near University")
    with col3:
        st.selectbox("Type", ["PG", "Flat", "Hostel"], label_visibility="collapsed", index=None, placeholder="Property Type")
    with col4:
        if st.button("Search", type="primary", use_container_width=True):
            st.switch_page("pages/1_🔍_Search.py")

# ==========================================================================
# Statistics Section
# ==========================================================================
def render_statistics():
    st.markdown("### Platform at a Glance")
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetching real stats from DB (using defaults if empty)
    total_props = fetch_one("SELECT COUNT(*) as count FROM properties")['count'] or 1240
    total_students = fetch_one("SELECT COUNT(*) as count FROM users WHERE role='student'")['count'] or 5600
    total_univs = fetch_one("SELECT COUNT(*) as count FROM universities")['count'] or 45
    
    with col1: render_metric_card("Verified Properties", f"{total_props}+", "🏢")
    with col2: render_metric_card("Happy Students", f"{total_students}+", "🎓")
    with col3: render_metric_card("Partner Universities", f"{total_univs}+", "🏛️")
    with col4: render_metric_card("Brokerage Saved", "₹12M+", "💰")
    
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================================
# Featured Properties Section
# ==========================================================================
def render_featured_properties():
    st.markdown("### Featured Verified Listings")
    
    # Fetch top 3 verified properties
    query = """
        SELECT id, title, city, price, property_type, distance_to_univ, gender_allowed, is_verified 
        FROM properties WHERE is_verified = 1 LIMIT 3
    """
    featured = fetch_all(query)
    
    if not featured:
        st.info("Demo mode: No properties in database yet. Run the sample data script to populate!")
        # Fallback dummy data for visual layout check
        featured = [
            {"id": 1, "title": "Lux Premium PG", "city": "Delhi", "price": 12000, "property_type": "PG", "distance_to_univ": 1.2, "gender_allowed": "Girls", "is_verified": 1},
            {"id": 2, "title": "Cozy Studio Near North Campus", "city": "Delhi", "price": 18000, "property_type": "Flat", "distance_to_univ": 0.5, "gender_allowed": "Any", "is_verified": 1},
            {"id": 3, "title": "Elite Boys Hostel", "city": "Bengaluru", "price": 9500, "property_type": "Hostel", "distance_to_univ": 2.1, "gender_allowed": "Boys", "is_verified": 1}
        ]

    cols = st.columns(3)
    for idx, prop in enumerate(featured):
        with cols[idx]:
            render_property_card(prop, key_suffix=f"feat_{idx}")

# ==========================================================================
# Authentication Modal / Sidebar
# ==========================================================================
def render_auth_section():
    if not st.session_state.get('authenticated', False):
        st.sidebar.markdown("### Join StayNest")
        tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
        
        with tab1:
            render_login_form()
        with tab2:
            render_registration_form()
    else:
        st.sidebar.success("You are logged in!")
        st.sidebar.markdown(f"Navigate to your **Dashboard** using the menu on the left.")

# ==========================================================================
# Main Layout Execution
# ==========================================================================
def main():
    render_navbar()
    render_auth_section()
    render_hero()
    render_statistics()
    render_featured_properties()
    render_footer()

if __name__ == "__main__":
    main()
