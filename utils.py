"""
Utility functions for the Clinical Notes Application - Supabase Version
FIXED: Preserve folder structure in uploads
"""
import re
import os
import requests
from typing import Tuple
from supabase import create_client

_supabase_client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        url, key, _ = get_supabase_config()
        _supabase_client = create_client(url, key)
    return _supabase_client


def safe_filename(name: str) -> str:
    """Convert string to safe filename (only alphanumeric, dash, underscore, dot)"""
    safe_name = re.sub(r'[^\w\-_.]', '_', name)
    print(f"[DEBUG] safe_filename: original='{name}' -> safe='{safe_name}'")
    return safe_name


def upload_file_to_supabase(filename: str, file_bytes: bytes, 
                            mimetype: str = 'audio/wav') -> Tuple[str, str]:
    """
    Upload file to Supabase Storage
    Returns: (file_id, public_url)
    
    IMPORTANT: filename should include folder path like "audio/file.wav"
    """
    url, key, bucket = get_supabase_config()
    
    # DON'T sanitize the entire path - preserve folder structure
    # Only sanitize the actual filename part
    if '/' in filename:
        parts = filename.split('/')
        folder = '/'.join(parts[:-1])  # Keep folder path as-is
        file_only = parts[-1]
        sanitized_file = safe_filename(file_only)
        final_path = f"{folder}/{sanitized_file}"
    else:
        final_path = safe_filename(filename)
    
    print(f"[DEBUG] Uploading file to Supabase:")
    print(f"        Bucket: {bucket}")
    print(f"        Original path: {filename}")
    print(f"        Final path: {final_path}")
    print(f"        Mimetype: {mimetype}")
    print(f"        File size: {len(file_bytes)} bytes")
    
    upload_url = f"{url}/storage/v1/object/{bucket}/{final_path}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": mimetype,
        "x-upsert": "true"
    }
    
    response = requests.post(upload_url, headers=headers, data=file_bytes)
    
    print(f"[DEBUG] Supabase response: {response.status_code} - {response.text}")
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    public_url = f"{url}/storage/v1/object/public/{bucket}/{final_path}"
    
    print(f"[DEBUG] Public URL: {public_url}")
    
    return final_path, public_url


def upload_audio_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload audio file to Supabase"""
    print(f"[DEBUG] upload_audio_file called with filename: {filename}")
    return upload_file_to_supabase(filename, file_bytes, mimetype='audio/wav')


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


def check_audio_exists_in_supabase(filename_pattern: str) -> bool:
    """
    Check if any file matching the pattern exists in Supabase
    Returns True if at least one matching file exists
    """
    try:
        url, key, bucket = get_supabase_config()
        
        # List files in the bucket
        list_url = f"{url}/storage/v1/object/list/{bucket}"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Extract the folder path from pattern (e.g., "audio/" from "audio/Dr_Kadri_1_")
        folder = filename_pattern.split('/')[0] if '/' in filename_pattern else ""
        
        # Request payload to list files
        payload = {
            "prefix": folder,
            "limit": 1000
        }
        
        response = requests.post(list_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            files = response.json()
            # Check if any file matches our pattern
            for file in files:
                file_name = file.get("name", "")
                if filename_pattern in file_name:
                    return True
        
        return False
        
    except Exception as e:
        # If there's an error checking, return False
        return False


def upload_notes_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload text notes to Supabase"""
    return upload_file_to_supabase(filename, file_bytes, mimetype='text/plain')


def create_directories():
    """Create necessary directories if they don't exist"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)


def get_activity(patient_id, username):
    supabase = get_supabase_client()
    res = (
        supabase.table("clinical_activity")
        .select("*")
        .eq("patient_id", patient_id)
        .eq("doctor_username", username)
        .execute()
    )
    return res.data


def upsert_activity(patient_id, username,
                    audio_path=None, notes_path=None):
    payload = {
        "patient_id": patient_id,
        "doctor_username": username,
    }
    if audio_path:
        payload["audio_path"] = audio_path
    if notes_path:
        payload["notes_path"] = notes_path
    supabase = get_supabase_client()

    supabase.table("clinical_activity").upsert(payload).execute()