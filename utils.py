"""
Utility functions for the Clinical Notes Application
"""
import re
import os
import io
import pickle
from typing import Optional, Tuple
from config import SCOPES
import streamlit as st
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False


def safe_filename(name: str) -> str:
    """Convert string to safe filename"""
    return re.sub(r'[^\w\-_.]', '_', name)




def authenticate_drive():
    """Authenticate with Google Drive using Streamlit secrets safely."""
    
    secret_path = "client_secret.json"

    # Write client_secret to file (only if missing or running locally)
    if not os.path.exists(secret_path):
        try:
            # Load JSON string from Streamlit secrets
            client_secret_json_str = st.secrets["google"]["client_secret_json"]
            client_secret_json = json.loads(client_secret_json_str)
        except Exception as e:
            st.error(f"Failed to load Google client secret: {e}")
            return None

        # Write to file for InstalledAppFlow
        with open(secret_path, "w") as f:
            json.dump(client_secret_json, f)

    # Streamlit Cloud has ephemeral filesystem, token.pkl might not persist
    creds = None
    token_path = "token.pkl"
    if os.path.exists(token_path):
        try:
            with open(token_path, "rb") as token_file:
                creds = pickle.load(token_file)
        except Exception:
            creds = None

    if not creds:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Attempt to save token for session (ok if ephemeral)
            with open(token_path, "wb") as token_file:
                pickle.dump(creds, token_file)
        except Exception as e:
            st.error(f"Drive authentication failed: {e}")
            return None

    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except Exception as e:
        st.error(f"Failed to build Drive service: {e}")
        return None



def upload_file_to_drive(service, filename: str, file_bytes: bytes, 
                         folder_id: str, mimetype: str = 'audio/wav') -> Tuple[str, str]:
    """Upload file to Google Drive"""
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mimetype)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    return file['id'], file['webViewLink']


def create_directories():
    """Create necessary directories if they don't exist"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)