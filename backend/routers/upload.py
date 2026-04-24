from fastapi import APIRouter, UploadFile, File, HTTPException, status
from datetime import datetime
import pandas as pd
import io

from models import UploadResponse, ErrorResponse
from utils import (
    generate_session_id,
    generate_request_id,
    get_session_file_path,
    get_session_expiry,
    validate_csv_file,
    MAX_FILE_SIZE
)
from error_handlers import (
    FileSizeExceededError,
    InvalidFormatError,
    InsufficientDataError
)

router = APIRouter(prefix="/api", tags=["upload"])

# In-memory session storage (replace with database in production)
sessions = {}

@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for fairness analysis
    
    - Accepts CSV files up to 50MB
    - Returns session ID and preview of first 10 rows
    - Validates file format and size
    """
    request_id = generate_request_id()
    
    # Validate file extension
    if not validate_csv_file(file.filename or ""):
        raise InvalidFormatError(file.filename or "unknown")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise FileSizeExceededError(size_mb)
    
    # Check for empty file
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Empty File",
                "message": "File is empty. Please upload a file with data.",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    # Try to parse CSV
    try:
        # Try different delimiters
        df = None
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv(io.BytesIO(content), delimiter=delimiter)
                if len(df.columns) > 1:  # Valid parse should have multiple columns
                    break
            except:
                continue
        
        if df is None or len(df.columns) <= 1:
            raise ValueError("Could not parse CSV with any delimiter")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Parse Error",
                "message": "Unable to parse CSV. Please check file encoding and structure.",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    # Generate session
    session_id = generate_session_id()
    file_path = get_session_file_path(session_id, file.filename or "upload.csv")
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Store session metadata
    sessions[session_id] = {
        "session_id": session_id,
        "filename": file.filename,
        "upload_timestamp": datetime.utcnow(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "file_path": str(file_path),
        "expires_at": get_session_expiry(),
        "dataframe": df  # Store in memory for now
    }
    
    # Generate preview (first 10 rows)
    preview_rows = min(10, len(df))
    preview = df.head(preview_rows).to_dict('records')
    
    # Generate warnings
    warnings = []
    if len(df) < 50:
        warnings.append({
            "type": "insufficient_data",
            "message": f"Dataset has only {len(df)} rows. Minimum 50 rows recommended for reliable analysis."
        })
    
    if len(df) > 500000:
        warnings.append({
            "type": "large_dataset",
            "message": f"Large dataset ({len(df):,} rows). Analysis may take longer than usual."
        })
    
    return UploadResponse(
        session_id=session_id,
        filename=file.filename or "upload.csv",
        size_bytes=file_size,
        row_count=len(df),
        column_count=len(df.columns),
        preview=preview,
        warnings=warnings
    )
