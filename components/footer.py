import streamlit as st

def render_footer():
    """Renders the professional footer at the bottom of the application."""
    st.markdown("---")
    
    footer_html = """
    <div style="text-align: center; padding: 2rem 0; color: var(--text-sub);">
        <h4>🏠 StayNest</h4>
        <p>Verified Student Housing & Brokerage-Free Rentals</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0;">
            <a href="#" style="color: var(--accent); text-decoration: none;">About Us</a>
            <a href="#" style="color: var(--accent); text-decoration: none;">Contact</a>
            <a href="#" style="color: var(--accent); text-decoration: none;">Privacy Policy</a>
            <a href="#" style="color: var(--accent); text-decoration: none;">Terms of Service</a>
        </div>
        <p style="font-size: 0.875rem;">© 2026 StayNest. All rights reserved.</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
