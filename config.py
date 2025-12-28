"""
Configuration file for Clinical Notes Application
"""

# File paths
DATA_PATH = "clinical_notes.csv"
AUDIO_DIR = "audios"  # Local fallback only
NOTES_DIR = "additional_notes"  # Local fallback only

# Supabase configuration (loaded from secrets/env at runtime)
# No hardcoded values needed here - handled in utils.py

# UI Configuration
VISIBLE_CARDS = 3
MAX_CARD_HEIGHT = 500
CARD_WIDTH_CHARS = 55

# Section colors and styles
SECTION_STYLES = {
    "atcd": {"color": "#5D9CEC", "emoji": "🟦"},
    "hdm": {"color": "#AC92EC", "emoji": "🟪"},
    "exam": {"color": "#4FC1E9", "emoji": "🟩"},
    "ecg": {"color": "#ED5565", "emoji": "🟥"},
    "ett": {"color": "#FC6E51", "emoji": "🟧"},
    "coro": {"color": "#E9573F", "emoji": "🫀"},
    "conduite": {"color": "#FFCE54", "emoji": "🟨"},
    "cat": {"color": "#A0826D", "emoji": "🟫"},
}