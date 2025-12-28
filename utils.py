"""
Utility functions for the Clinical Notes Application - Supabase Version
"""
import re
import os
import requests
from typing import Tuple


def safe_filename(name: str) -> str:
    """Convert string to safe filename"""
    return re.sub(r'[^\w\-_.]', '_', name)


def get_supabase_config():
    """Get Supabase configuration from secrets or environment"""
    try:
        import streamlit as st
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]
        bucket = st.secrets["supabase"]["BUCKET_NAME"]
        return url, key, bucket
    except:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        bucket = os.environ.get("SUPABASE_BUCKET", "recordings")
        
        if not url or not key:
            raise Exception(
                "Supabase configuration not found. "
                "Please set up credentials in Streamlit secrets or environment variables."
            )
        
        return url, key, bucket


def upload_file_to_supabase(filename: str, file_bytes: bytes, 
                            mimetype: str = 'audio/wav') -> Tuple[str, str]:
    """
    Upload file to Supabase Storage
    Returns: (file_id, public_url)
    """
    url, key, bucket = get_supabase_config()
    
    upload_url = f"{url}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": mimetype,
        "x-upsert": "true"
    }
    
    response = requests.post(upload_url, headers=headers, data=file_bytes)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    public_url = f"{url}/storage/v1/object/public/{bucket}/{filename}"
    
    return filename, public_url


def upload_audio_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload audio file to Supabase"""
    return upload_file_to_supabase(filename, file_bytes, mimetype='audio/wav')


def upload_notes_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload text notes to Supabase"""
    return upload_file_to_supabase(filename, file_bytes, mimetype='text/plain')


def create_directories():
    """Create necessary directories if they don't exist"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)