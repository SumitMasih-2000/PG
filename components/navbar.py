import streamlit as st
from utils.auth import is_authenticated, get_current_user, logout_user

def render_navbar():
    """Renders the top navigation and user status bar."""
    st.markdown('<div class="animate-slide-up">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 🏠 StayNest")
        
    with col2:
        # Placeholder for centralized search or quick links if needed in future
        pass
        
    with col3:
        if is_authenticated():
            user = get_current_user()
            st.markdown(f"**Welcome, {user['username']}** ({user['role'].capitalize()})")
            if st.button("Logout", key="nav_logout", use_container_width=True):
                logout_user()
        else:
            st.markdown("**Welcome to StayNest!**")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
