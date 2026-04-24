from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import os

from models import ExportRequest, ExportResponse
from report_generator import create_pdf_report
from html_report_generator import generate_html_report
from utils import generate_request_id

router = APIRouter(prefix="/api", tags=["export"])

# Import analyses and sessions
from routers.analyze import analyses
from routers.upload import sessions

# Reports directory
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# Store report metadata
reports = {}

@router.post("/export", response_model=ExportResponse)
async def export_report(request: ExportRequest):
    """
    Export fairness analysis report as PDF or HTML
    
    - Generates comprehensive report with all metrics
    - Includes visualizations and recommendations
    - Returns download URL with 24-hour expiry
    """
    request_id = generate_request_id()
    
    # Get analysis
    if request.analysis_id not in analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Analysis Not Found",
                "message": "Analysis must be completed before exporting report.",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    analysis_data = analyses[request.analysis_id]
    session_id = analysis_data["session_id"]
    
    # Get session
    if session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Session Not Found",
                "message": "Session expired. Please upload your data again.",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    session_data = sessions[session_id]
    
    # Generate report
    try:
        report_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"biaslens_report_{timestamp}.{request.format}"
        file_path = REPORTS_DIR / filename
        
        if request.format == "pdf":
            # Generate PDF
            create_pdf_report(
                analysis_data=analysis_data["result"].model_dump(),
                session_data=session_data,
                output_path=str(file_path)
            )
            media_type = "application/pdf"
        else:
            # Generate HTML
            result_dict = analysis_data["result"].model_dump()
            html_content = generate_html_report(
                analysis_data={
                    **result_dict,
                    "dataset_name": session_data["filename"],
                    "row_count": session_data["row_count"],
                    "protected_attribute": analysis_data.get("protected_attribute", "unknown"),
                    "outcome_column": analysis_data.get("outcome_column", "unknown")
                },
                report_id=report_id,
                include_sections=request.include_sections
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            media_type = "text/html"
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Store report metadata
        generated_at = datetime.utcnow()
        expires_at = generated_at + timedelta(hours=24)
        
        reports[report_id] = {
            "report_id": report_id,
            "analysis_id": request.analysis_id,
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_size,
            "generated_at": generated_at,
            "expires_at": expires_at,
            "media_type": media_type
        }
        
        return ExportResponse(
            report_id=report_id,
            download_url=f"/api/download/{report_id}",
            filename=filename,
            size_bytes=file_size,
            generated_at=generated_at,
            expires_at=expires_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Export Failed",
                "message": "Unable to generate report. Please try again.",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    Download generated report
    """
    if report_id not in reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or expired"
        )
    
    report = reports[report_id]
    
    # Check expiry
    if datetime.utcnow() > report["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Report has expired. Please generate a new report."
        )
    
    file_path = report["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=report["filename"],
        media_type=report.get("media_type", "application/pdf")
    )
