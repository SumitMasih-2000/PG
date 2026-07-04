import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import require_role, get_current_user
from database.connection import fetch_all, fetch_one
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_property_card, render_metric_card

# ==========================================================================
# Page Configuration & Protection
# ==========================================================================
st.set_page_config(page_title="University Partner Dashboard | StayNest", page_icon="🏛️", layout="wide")

# Load Custom CSS
try:
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Ensure only logged-in university reps (or admins) can access this page
require_role('university')
current_user = get_current_user()
univ_user_id = current_user['id']

# ==========================================================================
# Data Fetching Helpers
# ==========================================================================
def get_university_profile():
    return fetch_one("SELECT * FROM universities WHERE user_id = ?", (univ_user_id,))

def get_nearby_properties():
    query = """
        SELECT * FROM properties 
        WHERE nearest_university_id = ? AND is_verified = 1
        ORDER BY distance_to_univ ASC
    """
    return fetch_all(query, (univ_user_id,))

def get_student_stats():
    query = """
        SELECT s.gender, s.budget_max, s.food_pref, s.lifestyle_pref 
        FROM students s
        WHERE s.university_id = ?
    """
    return fetch_all(query, (univ_user_id,), as_dataframe=True)

# ==========================================================================
# Main Dashboard Layout
# ==========================================================================
def main():
    render_navbar()
    
    profile = get_university_profile()
    univ_name = profile['name'] if profile else current_user['username']
    
    # Official Partner Badge
    badge_html = ""
    if profile and profile.get('verified_badge'):
        badge_html = '<span class="badge-verified" style="font-size: 1rem; margin-left: 1rem;">🛡️ Official Partner</span>'
    
    st.markdown(f"<div class='animate-slide-up' style='display: flex; align-items: center;'><h1>{univ_name}</h1>{badge_html}</div>", unsafe_allow_html=True)
    st.markdown("Welcome to the Official Partnership Dashboard. Monitor safe and verified housing for your students.")
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Campus Overview", 
        "🏘️ Verified Nearby Housing", 
        "🎓 Student Insights"
    ])
    
    # ----------------------------------------------------------------------
    # TAB 1: Campus Overview
    # ----------------------------------------------------------------------
    with tab1:
        properties = get_nearby_properties()
        students_df = get_student_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Verified Properties Nearby", str(len(properties)), "🏢")
        with col2:
            total_students = len(students_df) if not students_df.empty else 0
            render_metric_card("Registered Students", str(total_students), "👨‍🎓")
        with col3:
            avg_distance = round(sum(p['distance_to_univ'] for p in properties) / len(properties), 2) if properties else 0
            render_metric_card("Avg Distance to Campus", f"{avg_distance} km", "📍")
            
        st.markdown("---")
        st.markdown("### Partnership Benefits")
        st.info("""
        **Why Partner with StayNest?**
        * **Safety First:** All properties listed under your university are physically verified by our team.
        * **Zero Brokerage:** Your students save thousands of rupees by connecting directly with owners.
        * **Priority Support:** Dedicated account managers for university-related housing disputes.
        """)

    # ----------------------------------------------------------------------
    # TAB 2: Verified Nearby Housing
    # ----------------------------------------------------------------------
    with tab2:
        st.markdown("### Safe Accommodations Around Campus")
        st.markdown("These properties have passed our strict verification process and are approved for your students.")
        
        if properties:
            cols = st.columns(3)
            for idx, prop in enumerate(properties):
                with cols[idx % 3]:
                    render_property_card(prop, key_suffix=f"univ_{idx}")
        else:
            st.info("No verified properties are currently linked to your university. Our team is actively onboarding owners in your area.")

    # ----------------------------------------------------------------------
    # TAB 3: Student Insights (Analytics)
    # ----------------------------------------------------------------------
    with tab3:
        st.markdown("### Student Housing Preferences")
        if not students_df.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Student Budget Distribution
                fig_budget = px.histogram(students_df, x='budget_max', nbins=10, 
                                          title="Student Budget Distribution (Max Budget)",
                                          color_discrete_sequence=['#2563EB'])
                fig_budget.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_budget, use_container_width=True)
                
            with col_chart2:
                # Food Preferences
                # Fill NA for better visualization
                students_df['food_pref'] = students_df['food_pref'].fillna('Not Specified')
                food_counts = students_df['food_pref'].value_counts().reset_index()
                food_counts.columns = ['Food Preference', 'Count']
                
                fig_food = px.pie(food_counts, names='Food Preference', values='Count', 
                                  title="Dietary Requirements", hole=0.4,
                                  color_discrete_sequence=px.colors.sequential.Teal)
                fig_food.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_food, use_container_width=True)
        else:
            st.info("Not enough student data to generate insights yet. Encourage your students to complete their profiles!")

    render_footer()

if __name__ == "__main__":
    main()
