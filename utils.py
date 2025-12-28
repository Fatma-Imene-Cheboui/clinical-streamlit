"""
Utility functions for the Clinical Notes Application
"""
import re
import os
import io
import json
from typing import Optional, Tuple
from config import SCOPES

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False


def safe_filename(name: str) -> str:
    """Convert string to safe filename"""
    return re.sub(r'[^\w\-_.]', '_', name)


def authenticate_drive():
    """
    Authenticate with Google Drive using Service Account
    Works in both local and deployed environments
    """
    # Try to get credentials from Streamlit secrets (deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'GOOGLE_SERVICE_ACCOUNT' in st.secrets:
            # Load from Streamlit secrets
            service_account_info = dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
            creds = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES
            )
            return build('drive', 'v3', credentials=creds)
    except:
        pass
    
    # Try to get credentials from environment variable
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_json:
        service_account_info = json.loads(service_account_json)
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        return build('drive', 'v3', credentials=creds)
    
    # Try to load from local file (development)
    service_account_file = 'service_account.json'
    if os.path.exists(service_account_file):
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )
        return build('drive', 'v3', credentials=creds)
    
    raise Exception(
        "No Google Service Account credentials found. "
        "Please set up credentials in Streamlit secrets or environment variables."
    )


def upload_file_to_drive(service, filename: str, file_bytes: bytes, 
                         folder_id: str, mimetype: str = 'audio/wav') -> Tuple[str, str]:
    """Upload file to Google Drive"""
    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(
            io.BytesIO(file_bytes),
            mimetype=mimetype,
            resumable=True
        )
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        return file['id'], file['webViewLink']
    except Exception as e:
        if '403' in str(e):
            raise Exception(
                f"Permission denied. Please ensure:\n"
                f"1. The service account has access to folder: {folder_id}\n"
                f"2. Google Drive API is enabled in your project\n"
                f"3. The service account email has Editor permissions on the folder"
            )
        raise


def create_directories():
    """Create necessary directories if they don't exist"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)