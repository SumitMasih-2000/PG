import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import require_role, get_current_user
from database.connection import fetch_all, run_query, fetch_one
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_metric_card

# ==========================================================================
# Page Configuration & Protection
# ==========================================================================
st.set_page_config(page_title="Admin Dashboard | StayNest", page_icon="🛡️", layout="wide")

# Load Custom CSS
try:
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Ensure only logged-in admins can access this page
require_role('admin')
current_user = get_current_user()

# ==========================================================================
# Data Fetching Helpers
# ==========================================================================
def get_platform_stats():
    stats = {}
    stats['total_users'] = fetch_one("SELECT COUNT(*) as count FROM users")['count'] or 0
    stats['total_properties'] = fetch_one("SELECT COUNT(*) as count FROM properties")['count'] or 0
    stats['total_bookings'] = fetch_one("SELECT COUNT(*) as count FROM bookings")['count'] or 0
    stats['pending_properties'] = fetch_one("SELECT COUNT(*) as count FROM properties WHERE is_verified = 0")['count'] or 0
    return stats

def get_pending_properties():
    query = """
        SELECT p.id, p.title, p.city, p.property_type, p.price, u.username as owner_name, p.created_at 
        FROM properties p
        JOIN users u ON p.owner_id = u.id
        WHERE p.is_verified = 0
        ORDER BY p.created_at ASC
    """
    return fetch_all(query, as_dataframe=True)

def get_all_users():
    query = "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
    return fetch_all(query, as_dataframe=True)

def get_universities():
    query = """
        SELECT u.id as user_id, un.name, un.domain, un.verified_badge 
        FROM universities un
        JOIN users u ON un.user_id = u.id
    """
    return fetch_all(query, as_dataframe=True)

# ==========================================================================
# Main Dashboard Layout
# ==========================================================================
def main():
    render_navbar()
    
    st.markdown(f"<h1 class='animate-slide-up'>System Administration 🛡️</h1>", unsafe_allow_html=True)
    st.markdown("Monitor platform health, verify listings, and manage network users.")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Platform Overview", 
        "✅ Property Verification", 
        "👥 User Management",
        "🏛️ University Management"
    ])
    
    # ----------------------------------------------------------------------
    # TAB 1: Platform Overview
    # ----------------------------------------------------------------------
    with tab1:
        stats = get_platform_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: render_metric_card("Total Users", str(stats['total_users']), "👥")
        with col2: render_metric_card("Total Properties", str(stats['total_properties']), "🏢")
        with col3: render_metric_card("Total Bookings", str(stats['total_bookings']), "📅")
        with col4: render_metric_card("Pending Verifications", str(stats['pending_properties']), "⏳")
            
        st.markdown("---")
        st.markdown("### System Analytics")
        
        users_df = get_all_users()
        if not users_df.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # User Roles Distribution
                role_counts = users_df['role'].value_counts().reset_index()
                role_counts.columns = ['Role', 'Count']
                fig_roles = px.pie(role_counts, names='Role', values='Count', 
                                   title="User Distribution by Role", hole=0.3,
                                   color_discrete_sequence=px.colors.qualitative.Set2)
                fig_roles.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_roles, use_container_width=True)
                
            with col_chart2:
                # Registration Timeline (Simplified for demo)
                users_df['date'] = pd.to_datetime(users_df['created_at']).dt.date
                timeline = users_df.groupby('date').size().reset_index(name='New Users')
                fig_timeline = px.line(timeline, x='date', y='New Users', 
                                       title="User Registration Timeline",
                                       markers=True)
                fig_timeline.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_timeline, use_container_width=True)

    # ----------------------------------------------------------------------
    # TAB 2: Property Verification
    # ----------------------------------------------------------------------
    with tab2:
        st.markdown("### Pending Property Verifications")
        st.markdown("Review and verify properties added by owners to make them visible in the search module.")
        
        pending_df = get_pending_properties()
        
        if not pending_df.empty:
            st.dataframe(pending_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### Action Panel")
            col_action1, col_action2, col_action3 = st.columns([2, 1, 1])
            
            with col_action1:
                selected_prop_id = st.selectbox("Select Property ID to Verify", pending_df['id'].tolist())
            
            with col_action2:
                if st.button("✅ Approve & Verify", type="primary", use_container_width=True):
                    success, msg = run_query("UPDATE properties SET is_verified = 1 WHERE id = ?", (selected_prop_id,))
                    if success:
                        st.success(f"Property ID {selected_prop_id} has been verified and is now live.")
                        st.rerun()
                    else:
                        st.error(msg)
                        
            with col_action3:
                if st.button("❌ Reject & Delete", use_container_width=True):
                    success, msg = run_query("DELETE FROM properties WHERE id = ?", (selected_prop_id,))
                    if success:
                        st.warning(f"Property ID {selected_prop_id} has been rejected and removed.")
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.success("All caught up! No pending properties to verify.")

    # ----------------------------------------------------------------------
    # TAB 3: User Management
    # ----------------------------------------------------------------------
    with tab3:
        st.markdown("### Platform Users")
        users_df = get_all_users()
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True, hide_index=True)
        else:
            st.info("No users found.")

    # ----------------------------------------------------------------------
    # TAB 4: University Management
    # ----------------------------------------------------------------------
    with tab4:
        st.markdown("### Official University Partnerships")
        univ_df = get_universities()
        
        if not univ_df.empty:
            # Map boolean to string for better display
            display_df = univ_df.copy()
            display_df['verified_badge'] = display_df['verified_badge'].map({1: '✅ Active', 0: '⏳ Pending'})
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### Manage Partnership Badges")
            col_u1, col_u2 = st.columns([3, 1])
            with col_u1:
                selected_univ_id = st.selectbox("Select University ID", univ_df['user_id'].tolist())
            with col_u2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Toggle Official Badge", use_container_width=True):
                    current_status = univ_df[univ_df['user_id'] == selected_univ_id]['verified_badge'].values[0]
                    new_status = 0 if current_status == 1 else 1
                    run_query("UPDATE universities SET verified_badge = ? WHERE user_id = ?", (new_status, selected_univ_id))
                    st.success("University badge status updated.")
                    st.rerun()
        else:
            st.info("No registered universities found.")

    render_footer()

if __name__ == "__main__":
    main()
