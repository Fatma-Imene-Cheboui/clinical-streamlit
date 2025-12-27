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

:root {
    --bg-main: #f4f6fb;
    --bg-card: #ffffff;
    --text-main: #2c3e50;
    --text-muted: #8492a6;
}
.login-title {
    color: var(--text-main);
    margin: 1rem 0 0.5rem 0;
    font-weight: 700;
}


@media (prefers-color-scheme: dark) {
    :root {
        --bg-main: #0e1117;
        --bg-card: #1e222a;
        --text-main: #e6e9ef;
        --text-muted: #a0a4ab;
    }
}

* {
    font-family: 'Inter', sans-serif;
}

.main {
    background: var(--bg-main);
}

.block-container {
    padding: 1.5rem 2rem !important;
}

/* Cards */
.login-card,
.note-section {
    background: var(--bg-card);
    color: var(--text-main);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}
.header-card{
    background: var(--bg-card);
    color: var(--text-main);
    border-radius: 16px;
    padding-left: 1.5rem;
    padding-top: 0.5rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-2px);
}

/* Inputs */
.stSelectbox>div>div,
.stTextArea textarea {
    background: var(--bg-card);
    color: var(--text-main);
    border-radius: 10px;
    border: 1px solid rgba(150,150,150,0.3);
}

/* Labels */
label, .stMarkdown {
    color: var(--text-main) !important;
}

/* Section headers */
.section-header {
    font-weight: 700;
    padding: 0.5rem 0.8rem;
    margin: 1rem 0;
    border-radius: 8px;
    display: inline-block;
}

.atcd { color:#5D9CEC; background:rgba(93,156,236,0.15); }
.hdm { color:#AC92EC; background:rgba(172,146,236,0.15); }
.exam { color:#4FC1E9; background:rgba(79,193,233,0.15); }
.ecg { color:#ED5565; background:rgba(237,85,101,0.15); }
.ett { color:#FC6E51; background:rgba(252,110,81,0.15); }
.conduite { color:#FFCE54; background:rgba(255,206,84,0.2); }
.cat { color:#A0826D; background:rgba(160,130,109,0.2); }

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 10px;
}
@media (max-width: 768px) {
    .note-section {
        max-height: none !important;
        overflow: visible !important;
        margin-bottom: 0.5rem !important;
        padding: 0.8rem !important;
    }

    /* Reduce space between columns */
    div[data-testid="column"] {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
}
@media (max-width: 768px) {
    .block-container {
        padding: 0.8rem !important;
    }
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
        <div>
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='color: #667eea; font-size: 56px; margin: 0;'>🩺</h1>
                <h2 class="login-title"> Clinical Notes Recording</h2>
                <p style='color: #8492a6; font-size: 16px; margin: 0;'>Doctor login portal</p>
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
            <h1 class='header-title'>🩺 Clinical Notes Recording — {st.session_state.username.replace('_', ' ').title()}</h1>
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
        <div class='note-section' style='max-height: 550px; overflow-y: auto;'>
            {sections[0]}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='note-section' style='max-height: 550px; overflow-y: auto;'>
            {sections[1]}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='note-section' style='max-height: 550px; overflow-y: auto;'>
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