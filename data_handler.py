"""
Data handling functions for Clinical Notes Application
ORGANIZED STRUCTURE: 60 STEMI patients, 10 per doctor (6 doctors)
"""
import pandas as pd
import streamlit as st
from typing import Optional
from config import DATA_PATH


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """Load clinical notes data from CSV - cached for performance"""
    df = pd.read_csv(DATA_PATH)
    return df


def save_data(df: pd.DataFrame):
    """Save clinical notes data to CSV"""
    df.to_csv(DATA_PATH, index=False)


DOCTORS = [
    "Dr. Kadri",
    "Dr. Mohand Akli",
    "Dr. Khacef",
    "Dr. Himeur",
    "Dr. Korichi",
    "Dr. New",
]

PATIENTS_PER_DOCTOR = 12


def get_doctor_note_indices(username: str) -> list:
    """
    Get note indices assigned to a specific doctor.
    60 STEMI patients split equally: 10 per doctor.
    
    Dr. Kadri:        patients 0–11
    Dr. Mohand Akli:  patients 12–23
    Dr. Khacef:       patients 24–35
    Dr. Himeur:       patients 36–47
    Dr. Korichi:         patients 48–59
    """
    if username not in DOCTORS:
        return []
    idx = DOCTORS.index(username)
    start = idx * PATIENTS_PER_DOCTOR
    return list(range(start, start + PATIENTS_PER_DOCTOR))


def get_doctor_notes(df: pd.DataFrame, username: str) -> pd.DataFrame:
    """Get notes assigned to a specific doctor"""
    indices = get_doctor_note_indices(username)
    if indices:
        valid = [i for i in indices if i < len(df)]
        return df.iloc[valid]
    return pd.DataFrame()


def get_note_by_id(df: pd.DataFrame, note_id: str) -> Optional[pd.Series]:
    """Get a specific note by ID"""
    notes = df[df["note_id"] == note_id]
    if notes.empty:
        return None
    return notes.iloc[0]


def get_unique_patient_ids(df: pd.DataFrame) -> list:
    """Get unique patient IDs from doctor's notes"""
    return sorted(df["patientId"].unique().tolist())


def get_patient_notes(df: pd.DataFrame, patient_id: int) -> pd.DataFrame:
    """Get all notes for a specific patient"""
    return df[df["patientId"] == patient_id]


def get_note_by_patient(df: pd.DataFrame, patient_id: int, note_idx: int = 0) -> Optional[pd.Series]:
    """
    Get a specific note by patient ID

    Args:
        df: DataFrame containing notes
        patient_id: Patient ID to search for
        note_idx: Index of note if patient has multiple (default 0)

    Returns:
        Series containing the note data, or None if not found
    """
    notes = df[df["patientId"] == patient_id]
    if notes.empty or len(notes) <= note_idx:
        return None
    return notes.iloc[note_idx]