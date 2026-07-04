import streamlit as st
from utils.auth import authenticate_user, login_user, register_user

def render_login_form():
    """Renders the login form and handles authentication logic."""
    st.markdown("### Welcome Back")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                user = authenticate_user(email, password)
                if user:
                    login_user(user)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

def render_registration_form():
    """Renders the multi-role registration form."""
    st.markdown("### Create an Account")
    
    role = st.selectbox("I am a:", ["Student", "Property Owner", "University Representative"])
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        st.markdown("#### Profile Details")
        full_name = st.text_input("Full Name / Organization Name")
        phone = st.text_input("Phone Number")
        
        # Additional fields based on role
        if role == "Student":
            st.caption("We will ask for university details and preferences later in your dashboard.")
        elif role == "Property Owner":
            company_name = st.text_input("Company Name (Optional)")
        elif role == "University Representative":
            domain = st.text_input("Official University Domain (e.g., univ.edu)")
            
        submit = st.form_submit_button("Register", use_container_width=True)
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match.")
            elif not all([username, email, password, full_name]):
                st.error("Please fill in all required fields.")
            else:
                role_key = "student" if role == "Student" else "owner" if role == "Property Owner" else "university"
                
                profile_data = {
                    "full_name": full_name,
                    "name": full_name, # Mapping for university
                    "phone": phone
                }
                
                if role == "Property Owner":
                    profile_data["company_name"] = company_name
                elif role == "University Representative":
                    profile_data["domain"] = domain
                
                success, msg = register_user(username, email, password, role_key, profile_data)
                
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
