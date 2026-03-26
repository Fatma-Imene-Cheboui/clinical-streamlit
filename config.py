"""
Configuration file for Clinical Notes Application
"""

# File paths
DATA_PATH = "2ndBatch_960patients.csv"
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
    "fdrcv": {"color": "#ED5565", "emoji": "🟥"},
    "hdm": {"color": "#AC92EC", "emoji": "🟪"},
    "exam": {"color": "#4FC1E9", "emoji": "🟩"},
    "bio": {"color": "#48CFAD", "emoji": "🧪"},
    "ecg": {"color": "#ED5565", "emoji": "📈"},
    "ett": {"color": "#FC6E51", "emoji": "🫀"},
    "coro": {"color": "#E9573F", "emoji": "🩺"},
    "conduite": {"color": "#FFCE54", "emoji": "🟨"},
    "evol": {"color": "#A0D468", "emoji": "📊"},
    "cat": {"color": "#A0826D", "emoji": "🟫"},
}
