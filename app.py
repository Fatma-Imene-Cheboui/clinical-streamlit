import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

def format_clinical_text(text: str) -> str:
    sections = {
        r"ATCD\s*:": ("<div class='section-header atcd'><span class='emoji'>🟦</span> ATCD:</div>", "#5D9CEC"),
        r"HDM\s*:": ("<div class='section-header hdm'><span class='emoji'>🟪</span> HDM:</div>", "#AC92EC"),
        r"Examen clinique\s*:": ("<div class='section-header exam'><span class='emoji'>🟩</span> Examen clinique:</div>", "#4FC1E9"),
        r"ECG\s*:": ("<div class='section-header ecg'><span class='emoji'>🟥</span> ECG:</div>", "#ED5565"),
        r"ETT des urgences\s*:": ("<div class='section-header ett'><span class='emoji'>🟧</span> ETT des urgences:</div>", "#FC6E51"),
        r"Conduite tenue en salle d'urgence": ("<div class='section-header conduite'><span class='emoji'>🟨</span> Conduite tenue en salle d'urgence</div>", "#FFCE54"),
        r"CAT\s*:": ("<div class='section-header cat'><span class='emoji'>🟫</span> CAT:</div>", "#A0826D"),
    }

    for pattern, (title, color) in sections.items():
        text = re.sub(pattern, title, text, flags=re.IGNORECASE)

    text = text.replace("\n", "<br>")
    return text

# Config
DATA_PATH = "clinical_notes.csv"
AUDIO_DIR = "audios"
os.makedirs(AUDIO_DIR, exist_ok=True)

st.set_page_config(layout="wide", page_title="Clinical Notes", page_icon="🩺")

# Enhanced CSS with smooth animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0 !important;
    }
    
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 100% !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .logout-btn button {
        background: linear-gradient(135deg, #ED5565 0%, #DA4453 100%) !important;
        box-shadow: 0 4px 15px rgba(237, 85, 101, 0.3) !important;
    }
    
    .save-btn button {
        background: linear-gradient(135deg, #48CFAD 0%, #37BC9B 100%) !important;
        box-shadow: 0 4px 15px rgba(72, 207, 173, 0.3) !important;
    }
    
    /* Input fields */
    .stSelectbox, .stTextArea {
        animation: fadeIn 0.5s ease;
    }
    
    .stSelectbox>div>div {
        background: white;
        border-radius: 10px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .stSelectbox>div>div:focus-within {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    .stTextArea textarea {
        border: 2px solid #e8ecf1;
        border-radius: 10px;
        transition: all 0.3s ease;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Login card */
    .login-card {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        animation: slideUp 0.6s ease;
    }
    
    /* Header */
    .header-card {
        background: white;
        border-radius: 15px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        animation: slideDown 0.5s ease;
    }
    
    .header-title {
        color: #667eea;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    
    /* Note sections */
    .note-section {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease;
    }
    
    .note-section:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Section headers in clinical text */
    .section-header {
        font-weight: 700;
        font-size: 16px;
        margin: 1rem 0 0.5rem 0;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        display: inline-block;
        transition: all 0.3s ease;
    }
    
    .section-header .emoji {
        margin-right: 0.5rem;
    }
    
    .atcd { background: rgba(93, 156, 236, 0.1); color: #5D9CEC; }
    .hdm { background: rgba(172, 146, 236, 0.1); color: #AC92EC; }
    .exam { background: rgba(79, 193, 233, 0.1); color: #4FC1E9; }
    .ecg { background: rgba(237, 85, 101, 0.1); color: #ED5565; }
    .ett { background: rgba(252, 110, 81, 0.1); color: #FC6E51; }
    .conduite { background: rgba(255, 206, 84, 0.1); color: #FFCE54; }
    .cat { background: rgba(160, 130, 109, 0.1); color: #A0826D; }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        animation: slideUp 0.4s ease;
        border-radius: 10px;
    }
    
    /* Audio input */
    .stAudioInput {
        animation: fadeIn 0.5s ease;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f3f5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Labels */
    label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #495057 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = pd.read_csv(DATA_PATH, dtype={"audio_file": "string", "transcript": "string", "validated": "boolean"})
df["audio_file"] = df["audio_file"].fillna("")
df["transcript"] = df["transcript"].fillna("")
df["validated"] = df["validated"].fillna(False)

# Users
USERS = {"dr_smith": "password123", "dr_jones": "mypassword"}

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None

# ================= LOGIN =================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class='login-card'>
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='color: #667eea; font-size: 56px; margin: 0;'>🩺</h1>
                <h2 style='color: #2c3e50; margin: 1rem 0 0.5rem 0; font-weight: 700;'>Clinical Notes Review</h2>
                <p style='color: #8492a6; font-size: 16px; margin: 0;'>Secure doctor login portal</p>
            </div>
        """, unsafe_allow_html=True)
        
        username = st.selectbox("👤 Select your account", list(USERS.keys()), label_visibility="visible")
        password = st.text_input("🔒 Password", type="password", label_visibility="visible")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Login", use_container_width=True):
            if USERS.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ================= MAIN APP =================
else:
    # Header
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.markdown(f"""
        <div class='header-card'>
            <h1 class='header-title'>🩺 Clinical Notes Review — {st.session_state.username.replace('_', ' ').title()}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col_h2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Assign notes
    if st.session_state.username == "dr_smith":
        doctor_notes = df.iloc[0:3]
    elif st.session_state.username == "dr_jones":
        doctor_notes = df.iloc[3:7]
    else:
        doctor_notes = pd.DataFrame()

    if doctor_notes.empty:
        st.info("📋 No notes assigned to your account.")
        st.stop()

    # Controls
    c1, c2, c3, c4 = st.columns([3, 3, 1, 1])
    with c1:
        note_ids = doctor_notes["note_id"].tolist()
        selected = st.selectbox("📝 Select Clinical Note", note_ids)

    note = doctor_notes[doctor_notes["note_id"] == selected].iloc[0]

    with c2:
        audio = st.audio_input("🎤 Record Audio Note")
    
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='save-btn'>", unsafe_allow_html=True)
        if audio and st.button("💾", use_container_width=True):
            st.session_state.pending_audio = audio
        st.markdown("</div>", unsafe_allow_html=True)

    # Save audio
    if st.session_state.pending_audio:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{AUDIO_DIR}/{selected}_{timestamp}.wav"
        with open(filename, "wb") as f:
            f.write(st.session_state.pending_audio.getbuffer())
        df.loc[df["note_id"] == selected, "audio_file"] = filename
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Audio saved successfully!")
        st.session_state.pending_audio = None

    st.markdown("<br>", unsafe_allow_html=True)

    # Three column layout
    col1, col2, col3 = st.columns([1, 1, 1])

    formatted_text = format_clinical_text(note["raw_text"])
    lines = formatted_text.split("<br>")
    chunk_size = max(1, len(lines) // 3)
    
    sections = [
        "<br>".join(lines[:chunk_size]),
        "<br>".join(lines[chunk_size:chunk_size*2]),
        "<br>".join(lines[chunk_size*2:])
    ]

    with col1:
        st.markdown(f"""
        <div class='note-section' style='max-height: 500px; overflow-y: auto;'>
            {sections[0]}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='note-section' style='max-height: 500px; overflow-y: auto;'>
            {sections[1]}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='note-section' style='max-height: 500px; overflow-y: auto;'>
            {sections[2]}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Transcription
    transcript = st.text_area("📋 Additional Notes ", note["transcript"], height=150)

    st.markdown("<div class='save-btn'>", unsafe_allow_html=True)
    if st.button("💾 Save & Validate Transcription", use_container_width=True):
        df.loc[df["note_id"] == selected, "transcript"] = transcript
        df.loc[df["note_id"] == selected, "validated"] = True
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Transcription saved and validated!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)