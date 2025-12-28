"""
Configuration file for Clinical Notes Application
"""

# File paths
DATA_PATH = "clinical_notes.csv"
AUDIO_DIR = "audios"
NOTES_DIR = "additional_notes"

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
DRIVE_AUDIO_FOLDER_ID = '1i0DW8qlRVAJuRD2Jf-3AtGAsbF0qtpd6'
DRIVE_NOTES_FOLDER_ID = '1vlZ00_eZI5ZLIdT7h15RNAszteIpYuey'

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