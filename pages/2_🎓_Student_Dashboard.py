import streamlit as st
import pandas as pd
from utils.auth import require_role, get_current_user
from database.connection import fetch_all, fetch_one, run_query
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_property_card, render_metric_card

# ==========================================================================
# Page Configuration & Protection
# ==========================================================================
st.set_page_config(page_title="Student Dashboard | StayNest", page_icon="🎓", layout="wide")

# Load Custom CSS
try:
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Ensure only logged-in students (or admins) can access this page
require_role('student')
current_user = get_current_user()
student_id = current_user['id']

# ==========================================================================
# Helper Data Fetchers
# ==========================================================================
def get_student_profile():
    return fetch_one("SELECT * FROM students WHERE user_id = ?", (student_id,))

def get_student_bookings():
    query = """
        SELECT b.id, p.title, p.city, p.price, b.visit_date, b.status 
        FROM bookings b
        JOIN properties p ON b.property_id = p.id
        WHERE b.student_id = ?
        ORDER BY b.created_at DESC
    """
    return fetch_all(query, (student_id,), as_dataframe=True)

def get_wishlist():
    query = """
        SELECT p.* FROM wishlist w
        JOIN properties p ON w.property_id = p.id
        WHERE w.student_id = ?
    """
    return fetch_all(query, (student_id,))

def get_notifications():
    query = "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC"
    return fetch_all(query, (student_id,))

# ==========================================================================
# Main Dashboard Layout
# ==========================================================================
def main():
    render_navbar()
    
    profile = get_student_profile()
    name = profile['full_name'] if profile else current_user['username']
    
    st.markdown(f"<h1 class='animate-slide-up'>Hello, {name}! 🎓</h1>", unsafe_allow_html=True)
    st.markdown("Welcome to your personal StayNest dashboard.")
    
    # Dashboard Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "📅 My Bookings", 
        "❤️ Wishlist", 
        "✨ AI Recommendations", 
        "🔔 Notifications"
    ])
    
    # ----------------------------------------------------------------------
    # TAB 1: Overview
    # ----------------------------------------------------------------------
    with tab1:
        st.markdown("### Quick Stats")
        bookings_df = get_student_bookings()
        wishlist_items = get_wishlist()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Bookings", str(len(bookings_df)) if not bookings_df.empty else "0", "📅")
        with col2:
            render_metric_card("Saved Properties", str(len(wishlist_items)), "❤️")
        with col3:
            render_metric_card("Active Alerts", str(len(get_notifications())), "🔔")
            
        st.markdown("---")
        st.markdown("### Profile Preferences")
        if profile:
            st.info(f"**Budget Range:** ₹{profile['budget_min']} - ₹{profile['budget_max']} | **Food:** {profile['food_pref'] or 'Not Set'}")
            if st.button("Update Preferences", key="update_prefs"):
                st.toast("Profile update modal would open here.")
        else:
            st.warning("Please complete your profile to get better recommendations.")

    # ----------------------------------------------------------------------
    # TAB 2: My Bookings
    # ----------------------------------------------------------------------
    with tab2:
        st.markdown("### Visit & Booking History")
        if not bookings_df.empty:
            # Apply styling to status column for better UX
            def color_status(val):
                color = 'green' if val == 'Approved' else 'orange' if val == 'Pending' else 'red' if val == 'Rejected' else 'gray'
                return f'color: {color}; font-weight: bold;'
            
            st.dataframe(
                bookings_df.style.map(color_status, subset=['status']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("You haven't booked any property visits yet.")
            if st.button("Browse Properties", key="browse_props_btn"):
                st.switch_page("pages/1_🔍_Search.py")

    # ----------------------------------------------------------------------
    # TAB 3: Wishlist
    # ----------------------------------------------------------------------
    with tab3:
        st.markdown("### Saved Properties")
        if wishlist_items:
            cols = st.columns(3)
            for idx, prop in enumerate(wishlist_items):
                with cols[idx % 3]:
                    render_property_card(prop, key_suffix=f"wish_{idx}")
        else:
            st.info("Your wishlist is empty. Start saving properties you like!")

    # ----------------------------------------------------------------------
    # TAB 4: AI Recommendations
    # ----------------------------------------------------------------------
    with tab4:
        st.markdown("### ✨ Smart Matches For You")
        st.markdown("Powered by StayNest AI based on your university, budget, and lifestyle.")
        
        # Placeholder query acting as a naive recommender until the ML engine is built
        if profile:
            rec_query = """
                SELECT * FROM properties 
                WHERE price BETWEEN ? AND ?
                AND is_verified = 1
                LIMIT 3
            """
            recs = fetch_all(rec_query, (profile['budget_min'], profile['budget_max']))
            
            if recs:
                cols = st.columns(3)
                for idx, prop in enumerate(recs):
                    with cols[idx % 3]:
                        render_property_card(prop, key_suffix=f"rec_{idx}")
            else:
                st.info("We are currently analyzing properties to find your perfect match.")
        else:
            st.warning("Complete your profile to unlock AI Recommendations.")

    # ----------------------------------------------------------------------
    # TAB 5: Notifications
    # ----------------------------------------------------------------------
    with tab5:
        st.markdown("### Alerts & Messages")
        notifications = get_notifications()
        
        if notifications:
            for notif in notifications:
                status_icon = "🟢" if not notif['is_read'] else "⚪"
                st.markdown(f"> {status_icon} **{notif['created_at'][:10]}**: {notif['message']}")
            
            if st.button("Mark all as read"):
                run_query("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (student_id,))
                st.rerun()
        else:
            st.info("No new notifications.")

    render_footer()

if __name__ == "__main__":
    main()
