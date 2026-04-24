import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
SESSION_EXPIRY_HOURS = 24

def generate_session_id() -> str:
    """Generate a unique session identifier"""
    return str(uuid.uuid4())

def generate_request_id() -> str:
    """Generate a unique request identifier for error tracking"""
    return str(uuid.uuid4())

def get_session_file_path(session_id: str, filename: str) -> Path:
    """Get the file path for a session's uploaded file"""
    safe_filename = f"{session_id}_{filename}"
    return UPLOAD_DIR / safe_filename

def get_session_expiry() -> datetime:
    """Get the expiry datetime for a new session"""
    return datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)

def validate_csv_file(filename: str) -> bool:
    """Validate that the file has a CSV extension"""
    return filename.lower().endswith('.csv')
