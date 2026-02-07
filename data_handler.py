"""
Data handling functions for Clinical Notes Application
ORGANIZED STRUCTURE: 4 patients per motif per doctor (100 patients total)
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
    100 patients total organized by motif:
    - Patients 1-20: Motif 1 (STEMI)
    - Patients 21-40: Motif 2 (NSTEMI)
    - Patients 41-60: Motif 3 (BAV)
    - Patients 61-80: Motif 4 (Coronarographie programmée)
    - Patients 81-100: Motif 5 (Changement de boitier)
    
    Each doctor gets 4 patients from each motif group = 20 patients total
    """
    doctor_assignments = {
        # Each doctor gets indices 0-3, 20-23, 40-43, 60-63, 80-83 (4 from each motif)
        "Dr. Kadri": [0, 1, 2, 3, 20, 21, 22, 23, 40, 41, 42, 43, 60, 61, 62, 63, 80, 81, 82, 83],
        "Dr. Mohand Akli": [4, 5, 6, 7, 24, 25, 26, 27, 44, 45, 46, 47, 64, 65, 66, 67, 84, 85, 86, 87],
        "Dr. Khacef": [8, 9, 10, 11, 28, 29, 30, 31, 48, 49, 50, 51, 68, 69, 70, 71, 88, 89, 90, 91],
        "Dr. Himeur": [12, 13, 14, 15, 32, 33, 34, 35, 52, 53, 54, 55, 72, 73, 74, 75, 92, 93, 94, 95],
        "Dr. New": [16, 17, 18, 19, 36, 37, 38, 39, 56, 57, 58, 59, 76, 77, 78, 79, 96, 97, 98, 99]
    }
    return doctor_assignments.get(username, [])


def get_doctor_notes(df: pd.DataFrame, username: str) -> pd.DataFrame:
    """Get notes assigned to a specific doctor"""
    indices = get_doctor_note_indices(username)
    if indices:
        return df.iloc[indices]
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
    Since all notes are admission notes, we just get by patientId
    
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