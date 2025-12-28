"""
Utility functions for the Clinical Notes Application
"""
import re
import os
import io
import pickle
from typing import Optional, Tuple
from config import SCOPES
import json
import streamlit as st

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
    client_secret_dict = json.loads(st.secrets["google"]["client_secret_json"])
    flow = InstalledAppFlow.from_client_config(client_secret_dict, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build("drive", "v3", credentials=creds)
    return service


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