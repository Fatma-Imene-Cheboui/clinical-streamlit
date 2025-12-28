"""
Authentication module for Clinical Notes Application
"""
import streamlit as st
from typing import Dict, Optional


def get_users() -> Dict[str, str]:
    """Get users from Streamlit secrets or use defaults"""
    try:
        return {
            "Dr. Smith": st.secrets["passwords"]["dr_smith"],
            "Dr. Jhones": st.secrets["passwords"]["dr_jones"]
        }
    except:
        return {
            "Dr. Smith": "password123",
            "Dr. Jhones": "mypassword"
        }


def initialize_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "recorded_audio" not in st.session_state:
        st.session_state.recorded_audio = None
    if "card_offset" not in st.session_state:
        st.session_state.card_offset = 0
    if "additional_notes_text" not in st.session_state:
        st.session_state.additional_notes_text = ""


def render_login_page():
    """Render the login page"""
    USERS = get_users()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: #667eea; font-size: 56px; margin: 0;'>🩺</h1>
            <h2 class="login-title">Clinical Notes Recording</h2>
            <p style='color: #8492a6; font-size: 16px; margin: 0;'>Doctor login portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.selectbox("👤 Select your account", list(USERS.keys()))
        password = st.text_input("🔒 Password", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Login", use_container_width=True):
            if USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")


def check_authentication() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("logged_in", False)


def get_current_username() -> Optional[str]:
    """Get current logged in username"""
    return st.session_state.get("username", None)