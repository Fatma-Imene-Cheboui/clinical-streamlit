"""
UI components for Clinical Notes Application
"""
import streamlit as st
import base64
import os
from datetime import datetime
from typing import List
from config import VISIBLE_CARDS, AUDIO_DIR, NOTES_DIR, DRIVE_AUDIO_FOLDER_ID, DRIVE_NOTES_FOLDER_ID
from utils import safe_filename, authenticate_drive, upload_file_to_drive
from data_handler import update_audio_file, update_additional_notes, save_data

st.session_state.setdefault("audio_saved_msg", None)
st.session_state.setdefault("notes_saved_msg", None)

def render_note_selector(doctor_notes, username: str) -> str:
    """Render note selection dropdown"""
    note_ids = doctor_notes["note_id"].tolist()
    selected = st.selectbox(
        f"📝 Select Clinical Note — {username}",
        note_ids
    )
    return selected


def render_audio_recorder():

    audio = st.audio_input(
        "🎤 Record audio",
        key="audio_input"
    )

    if audio is not None:
        st.session_state.recorded_audio = audio.getvalue()


def render_save_audio_button(selected_note_id: str, username: str, df):
    recorded_audio = st.session_state.get("recorded_audio")


    if st.button("💾 Save Audio", use_container_width=True):
        safe_doctor_name = safe_filename(username)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_doctor_name}_{selected_note_id}_{timestamp}.wav"

        try:
            service = authenticate_drive()
            _, link = upload_file_to_drive(
                service,
                filename,
                recorded_audio,
                DRIVE_AUDIO_FOLDER_ID,
                "audio/wav"
            )

            update_audio_file(df, selected_note_id, link)
            save_data(df)

            # ✅ persist message
            st.session_state.audio_saved_msg = (
                f"✅ Audio saved successfully\n\n{link}"
            )

            st.session_state.recorded_audio = None
            st.rerun()

        except Exception as e:
            st.error(f"❌ Save failed: {e}")

    # ✅ render message AFTER rerun
    if st.session_state.audio_saved_msg:
        st.success("Audio saved")


def render_content_cards(sections: List[str]):
    """Render content display cards with navigation"""
    num_cards = len(sections)
    
    if num_cards > VISIBLE_CARDS:
        nav_col1, nav_col2, nav_col3 = st.columns([1, 6, 1])
        
        with nav_col1:
            if st.button("◀", key="prev_card", disabled=st.session_state.card_offset == 0):
                st.session_state.card_offset = max(0, st.session_state.card_offset - 1)
                st.rerun()
        
        with nav_col3:
            max_offset = num_cards - VISIBLE_CARDS
            if st.button("▶", key="next_card", disabled=st.session_state.card_offset >= max_offset):
                st.session_state.card_offset = min(max_offset, st.session_state.card_offset + 1)
                st.rerun()
    
    start_idx = st.session_state.card_offset
    end_idx = min(start_idx + VISIBLE_CARDS, num_cards)
    visible_sections = sections[start_idx:end_idx]
    
    cols = st.columns(len(visible_sections))
    for col, section in zip(cols, visible_sections):
        with col:
            st.markdown(
                f"<div class='note-section'>{section}</div>",
                unsafe_allow_html=True
            )


def render_additional_notes(selected_note_id: str, username: str, df):
    st.markdown("<br>", unsafe_allow_html=True)
    col_note1, col_note2 = st.columns([3, 1])

    with col_note1:
        notes_text = st.text_area(
            "📝 **Additional Notes**",
            value=st.session_state.get("additional_notes_text", ""),
            height=100,
            key="notes_area"
        )
        st.session_state.additional_notes_text = notes_text

    with col_note2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Notes", use_container_width=True):
            if not notes_text.strip():
                st.warning("⚠️ Please enter some notes first")
                return

            safe_doctor_name = safe_filename(username)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_doctor_name}_{selected_note_id}_notes_{timestamp}.txt"
            notes_bytes = notes_text.encode('utf-8')

            try:
                service = authenticate_drive()
                _, link = upload_file_to_drive(
                    service,
                    filename,
                    notes_bytes,
                    DRIVE_NOTES_FOLDER_ID,
                    'text/plain'
                )

                update_additional_notes(df, selected_note_id, link)
                save_data(df)

                # ✅ persist message
                st.session_state.notes_saved_msg = (
                    f"✅ Notes saved successfully\n\n{link}"
                )

                st.session_state.additional_notes_text = ""
                st.rerun()

            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

    # ✅ render message AFTER rerun
    if st.session_state.notes_saved_msg:
        st.success("Notes saved")
