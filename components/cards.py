import streamlit as st

def render_property_card(property_data: dict, key_suffix: str = ""):
    """
    Renders a premium glassmorphism card for a property.
    Uses HTML for the visual layout and Streamlit elements for interactions.
    """
    verified_badge = '<span class="badge-verified">✓ Verified</span>' if property_data.get('is_verified') else ''
    
    card_html = f"""
    <div class="glass-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h3 style="margin: 0 0 0.5rem 0;">{property_data.get('title', 'Property Title')}</h3>
                <p style="color: var(--text-sub); margin: 0 0 1rem 0;">
                    📍 {property_data.get('city', 'City')} | {property_data.get('property_type', 'Type')}
                </p>
            </div>
            {verified_badge}
        </div>
        <h2 style="color: var(--accent); margin: 0 0 1rem 0;">₹{property_data.get('price', 0):,}<span style="font-size: 1rem; color: var(--text-sub); font-weight: 400;">/month</span></h2>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <span style="background: var(--background); padding: 0.25rem 0.5rem; border-radius: var(--radius-md); font-size: 0.875rem;">
                Distance to Univ: {property_data.get('distance_to_univ', 'N/A')} km
            </span>
            <span style="background: var(--background); padding: 0.25rem 0.5rem; border-radius: var(--radius-md); font-size: 0.875rem;">
                For: {property_data.get('gender_allowed', 'Any')}
            </span>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Render interactive buttons below the HTML card
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Details", key=f"view_{property_data.get('id')}_{key_suffix}", use_container_width=True):
            st.session_state['viewing_property_id'] = property_data.get('id')
            st.switch_page("pages/1_🔍_Search.py")
            
    with col2:
        if st.button("Save", key=f"save_{property_data.get('id')}_{key_suffix}", use_container_width=True):
            st.toast(f"Saved {property_data.get('title')} to Wishlist!")

def render_metric_card(title: str, value: str, icon: str = "📊"):
    """Renders a simple dashboard metric card."""
    html = f"""
    <div class="glass-card" style="text-align: center; padding: 1.5rem 1rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="color: var(--text-sub); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">{title}</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">{value}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
