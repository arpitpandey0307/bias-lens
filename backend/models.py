from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any

# Session Models
class Session(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    filename: str
    upload_timestamp: datetime
    row_count: int
    column_count: int
    file_path: str
    expires_at: datetime

class UploadResponse(BaseModel):
    session_id: str
    filename: str
    size_bytes: int
    row_count: int
    column_count: int
    preview: List[Dict[str, Any]]
    warnings: List[Dict[str, str]] = []

# Schema Models
class ColumnInfo(BaseModel):
    name: str
    detected_type: Literal["numeric", "categorical", "binary", "text"]
    unique_values: int
    missing_percentage: float
    sample_values: List[Any]

class ProtectedAttributeSuggestion(BaseModel):
    column: str
    confidence: Literal["high", "medium", "low"]
    detected_groups: List[str]

class OutcomeSuggestion(BaseModel):
    column: str
    confidence: Literal["high", "medium", "low"]

class SchemaSuggestions(BaseModel):
    protected_attributes: List[ProtectedAttributeSuggestion]
    outcome_column: OutcomeSuggestion
    feature_columns: List[str]

class SchemaWarning(BaseModel):
    column: str
    issue: Literal["high_missing", "too_many_categories", "low_variance"]
    message: str

class SchemaValidationResponse(BaseModel):
    columns: List[ColumnInfo]
    suggestions: SchemaSuggestions
    warnings: List[SchemaWarning] = []

# Error Response
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[str] = None
    timestamp: datetime
    request_id: str


# Analysis Models
class AnalyzeRequest(BaseModel):
    session_id: str
    protected_attribute: str
    outcome_column: str
    feature_columns: List[str] = []

class MetricResult(BaseModel):
    value: float
    threshold_status: Literal["pass", "warning", "fail"]
    by_group: Dict[str, float]

class ConfusionMatrixData(BaseModel):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

class GroupStatistics(BaseModel):
    total_count: int
    positive_outcomes: int
    approval_rate: float
    confusion_matrix: ConfusionMatrixData

class FairnessAnalysisResponse(BaseModel):
    analysis_id: str
    protected_groups: List[str]
    metrics: Dict[str, MetricResult]
    group_statistics: Dict[str, GroupStatistics]
    computation_time_ms: int


# Export Models
class ExportRequest(BaseModel):
    analysis_id: str
    format: Literal["pdf", "html"] = "pdf"
    include_sections: Dict[str, bool] = {
        "executive_summary": True,
        "data_overview": True,
        "fairness_metrics": True,
        "visualizations": True,
        "recommendations": True
    }

class ExportResponse(BaseModel):
    report_id: str
    download_url: str
    filename: str
    size_bytes: int
    generated_at: datetime
    expires_at: datetime
