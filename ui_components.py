"""
UI components for Clinical Notes Application
"""

import streamlit as st
from datetime import datetime
from typing import List
import time

from config import VISIBLE_CARDS
from utils import safe_filename, upload_audio_file, upload_notes_file
from data_handler import update_audio_file, update_additional_notes, save_data

import streamlit as st

st.markdown(
    """
    <script>
    (function() {
        function updateIsMobile() {
            const isMobile = window.innerWidth <= 768;
            const streamlitDoc = window.parent.document;
            let input = streamlitDoc.getElementById("is_mobile");

            if (!input) {
                input = streamlitDoc.createElement("input");
                input.type = "hidden";
                input.id = "is_mobile";
                streamlitDoc.body.appendChild(input);
            }

            input.value = isMobile;

            // Notify Streamlit about the change
            fetch(window.location.href + `?is_mobile=${isMobile}`, {
                method: "GET"
            });
        }

        // Initial detection
        updateIsMobile();

        // Update on resize
        window.addEventListener("resize", updateIsMobile);
    })();
    </script>
    """,
    unsafe_allow_html=True
)

# Update session state based on query parameters
query_params = st.query_params
if "is_mobile" in query_params:
    st.session_state.is_mobile = query_params["is_mobile"][0] == "true"
else:
    st.session_state.is_mobile = False

def is_mobile():
    return st.session_state.get("is_mobile", False)

def init_session_state():
    """Initialize session state variables"""
    if "recorded_audio" not in st.session_state:
        st.session_state.recorded_audio = None

    if "audio_saved_msg" not in st.session_state:
        st.session_state.audio_saved_msg = None
    
    if "audio_saved_time" not in st.session_state:
        st.session_state.audio_saved_time = None

    if "notes_saved_msg" not in st.session_state:
        st.session_state.notes_saved_msg = None
    
    if "notes_saved_time" not in st.session_state:
        st.session_state.notes_saved_time = None

    if "additional_notes_text" not in st.session_state:
        st.session_state.additional_notes_text = ""

    if "card_offset" not in st.session_state:
        st.session_state.card_offset = 0


def render_note_selector(doctor_notes, username: str) -> str:
    """Render note selection dropdown"""
    note_ids = doctor_notes["note_id"].tolist()
    return st.selectbox(
        f"📝 Select Clinical Note — {username}",
        note_ids
    )


def render_audio_recorder():
    """Render audio recording input"""
    audio = st.audio_input("🎤 Record audio", key="audio_input")

    if audio is not None:
        st.session_state.recorded_audio = audio.getvalue()


def render_save_audio_button(selected_note_id: str, username: str, df):
    """Render save audio button and handle upload"""
    init_session_state()

    recorded_audio = st.session_state.get("recorded_audio")

    if st.button("💾 Save Audio", use_container_width=True):

        if not recorded_audio:
            st.warning("⚠️ No audio recorded")
            return

        safe_doctor_name = safe_filename(username)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio/{safe_doctor_name}_{selected_note_id}_{timestamp}.wav"

        try:
            _, link = upload_audio_file(filename, recorded_audio)

            update_audio_file(df, selected_note_id, link)
            save_data(df)

            st.session_state.audio_saved_msg = link
            st.session_state.audio_saved_time = time.time()
            st.session_state.recorded_audio = None

            st.rerun()

        except Exception as e:
            st.error(f"❌ Save failed: {e}")

    # Display success message if within 3 seconds
    msg = st.session_state.get("audio_saved_msg")
    msg_time = st.session_state.get("audio_saved_time")
    
    if msg and msg_time:
        elapsed = time.time() - msg_time
        if elapsed < 3:
            st.success("✅ Audio saved successfully")
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.audio_saved_msg = None
            st.session_state.audio_saved_time = None


def render_content_cards(sections):
    init_session_state()
    num_cards = len(sections)

    # ===== MOBILE =====
    if is_mobile():
        for section in sections:
            st.markdown(
                f"<div class='note-section mobile-card'>{section}</div>",
                unsafe_allow_html=True
            )
        return

    # ===== DESKTOP =====
    if num_cards > VISIBLE_CARDS:
        nav_col1, _, nav_col3 = st.columns([1, 6, 1])

        with nav_col1:
            if st.button("◀", disabled=st.session_state.card_offset == 0):
                st.session_state.card_offset -= 1
                st.rerun()

        with nav_col3:
            max_offset = num_cards - VISIBLE_CARDS
            if st.button("▶", disabled=st.session_state.card_offset >= max_offset):
                st.session_state.card_offset += 1
                st.rerun()

    start = st.session_state.card_offset
    end = start + VISIBLE_CARDS

    cols = st.columns(VISIBLE_CARDS)
    for col, section in zip(cols, sections[start:end]):
        with col:
            st.markdown(
                f"<div class='note-section desktop-card'>{section}</div>",
                unsafe_allow_html=True
            )



def render_additional_notes(selected_note_id: str, username: str, df):
    """Render additional notes text area and save button"""
    init_session_state()

    st.markdown("<br>", unsafe_allow_html=True)
    col_note1, col_note2 = st.columns([3, 1])

    with col_note1:
        notes_text = st.text_area(
            "📝 Additional Notes",
            value=st.session_state.additional_notes_text,
            height=100
        )
        st.session_state.additional_notes_text = notes_text

    with col_note2:
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("💾 Save Notes", use_container_width=True):

            if not notes_text.strip():
                st.warning("⚠️ Please enter some notes first")
                return

            safe_doctor_name = safe_filename(username)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"notes/{safe_doctor_name}_{selected_note_id}_notes_{timestamp}.txt"

            try:
                _, link = upload_notes_file(filename, notes_text.encode("utf-8"))

                update_additional_notes(df, selected_note_id, link)
                save_data(df)

                st.session_state.notes_saved_msg = link
                st.session_state.notes_saved_time = time.time()
                st.session_state.additional_notes_text = ""

                st.rerun()

            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

    # Display success message if within 3 seconds
    msg = st.session_state.get("notes_saved_msg")
    msg_time = st.session_state.get("notes_saved_time")
    
    if msg and msg_time:
        elapsed = time.time() - msg_time
        if elapsed < 3:
            st.success("✅ Notes saved successfully")
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.notes_saved_msg = None
            st.session_state.notes_saved_time = None