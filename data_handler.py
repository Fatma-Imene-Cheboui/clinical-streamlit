"""
Data handling functions for Clinical Notes Application
ORGANIZED STRUCTURE: 2 patients per motif per doctor
"""
import pandas as pd
from typing import Optional
from config import DATA_PATH


def load_data() -> pd.DataFrame:
    """Load clinical notes data from CSV"""
    df = pd.read_csv(DATA_PATH)
   
    return df


def save_data(df: pd.DataFrame):
    """Save clinical notes data to CSV"""
    df.to_csv(DATA_PATH, index=False)


def get_doctor_note_indices(username: str) -> list:
    """
    Get note indices assigned to a specific doctor
    50 patients total organized by motif:
    - Patients 1-10: Motif 1 (STEMI)
    - Patients 11-20: Motif 2 (NSTEMI)
    - Patients 21-30: Motif 3 (BAV)
    - Patients 31-40: Motif 4 (Coronarographie programmée)
    - Patients 41-50: Motif 5 (Changement de boitier)
    
    Each doctor gets 2 patients from each motif group = 10 patients total
    """
    doctor_assignments = {
        # Each doctor gets indices 0-1, 10-11, 20-21, 30-31, 40-41 (2 from each motif)
        "Dr. Kadri": [0, 1, 10, 11, 20, 21, 30, 31, 40, 41],
        "Dr. Mohand Akli": [2, 3, 12, 13, 22, 23, 32, 33, 42, 43],
        "Dr. Khacef": [4, 5, 14, 15, 24, 25, 34, 35, 44, 45],
        "Dr. Himeur": [6, 7, 16, 17, 26, 27, 36, 37, 46, 47],
        "Dr. Benali": [8, 9, 18, 19, 28, 29, 38, 39, 48, 49]
    }
    return doctor_assignments.get(username, [])


def get_doctor_notes(df: pd.DataFrame, username: str) -> pd.DataFrame:
    """Get notes assigned to a specific doctor"""
    indices = get_doctor_note_indices(username)
    if indices:
        return df.iloc[indices]
    return pd.DataFrame()


def update_audio_file(df: pd.DataFrame, note_id: str, file_path: str):
    """Update audio file path for a note"""
    df.loc[df["note_id"] == note_id, "audio_file"] = file_path


def update_additional_notes(df: pd.DataFrame, note_id: str, notes_path: str):
    """Update additional notes path for a note"""
    df.loc[df["note_id"] == note_id, "additional_notes"] = notes_path


def get_note_by_id(df: pd.DataFrame, note_id: str) -> Optional[pd.Series]:
    """Get a specific note by ID"""
    notes = df[df["note_id"] == note_id]
    if notes.empty:
        return None
    return notes.iloc[0]


def get_unique_patient_ids(df: pd.DataFrame) -> list:
    """Get unique patient IDs from doctor's notes"""
    return sorted(df["patientId"].unique().tolist())


def get_patient_notes(df: pd.DataFrame, patient_id: str) -> pd.DataFrame:
    """Get all notes for a specific patient"""
    return df[df["patientId"] == patient_id]


def get_note_by_patient_and_type(df: pd.DataFrame, patient_id: str, note_type: str, note_idx: int = 0) -> Optional[pd.Series]:
    """Get a specific note by patient ID, note type (case-insensitive), and index"""
    notes = df[(df["patientId"] == patient_id) & (df["note_type"].str.lower() == note_type.lower())]
    if notes.empty or len(notes) <= note_idx:
        return None
    return notes.iloc[note_idx]