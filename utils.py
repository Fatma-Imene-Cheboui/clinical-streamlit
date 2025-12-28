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


import json
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def authenticate_drive():
    try:
        st.write("Loading service account from Streamlit secrets...")
        client_secret_dict = json.loads(st.secrets["google"]["client_secret_json"])
        creds = service_account.Credentials.from_service_account_info(
            client_secret_dict,
            scopes=SCOPES
        )
        service = build("drive", "v3", credentials=creds)
        st.success("Drive service authenticated successfully!")
        return service
    except Exception as e:
        st.error(f"Drive authentication failed: {e}")
        return None


def upload_file_to_drive(service, filename: str, file_bytes: bytes, folder_id: str, mimetype: str = 'audio/wav'):
    """Upload file to a shared folder using a service account"""
    if service is None:
        st.error("Drive service is None! Cannot upload file.")
        return None, None

    try:
        st.write(f"Uploading file: {filename} to folder: {folder_id}")
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mimetype)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True  # crucial for shared folders
        ).execute()

        st.success(f"File uploaded! ID: {file['id']}")
        return file['id'], file['webViewLink']

    except Exception as e:
        st.error(f"File upload failed: {e}")
        return None, None




def create_directories():
    """Create necessary directories if they don't exist"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)