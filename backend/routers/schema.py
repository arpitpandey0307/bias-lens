from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import numpy as np
from typing import List

from models import (
    ColumnInfo,
    SchemaValidationResponse,
    SchemaSuggestions,
    ProtectedAttributeSuggestion,
    OutcomeSuggestion,
    SchemaWarning
)
from utils import generate_request_id

router = APIRouter(prefix="/api", tags=["schema"])

# Import sessions from upload router
from routers.upload import sessions

class SchemaValidationRequest(BaseModel):
    session_id: str

# Protected attribute keywords for detection
PROTECTED_ATTR_KEYWORDS = [
    'gender', 'sex', 'race', 'ethnicity', 'age', 'religion',
    'disability', 'national_origin', 'nationality', 'color'
]

# Outcome keywords for detection
OUTCOME_KEYWORDS = [
    'outcome', 'result', 'decision', 'approved', 'hired',
    'accepted', 'admitted', 'label', 'target', 'class'
]

def detect_column_type(series: pd.Series) -> str:
    """Detect the type of a column"""
    # Remove NaN values for analysis
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return "text"
    
    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        unique_count = series.nunique()
        if unique_count == 2:
            return "binary"
        elif unique_count <= 10:
            return "categorical"
        else:
            return "numeric"
    
    # Check if binary (2 unique values)
    unique_count = series.nunique()
    if unique_count == 2:
        return "binary"
    elif unique_count <= 20:
        return "categorical"
    else:
        return "text"


def detect_protected_attributes(df: pd.DataFrame) -> List[ProtectedAttributeSuggestion]:
    """Detect potential protected attribute columns"""
    suggestions = []
    
    for col in df.columns:
        col_lower = col.lower()
        confidence = "low"
        unique_count = df[col].nunique()
        
        # Skip columns with too many or too few unique values
        if unique_count < 2 or unique_count > 10:
            continue
        
        # Check if column name matches protected attribute keywords
        for keyword in PROTECTED_ATTR_KEYWORDS:
            if keyword in col_lower:
                confidence = "high"
                break
        
        # If high confidence or categorical with reasonable unique values
        if confidence == "high" or (unique_count >= 2 and unique_count <= 10):
            if confidence == "low":
                confidence = "medium"
            
            detected_groups = df[col].dropna().unique().tolist()
            
            suggestions.append(ProtectedAttributeSuggestion(
                column=col,
                confidence=confidence,
                detected_groups=[str(g) for g in detected_groups[:10]]  # Limit to 10
            ))
    
    # Sort by confidence
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: confidence_order[x.confidence])
    
    return suggestions[:5]  # Return top 5

def detect_outcome_column(df: pd.DataFrame) -> OutcomeSuggestion:
    """Detect potential outcome column"""
    for col in df.columns:
        col_lower = col.lower()
        
        # Check if column name matches outcome keywords
        for keyword in OUTCOME_KEYWORDS:
            if keyword in col_lower:
                # Check if binary
                if df[col].nunique() == 2:
                    return OutcomeSuggestion(column=col, confidence="high")
                else:
                    return OutcomeSuggestion(column=col, confidence="medium")
    
    # Fallback: find binary columns
    for col in df.columns:
        if df[col].nunique() == 2:
            return OutcomeSuggestion(column=col, confidence="low")
    
    # Default to last column
    return OutcomeSuggestion(column=df.columns[-1], confidence="low")


@router.post("/validate-schema", response_model=SchemaValidationResponse)
async def validate_schema(request: SchemaValidationRequest):
    """
    Validate and analyze CSV schema
    
    - Detects column types
    - Identifies protected attributes
    - Suggests outcome column
    - Flags missing values and data quality issues
    """
    request_id = generate_request_id()
    
    # Get session
    if request.session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Session Not Found",
                "message": "Session not found.",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    session = sessions[request.session_id]
    df = session["dataframe"]
    
    # Analyze columns
    columns_info = []
    warnings = []
    
    for col in df.columns:
        series = df[col]
        
        # Calculate statistics
        unique_values = series.nunique()
        missing_count = series.isna().sum()
        missing_percentage = (missing_count / len(series)) * 100
        
        # Get sample values
        sample_values = series.dropna().head(5).tolist()
        
        # Detect type
        detected_type = detect_column_type(series)
        
        columns_info.append(ColumnInfo(
            name=col,
            detected_type=detected_type,
            unique_values=unique_values,
            missing_percentage=round(missing_percentage, 2),
            sample_values=sample_values
        ))
        
        # Generate warnings
        if missing_percentage > 30:
            warnings.append(SchemaWarning(
                column=col,
                issue="high_missing",
                message=f"Column '{col}' has {missing_percentage:.1f}% missing values"
            ))
        
        if detected_type == "categorical" and unique_values > 10:
            warnings.append(SchemaWarning(
                column=col,
                issue="too_many_categories",
                message=f"Column '{col}' has {unique_values} categories (consider grouping)"
            ))
    
    # Detect protected attributes and outcome
    protected_attrs = detect_protected_attributes(df)
    outcome = detect_outcome_column(df)
    
    # Feature columns (all except protected and outcome)
    feature_columns = [
        col for col in df.columns 
        if col != outcome.column and col not in [pa.column for pa in protected_attrs]
    ]
    
    suggestions = SchemaSuggestions(
        protected_attributes=protected_attrs,
        outcome_column=outcome,
        feature_columns=feature_columns
    )
    
    return SchemaValidationResponse(
        columns=columns_info,
        suggestions=suggestions,
        warnings=warnings
    )
