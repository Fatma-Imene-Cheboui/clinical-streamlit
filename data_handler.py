"""
Data handling functions for Clinical Notes Application
"""
import pandas as pd
from typing import Optional
from config import DATA_PATH


def load_data() -> pd.DataFrame:
    """Load clinical notes data from CSV"""
    df = pd.read_csv(DATA_PATH, dtype={
        "audio_file": "string",
        "validated": "boolean",
        "additional_notes": "string"
    })
    df["audio_file"] = df["audio_file"].fillna("")
    df["validated"] = df["validated"].fillna(False)
    df["additional_notes"] = df["additional_notes"].fillna("")
    return df


def save_data(df: pd.DataFrame):
    """Save clinical notes data to CSV"""
    df.to_csv(DATA_PATH, index=False)


def get_doctor_notes(df: pd.DataFrame, username: str) -> pd.DataFrame:
    """Get notes assigned to a specific doctor"""
    if username == "Dr. Smith":
        return df.iloc[0:3]
    elif username == "Dr. Jhones":
        return df.iloc[3:7]
    else:
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