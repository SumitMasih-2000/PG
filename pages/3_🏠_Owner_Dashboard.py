import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import require_role, get_current_user
from database.connection import fetch_all, fetch_one, run_query
from components.navbar import render_navbar
from components.footer import render_footer
from components.cards import render_property_card, render_metric_card

# ==========================================================================
# Page Configuration & Protection
# ==========================================================================
st.set_page_config(page_title="Owner Dashboard | StayNest", page_icon="🏠", layout="wide")

# Load Custom CSS
try:
    with open("assets/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Ensure only logged-in owners (or admins) can access this page
require_role('owner')
current_user = get_current_user()
owner_id = current_user['id']

# ==========================================================================
# Data Fetching Helpers
# ==========================================================================
def get_owner_profile():
    return fetch_one("SELECT * FROM owners WHERE user_id = ?", (owner_id,))

def get_my_properties():
    return fetch_all("SELECT * FROM properties WHERE owner_id = ? ORDER BY created_at DESC", (owner_id,))

def get_universities():
    return fetch_all("SELECT user_id, name FROM universities WHERE verified_badge = 1")

def get_property_bookings():
    query = """
        SELECT b.id as booking_id, p.title as property_name, u.username as student_name, 
               b.visit_date, b.status, b.created_at
        FROM bookings b
        JOIN properties p ON b.property_id = p.id
        JOIN users u ON b.student_id = u.id
        WHERE p.owner_id = ?
        ORDER BY b.created_at DESC
    """
    return fetch_all(query, (owner_id,), as_dataframe=True)

# ==========================================================================
# Main Dashboard Layout
# ==========================================================================
def main():
    render_navbar()
    
    profile = get_owner_profile()
    name = profile['full_name'] if profile else current_user['username']
    company = f" ({profile['company_name']})" if profile and profile.get('company_name') else ""
    
    st.markdown(f"<h1 class='animate-slide-up'>Welcome back, {name}{company} 🏠</h1>", unsafe_allow_html=True)
    st.markdown("Manage your properties, track bookings, and grow your rental business.")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Analytics & Overview", 
        "🏢 My Listings", 
        "➕ Add New Property", 
        "📅 Visit Requests"
    ])
    
    # ----------------------------------------------------------------------
    # TAB 1: Analytics & Overview
    # ----------------------------------------------------------------------
    with tab1:
        properties = get_my_properties()
        bookings_df = get_property_bookings()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Total Properties", str(len(properties)), "🏢")
        with col2:
            total_requests = len(bookings_df) if not bookings_df.empty else 0
            render_metric_card("Total Visit Requests", str(total_requests), "👀")
        with col3:
            approved_reqs = len(bookings_df[bookings_df['status'] == 'Approved']) if not bookings_df.empty else 0
            render_metric_card("Approved Visits", str(approved_reqs), "✅")
            
        st.markdown("---")
        st.markdown("### Portfolio Analytics")
        
        if not bookings_df.empty:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Group bookings by property
                prop_bookings = bookings_df.groupby('property_name').size().reset_index(name='requests')
                fig1 = px.bar(prop_bookings, x='property_name', y='requests', 
                              title="Visit Requests per Property",
                              color_discrete_sequence=['#2563EB'])
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, use_container_width=True)
                
            with col_chart2:
                # Group by status
                status_counts = bookings_df.groupby('status').size().reset_index(name='count')
                fig2 = px.pie(status_counts, names='status', values='count', 
                              title="Request Status Distribution",
                              color='status',
                              color_discrete_map={'Approved':'#22C55E', 'Pending':'#F59E0B', 'Rejected':'#EF4444'})
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Not enough data to generate analytics. Add properties and wait for student requests!")

    # ----------------------------------------------------------------------
    # TAB 2: My Listings
    # ----------------------------------------------------------------------
    with tab2:
        st.markdown("### Manage Your Properties")
        if properties:
            for idx, prop in enumerate(properties):
                col1, col2 = st.columns([3, 1])
                with col1:
                    render_property_card(prop, key_suffix=f"owner_{idx}")
                with col2:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.info("Status: " + ("✅ Verified" if prop['is_verified'] else "⏳ Pending Verification"))
                    if st.button("Edit Listing", key=f"edit_{prop['id']}", use_container_width=True):
                        st.toast("Edit functionality would launch a modal here.")
                    if st.button("Delete", key=f"del_{prop['id']}", type="primary", use_container_width=True):
                        st.toast("Contact Admin to delete a verified listing.")
                st.markdown("---")
        else:
            st.info("You haven't listed any properties yet.")

    # ----------------------------------------------------------------------
    # TAB 3: Add New Property
    # ----------------------------------------------------------------------
    with tab3:
        st.markdown("### List a New Property")
        st.markdown("Add details below. All new properties must be verified by StayNest admins before appearing in search.")
        
        universities = get_universities()
        univ_options = {u['name']: u['user_id'] for u in universities}
        
        with st.form("add_property_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Property Title*", placeholder="e.g., Luxury Boys PG near North Campus")
                property_type = st.selectbox("Property Type*", ["PG", "Flat", "Hostel"])
                city = st.selectbox("City*", ["Delhi", "Mumbai", "Bengaluru", "Pune", "Chennai"])
                price = st.number_input("Monthly Rent (₹)*", min_value=1000, max_value=200000, step=500)
                
            with col2:
                gender_allowed = st.selectbox("Tenant Preference*", ["Boys", "Girls", "Any"])
                address = st.text_area("Complete Address*", height=100)
                nearest_univ_name = st.selectbox("Nearest University", ["None"] + list(univ_options.keys()))
                distance_to_univ = st.number_input("Distance to University (km)", min_value=0.0, max_value=50.0, step=0.1)

            st.markdown("#### Amenities Included")
            amenity_cols = st.columns(6)
            food = amenity_cols[0].checkbox("Food")
            wifi = amenity_cols[1].checkbox("WiFi")
            ac = amenity_cols[2].checkbox("AC")
            laundry = amenity_cols[3].checkbox("Laundry")
            parking = amenity_cols[4].checkbox("Parking")
            security = amenity_cols[5].checkbox("CCTV/Security")
            
            description = st.text_area("Property Description", placeholder="Highlight the best features of your property...")
            
            submitted = st.form_submit_button("Submit for Verification", type="primary", use_container_width=True)
            
            if submitted:
                if not title or not address or not city or not price:
                    st.error("Please fill in all required fields marked with *")
                else:
                    univ_id = univ_options.get(nearest_univ_name) if nearest_univ_name != "None" else None
                    
                    insert_query = """
                        INSERT INTO properties 
                        (owner_id, title, description, address, city, price, property_type, gender_allowed, 
                         food, wifi, ac, laundry, parking, security, distance_to_univ, nearest_university_id, is_verified)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """
                    params = (
                        owner_id, title, description, address, city, price, property_type, gender_allowed,
                        food, wifi, ac, laundry, parking, security, distance_to_univ, univ_id
                    )
                    
                    success, msg = run_query(insert_query, params)
                    if success:
                        st.success("Property added successfully! It is now pending admin verification.")
                        st.rerun()
                    else:
                        st.error(f"Error adding property: {msg}")

    # ----------------------------------------------------------------------
    # TAB 4: Visit Requests (Bookings)
    # ----------------------------------------------------------------------
    with tab4:
        st.markdown("### Manage Student Visit Requests")
        if not bookings_df.empty:
            st.dataframe(
                bookings_df[['booking_id', 'property_name', 'student_name', 'visit_date', 'status', 'created_at']],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("#### Update Request Status")
            action_col1, action_col2, action_col3 = st.columns([2, 1, 1])
            with action_col1:
                selected_booking = st.selectbox("Select Booking ID", bookings_df['booking_id'].tolist())
            with action_col2:
                if st.button("Approve Request", type="primary", use_container_width=True):
                    run_query("UPDATE bookings SET status = 'Approved' WHERE id = ?", (selected_booking,))
                    st.success(f"Booking {selected_booking} Approved!")
                    st.rerun()
            with action_col3:
                if st.button("Reject Request", use_container_width=True):
                    run_query("UPDATE bookings SET status = 'Rejected' WHERE id = ?", (selected_booking,))
                    st.warning(f"Booking {selected_booking} Rejected.")
                    st.rerun()
        else:
            st.info("No visit requests pending for your properties.")

    render_footer()

if __name__ == "__main__":
    main()
