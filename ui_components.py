"""
UI components for Clinical Notes Application
"""

import streamlit as st
from datetime import datetime
import time
from typing import List

from utils import (
    safe_filename,
    upload_audio_file,
    upload_notes_file,
    get_supabase_client,
)

# -------------------------------------------------
# Session state
# -------------------------------------------------

def init_session_state():
    defaults = {
        "recorded_audio": None,
        "additional_notes_text": "",
        "selected_patient_id": None,
        "audio_saved_msg": None,
        "notes_saved_msg": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -------------------------------------------------
# Supabase helpers
# -------------------------------------------------

def get_patient_activity(patient_id: int):
    """Get activity record for a patient from Supabase"""
    try:
        supabase = get_supabase_client()
        resp = (
            supabase
            .table("clinical_activity")
            .select("audio_path, notes_path")
            .eq("patient_id", str(patient_id))
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def patient_is_completed(patient_id: int) -> bool:
    """Check if patient has audio completed (notes not required)"""
    activity = get_patient_activity(patient_id)
    if not activity:
        return False

    # Only check for audio - notes are optional
    # There might be multiple records if multiple doctors, so check any
    has_audio = any(
        bool(record.get("audio_path") and len(str(record.get("audio_path", "")).strip()) > 0)
        for record in activity
    )
    
    return has_audio


# -------------------------------------------------
# Patient selector (Supabase-driven checkmarks)
# -------------------------------------------------

def render_patient_selector(doctor_notes, username: str) -> int:
    """Render patient selector with completion status from Supabase"""
    init_session_state()

    patient_ids = sorted(doctor_notes["patientId"].unique().tolist())
    options = []

    for pid in patient_ids:
        row = doctor_notes[doctor_notes["patientId"] == pid].iloc[0]
        motif = row.get("motif", "Unknown")
        motif_short = motif.split()[0] if motif else "Unknown"

        completed = patient_is_completed(pid)
        icon = "✅" if completed else "⭕"
        options.append(f"{icon} Patient {pid} ({motif_short})")

    label_to_id = {label: pid for label, pid in zip(options, patient_ids)}

    selected_label = st.selectbox(
        f"👤 Select Patient — {username}",
        options,
        key="patient_selector"
    )

    selected_id = label_to_id[selected_label]
    st.session_state.selected_patient_id = selected_id
    return selected_id


# -------------------------------------------------
# Audio recording + save
# -------------------------------------------------

def render_audio_recorder():
    """Render audio input widget"""
    audio = st.audio_input("🎤 Record audio")
    if audio:
        st.session_state.recorded_audio = audio.getvalue()


def render_save_audio_button(patient_id: int, username: str, df):
    """Save audio file to Supabase storage and track in database"""
    init_session_state()
    supabase = get_supabase_client()
    audio_bytes = st.session_state.recorded_audio

    if st.button("💾 Save Audio", use_container_width=True):

        if not audio_bytes:
            st.warning("⚠️ No audio recorded")
            return

        # Get patient info
        row = df[df["patientId"] == patient_id].iloc[0]
        motif = row.get("motif", "unknown")
        note_id = row.get("note_id", "unknown")

        # Build filename with FOLDER included
        safe_doctor = safe_filename(username)
        safe_motif = safe_filename(motif)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = (
            f"{safe_doctor}_"
            f"patient{patient_id}_"
            f"{safe_motif}_"
            f"{note_id}_.wav"
        )
        
        # IMPORTANT: Include folder in the path passed to upload
        full_path = f"audio/{filename}"

        try:
            # Upload to Supabase storage
            _, public_url = upload_audio_file(full_path, audio_bytes)

            # Upsert into clinical_activity table
            # Supabase will handle upsert based on primary key (patient_id, doctor_username)
            supabase.table("clinical_activity").upsert({
                "patient_id": str(patient_id),
                "doctor_username": username,
                "note_id": note_id,
                "motif": motif,
                "audio_path": public_url,
                "updated_at": datetime.now().isoformat(),
            }).execute()

            # Clear state and show success
            st.session_state.recorded_audio = None
            st.session_state.audio_saved_msg = True
            st.rerun()

        except Exception as e:
            st.error(f"❌ Save failed: {e}")

    # Show success message if flag is set
    if st.session_state.audio_saved_msg:
        st.success("✅ Audio saved successfully")
        # Clear the flag after showing
        st.session_state.audio_saved_msg = None


# -------------------------------------------------
# Additional notes + save
# -------------------------------------------------

def render_additional_notes(patient_id: int, username: str, df):
    """Render notes text area and save ONLY to Supabase storage (not DB)"""
    init_session_state()

    col1, col2 = st.columns([3, 1])

    with col1:
        text = st.text_area(
            "📝 Additional Notes",
            value=st.session_state.additional_notes_text,
            height=120,
        )
        st.session_state.additional_notes_text = text

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("💾 Save Notes", use_container_width=True):

            if not text.strip():
                st.warning("⚠️ Notes are empty")
                return

            # Get patient info
            row = df[df["patientId"] == patient_id].iloc[0]
            motif = row.get("motif", "unknown")

            # Build filename with FOLDER included
            safe_doctor = safe_filename(username)
            safe_motif = safe_filename(motif)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = (
                f"{safe_doctor}_"
                f"patient{patient_id}_"
                f"{safe_motif}_"
                f"date_{timestamp}_notes.txt"
            )
            
            # Include folder
            full_path = f"notes/{filename}"

            try:
                # Upload to Supabase storage ONLY
                _, public_url = upload_notes_file(full_path, text.encode("utf-8"))

                # Clear state and show success
                st.session_state.additional_notes_text = ""
                st.session_state.notes_saved_msg = True
                st.rerun()

            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

    # Show success message if flag is set
    if st.session_state.notes_saved_msg:
        st.success("✅ Notes saved successfully")
        # Clear the flag after showing
        st.session_state.notes_saved_msg = None


# -------------------------------------------------
# Content cards (unchanged)
# -------------------------------------------------

def render_content_cards(sections: List[str]):
    """Render clinical note content in cards"""
    cols = st.columns(min(3, len(sections)))
    for col, section in zip(cols, sections[:3]):
        with col:
            st.markdown(
                f'<div class="note-section">{section}</div>',
                unsafe_allow_html=True,
            )