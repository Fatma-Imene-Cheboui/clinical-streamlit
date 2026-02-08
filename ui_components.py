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
        "audio_recorder_key": 0,  # For resetting audio recorder widget
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -------------------------------------------------
# Supabase helpers
# -------------------------------------------------

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_all_patient_activities(patient_ids: list):
    """Get activity records for ALL patients in one query - MUCH faster"""
    try:
        supabase = get_supabase_client()
        # Convert to strings for the query
        patient_id_strs = [str(pid) for pid in patient_ids]
        
        resp = (
            supabase
            .table("clinical_activity")
            .select("patient_id, audio_path, notes_path")
            .in_("patient_id", patient_id_strs)
            .execute()
        )
        
        # Build a dict for quick lookup
        activity_map = {}
        for record in (resp.data or []):
            pid = int(record.get("patient_id", 0))
            has_audio = bool(record.get("audio_path", "").strip())
            activity_map[pid] = has_audio
        
        return activity_map
    except Exception:
        return {}


def patient_is_completed(patient_id: int, activity_map: dict) -> bool:
    """Check if patient has audio completed using pre-loaded activity map"""
    return activity_map.get(patient_id, False)


# -------------------------------------------------
# Patient selector (Supabase-driven checkmarks)
# -------------------------------------------------

def render_patient_selector(doctor_notes, username: str) -> int:
    """Render patient selector with completion status from Supabase"""
    init_session_state()

    patient_ids = sorted(doctor_notes["patientId"].unique().tolist())
    
    # PERFORMANCE FIX: Fetch ALL patient activities in ONE query
    activity_map = get_all_patient_activities(patient_ids)
    
    options = []

    for pid in patient_ids:
        row = doctor_notes[doctor_notes["patientId"] == pid].iloc[0]
        motif = row.get("motif", "Unknown")
        motif_short = motif.split()[0] if motif else "Unknown"

        completed = patient_is_completed(pid, activity_map)
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
    # Use a key that changes when audio is cleared to reset the widget
    if "audio_recorder_key" not in st.session_state:
        st.session_state.audio_recorder_key = 0
    
    audio = st.audio_input(
        "🎤 Record audio", 
        key=f"audio_input_{st.session_state.audio_recorder_key}"
    )
    
    if audio:
        st.session_state.recorded_audio = audio.getvalue()
    elif st.session_state.get("recorded_audio") is None:
        # If no audio and session state also has none, ensure it's cleared
        st.session_state.recorded_audio = None


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

        # Create a placeholder for status updates
        status_placeholder = st.empty()

        try:
            with st.spinner("⏳ Uploading audio..."):
                _, public_url = upload_audio_file(full_path, audio_bytes)
                
                supabase.table("clinical_activity").upsert({
                    "patient_id": str(patient_id),
                    "doctor_username": username,
                    "note_id": note_id,
                    "motif": motif,
                    "audio_path": public_url,
                    "updated_at": datetime.now().isoformat(),
                }).execute()
            
            # ... state clearing code ...
            
            get_all_patient_activities.clear()  # Only clear this cache
            st.success("✅ Audio saved successfully!")
            time.sleep(0.5)  # Shorter delay
            st.rerun()

            # ONLY after successful upload, clear state
            st.session_state.recorded_audio = None
            
            # Reset the audio recorder widget by changing its key
            st.session_state.audio_recorder_key = st.session_state.get("audio_recorder_key", 0) + 1
            
            # Clear cache to update checkmarks
            get_all_patient_activities.clear()
            
            # Show success message
            status_placeholder.success("✅ Audio saved successfully!")
            
            # Wait a moment so user sees the success message
            time.sleep(1.5)
            
            # Now rerun to refresh the UI
            st.rerun()

        except Exception as e:
            # Show error without rerunning
            status_placeholder.error(f"❌ Save failed: {str(e)}")
            # Don't clear audio on error so user can try again


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
                with st.spinner("Saving notes..."):
                    # Upload to Supabase storage ONLY
                    _, public_url = upload_notes_file(full_path, text.encode("utf-8"))

                    # Clear state
                    st.session_state.additional_notes_text = ""
                    st.success("✅ Notes saved successfully")
                    time.sleep(1)
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Upload failed: {e}")


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