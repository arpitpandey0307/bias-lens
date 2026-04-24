from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/samples", tags=["samples"])

# Import sessions from upload router
from routers.upload import sessions

class SampleDataset(BaseModel):
    name: str
    display_name: str
    description: str
    prediction_task: str
    protected_attributes: List[str]
    outcome_column: str
    row_count: int
    column_count: int

class SampleLoadResponse(BaseModel):
    session_id: str
    filename: str
    size_bytes: int
    row_count: int
    column_count: int
    preview: List[Dict[str, Any]]
    warnings: List[Dict[str, str]]
    suggested_protected_attr: str
    suggested_outcome: str

# Sample dataset metadata
SAMPLE_DATASETS = {
    "adult_income": SampleDataset(
        name="adult_income",
        display_name="UCI Adult Income",
        description="Predict whether income exceeds $50K/yr based on census data. Classic fairness benchmark with gender and race as protected attributes.",
        prediction_task="Binary classification: income >50K or ≤50K",
        protected_attributes=["sex", "race"],
        outcome_column="income",
        row_count=21,
        column_count=13
    ),
    "compas": SampleDataset(
        name="compas",
        display_name="COMPAS Recidivism",
        description="Predict recidivism risk using COMPAS algorithm data. Widely studied for racial bias in criminal justice.",
        prediction_task="Binary classification: recidivate within 2 years",
        protected_attributes=["race", "sex"],
        outcome_column="two_year_recid",
        row_count=21,
        column_count=14
    )
}

@router.get("/", response_model=List[SampleDataset])
async def list_samples():
    """List all available sample datasets"""
    return list(SAMPLE_DATASETS.values())

@router.post("/{name}/load", response_model=SampleLoadResponse)
async def load_sample(name: str):
    """Load a sample dataset and create a session"""
    if name not in SAMPLE_DATASETS:
        raise HTTPException(status_code=404, detail=f"Sample dataset '{name}' not found")
    
    sample_info = SAMPLE_DATASETS[name]
    
    # Load the sample CSV file
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    csv_path = os.path.join(fixtures_dir, f"{name}.csv")
    
    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=500,
            detail=f"Sample dataset file not found. Please ensure {name}.csv exists in backend/fixtures/"
        )
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample dataset: {str(e)}")
    
    # Create session
    session_id = str(uuid.uuid4())
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    session_file = os.path.join(upload_dir, f"{session_id}.csv")
    df.to_csv(session_file, index=False)
    
    # Get file size
    file_size = os.path.getsize(session_file)
    
    # Store session metadata (same as upload router)
    sessions[session_id] = {
        "session_id": session_id,
        "filename": f"{sample_info.display_name}.csv",
        "upload_timestamp": datetime.utcnow(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "file_path": session_file,
        "expires_at": datetime.utcnow() + timedelta(hours=24),
        "dataframe": df  # Store in memory
    }
    
    # Generate preview (first 10 rows)
    preview = df.head(10).to_dict(orient="records")
    
    # Check for warnings
    warnings = []
    if len(df) > 100000:
        warnings.append({
            "type": "large_dataset",
            "message": f"Large dataset ({len(df):,} rows). Analysis may take longer."
        })
    
    return SampleLoadResponse(
        session_id=session_id,
        filename=f"{sample_info.display_name}.csv",
        size_bytes=file_size,
        row_count=len(df),
        column_count=len(df.columns),
        preview=preview,
        warnings=warnings,
        suggested_protected_attr=sample_info.protected_attributes[0],
        suggested_outcome=sample_info.outcome_column
    )
