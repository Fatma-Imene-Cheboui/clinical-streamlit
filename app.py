"""
Main application file for Clinical Notes Recording System
"""
import streamlit as st
from utils import create_directories
from auth import initialize_session_state, render_login_page, check_authentication, get_current_username
from data_handler import load_data, get_doctor_notes, get_note_by_id
from text_formatter import format_clinical_text, split_content_dynamically
from ui_components import (
    render_note_selector,
    render_audio_recorder,
    render_save_audio_button,
    render_content_cards,
    render_additional_notes
)
from styles import MAIN_STYLES


def main():
    """Main application entry point"""
    st.set_page_config(
        layout="wide",
        page_title="Clinical Notes",
        page_icon="🩺"
    )
    
    st.markdown(MAIN_STYLES, unsafe_allow_html=True)
    
    create_directories()
    initialize_session_state()
    
    if not check_authentication():
        render_login_page()
        return
    
    df = load_data()
    username = get_current_username()
    
    doctor_notes = get_doctor_notes(df, username)
    
    if doctor_notes.empty:
        st.info("📋 No notes assigned to your account.")
        return
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 2, 1])
    
    with c1:
        selected = render_note_selector(doctor_notes, username)
    
    with c2:
        render_audio_recorder()

    with c3:
        render_save_audio_button(selected, username, df)
    
    note = get_note_by_id(doctor_notes, selected)
    if note is None:
        st.error("Note not found!")
        return
    
    formatted_text = format_clinical_text(note["raw_text"])
    sections = split_content_dynamically(formatted_text, max_height=500)
    render_content_cards(sections)
    
    render_additional_notes(selected, username, df)
    
    st.markdown("<br>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()