"""
Authentication module for Clinical Notes Application
"""
import streamlit as st
from typing import Dict, Optional


def get_users() -> Dict[str, str]:
    """Get users from Streamlit secrets or use defaults"""
    try:
        return dict(st.secrets["passwords"])
    except (KeyError, FileNotFoundError):
        return {
            "Dr. Abdelouhab": "Abdel_ouhab",
            "Dr. ACHIKA": "Achi!ka",
            "Dr. AGRANE": "AgraNe",
            "Dr. AOUANOUK": "Aoua_nouk",
            "Dr. BOUDJELEL": "Boudj@lel",
            "Dr. EL MESSRI": "ElMessr!",
            "Dr. HAMDI": "Ham_di",
            "Dr. Himeur": "Hi_meur",
            "Dr. KADRI": "Ka_dri",
            "Dr. Kerkache": "Kerk@che",
            "Dr. Khacef": "Kha_cef",
            "Dr. KORICHI ACHOUAK": "Korichi_A",
            "Dr. KORICHI HICHEM": "Korichi_H",
            "Dr. MOHELLEBI": "Mohelle_bi",
            "Dr. NAIDJI": "Naid_ji",
            "Dr. SAD DJABELLAH": "SadDj!",
            "Dr. SLIMANI": "Sli_mani",
        }


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        "logged_in": False,
        "username": None,
        "recorded_audio": None,
        "card_offset": 0,
        "additional_notes_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
        password = st.text_input("🔑 Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Login", use_container_width=True):
            if USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")


def check_authentication() -> bool:
    return st.session_state.get("logged_in", False)


def get_current_username() -> Optional[str]:
    return st.session_state.get("username", None)