"""
Utility functions for the Clinical Notes Application - Supabase Version
Works locally and on deployment with zero hassle
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
        print(f"✅ Loaded Supabase config from Streamlit secrets")
        return url, key, bucket
    except Exception as e:
        print(f"⚠️ Streamlit secrets not found: {e}")
        # Fallback to environment variables (for local development)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        bucket = os.environ.get("SUPABASE_BUCKET", "recordings")
        
        if not url or not key:
            raise Exception(
                "❌ Supabase configuration not found!\n"
                "Please set up Supabase credentials in:\n"
                "- Streamlit Cloud: App Settings > Secrets\n"
                "- Local: .streamlit/secrets.toml or environment variables"
            )
        
        print(f"✅ Loaded Supabase config from environment variables")
        return url, key, bucket


def upload_file_to_supabase(filename: str, file_bytes: bytes, 
                            mimetype: str = 'audio/wav') -> Tuple[str, str]:
    """
    Upload file to Supabase Storage
    Returns: (file_id, public_url)
    """
    url, key, bucket = get_supabase_config()
    
    print(f"🔍 Uploading {filename} to Supabase...")
    print(f"📦 File size: {len(file_bytes)} bytes")
    print(f"🪣 Bucket: {bucket}")
    
    # Upload file
    upload_url = f"{url}/storage/v1/object/{bucket}/{filename}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": mimetype,
        "x-upsert": "true"  # Overwrite if exists
    }
    
    response = requests.post(upload_url, headers=headers, data=file_bytes)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    
    print(f"✅ Upload successful!")
    
    # Generate public URL
    public_url = f"{url}/storage/v1/object/public/{bucket}/{filename}"
    print(f"🔗 Public URL: {public_url}")
    
    return filename, public_url


def upload_audio_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload audio file to Supabase"""
    return upload_file_to_supabase(filename, file_bytes, mimetype='audio/wav')


def upload_notes_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Upload text notes to Supabase"""
    return upload_file_to_supabase(filename, file_bytes, mimetype='text/plain')


def list_files(prefix: str = "") -> list:
    """List files in Supabase bucket (optional)"""
    url, key, bucket = get_supabase_config()
    
    list_url = f"{url}/storage/v1/object/list/{bucket}"
    headers = {"Authorization": f"Bearer {key}"}
    
    params = {}
    if prefix:
        params["prefix"] = prefix
    
    response = requests.get(list_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ Failed to list files: {response.status_code}")
        return []


def create_directories():
    """Create necessary directories if they don't exist (for local storage fallback)"""
    from config import AUDIO_DIR, NOTES_DIR
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)


def test_supabase_connection():
    """Test Supabase connection - call this for debugging"""
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE CONNECTION")
    print("="*60)
    
    try:
        url, key, bucket = get_supabase_config()
        print(f"✅ Config loaded")
        print(f"📍 URL: {url}")
        print(f"🪣 Bucket: {bucket}")
        
        # Try to list files
        print(f"\n[TEST] Listing files in bucket...")
        files = list_files()
        print(f"✅ Found {len(files)} files")
        
        # Try to upload a test file
        print(f"\n[TEST] Uploading test file...")
        test_content = b"test connection"
        test_filename = "test_connection.txt"
        
        file_id, file_url = upload_file_to_supabase(
            test_filename,
            test_content,
            mimetype='text/plain'
        )
        
        print(f"✅ Test upload successful!")
        print(f"📄 File ID: {file_id}")
        print(f"🔗 URL: {file_url}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - Supabase is working!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\n" + "="*60)
        print("🔧 TROUBLESHOOTING:")
        print("="*60)
        print("1. Check your Supabase credentials are correct")
        print("2. Make sure the bucket exists and is public")
        print("3. Verify you copied the correct API URL and key")
        print("="*60 + "\n")
        return False