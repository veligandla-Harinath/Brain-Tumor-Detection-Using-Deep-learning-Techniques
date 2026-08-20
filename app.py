import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os
import hashlib
import json

st.set_page_config(page_title="Brain Tumor Detection")

# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

# Simple user database (in production, use a real database)
USERS_DB_FILE = "users_db.json"

def load_users_db():
    """Load users from JSON file"""
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, "r") as f:
            return json.load(f)
    else:
        # Default users
        default_db = {
            "admin": hashlib.sha256("admin123".encode()).hexdigest(),
            "user": hashlib.sha256("user123".encode()).hexdigest(),
        }
        save_users_db(default_db)
        return default_db

def save_users_db(users_dict):
    """Save users to JSON file"""
    with open(USERS_DB_FILE, "w") as f:
        json.dump(users_dict, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup_page():
    """Display signup page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🧠 Brain Tumor Detection")
        st.write("---")
        st.subheader("Create New Account")
        
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Sign Up", use_container_width=True):
                users_db = load_users_db()
                
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif len(new_username) < 3:
                    st.error("Username must be at least 3 characters")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif new_username in users_db:
                    st.error("Username already exists. Choose a different one.")
                else:
                    users_db[new_username] = hash_password(new_password)
                    save_users_db(users_db)
                    st.success("Account created successfully! Please login.")
                    st.session_state.show_signup = False
                    st.rerun()
        
        with col_b:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.show_signup = False
                st.rerun()

def login_page():
    """Display login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🧠 Brain Tumor Detection")
        st.write("---")
        st.subheader("Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Login", use_container_width=True):
                users_db = load_users_db()
                if username in users_db and users_db[username] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col_b:
            if st.button("Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()
        
        st.markdown("---")
        st.write("**Demo Credentials:**")
        st.write("- Username: `admin` | Password: `admin123`")
        st.write("- Username: `user` | Password: `user123`")

def main_app():
    """Display main application"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("🧠 Brain Tumor Detection using deeplearning")
    
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    
    st.write(f"Welcome, **{st.session_state.username}**!")
    st.write("Upload an MRI image to detect tumors.")
    st.write("---")
    
    @st.cache_resource
    def load_model():
        return YOLO("best.pt")
    
    model = load_model()
    
    uploaded_file = st.file_uploader("Upload MRI Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
    
        if st.button("Detect Tumor"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                image.save(tmp.name)
                temp_path = tmp.name
    
            results = model(temp_path, conf=0.5)
            st.image(results[0].plot(), caption="Detection Result", use_container_width=True)
    
            os.remove(temp_path)

# Main application logic
if st.session_state.logged_in:
    main_app()
elif st.session_state.show_signup:
    signup_page()
else:
    login_page()
