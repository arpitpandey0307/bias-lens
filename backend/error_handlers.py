from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class BiasLensException(Exception):
    """Base exception for BiasLens errors"""
    def __init__(self, message: str, status_code: int = 500, details: str = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class FileSizeExceededError(BiasLensException):
    def __init__(self, size_mb: float, max_mb: int = 50):
        super().__init__(
            message=f"File size ({size_mb:.1f}MB) exceeds maximum allowed size ({max_mb}MB)",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details="Please upload a smaller file or sample your dataset"
        )

class InvalidFormatError(BiasLensException):
    def __init__(self, format_type: str):
        super().__init__(
            message=f"Invalid file format: {format_type}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Only CSV files are supported. Please ensure your file has a .csv extension"
        )

class InsufficientDataError(BiasLensException):
    def __init__(self, row_count: int, min_rows: int = 50):
        super().__init__(
            message=f"Insufficient data: {row_count} rows (minimum {min_rows} required)",
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Please upload a dataset with at least 50 rows for meaningful analysis"
        )

class SessionExpiredError(BiasLensException):
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session expired or not found: {session_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            details="Your session has expired. Please upload your data again"
        )

class ComputationTimeoutError(BiasLensException):
    def __init__(self):
        super().__init__(
            message="Analysis computation timed out",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details="The dataset is too large to process. Try sampling your data or contact support"
        )

class MissingColumnError(BiasLensException):
    def __init__(self, column_name: str):
        super().__init__(
            message=f"Required column not found: {column_name}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=f"The column '{column_name}' does not exist in your dataset"
        )

async def biaslens_exception_handler(request: Request, exc: BiasLensException):
    """Handle BiasLens custom exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        f"BiasLens Error [{request_id}]: {exc.message}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.exception(
        f"Unexpected Error [{request_id}]: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": "Please try again or contact support if the issue persists",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )
