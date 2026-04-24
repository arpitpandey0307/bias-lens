from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import time
import uuid

from models import AnalyzeRequest, FairnessAnalysisResponse, MetricResult, GroupStatistics, ConfusionMatrixData
from fairness_utils import (
    compute_statistical_parity_difference,
    compute_disparate_impact,
    compute_equal_opportunity_difference,
    compute_predictive_parity_difference,
    compute_confusion_matrix,
    _encode_outcome_column
)
from utils import generate_request_id

router = APIRouter(prefix="/api", tags=["analyze"])

# Import sessions from upload router
from routers.upload import sessions

# Store analyses
analyses = {}

def classify_threshold(value: float, metric_type: str) -> str:
    """Classify metric value into pass/warning/fail based on thresholds"""
    if metric_type == "statistical_parity_difference":
        if -0.1 <= value <= 0.1:
            return "pass"
        elif -0.2 <= value <= 0.2:
            return "warning"
        else:
            return "fail"
    
    elif metric_type == "disparate_impact":
        if 0.8 <= value <= 1.25:
            return "pass"
        elif 0.7 <= value <= 1.4:
            return "warning"
        else:
            return "fail"
    
    elif metric_type in ["equal_opportunity_difference", "predictive_parity_difference"]:
        if -0.1 <= value <= 0.1:
            return "pass"
        elif -0.2 <= value <= 0.2:
            return "warning"
        else:
            return "fail"
    
    return "warning"

@router.post("/analyze", response_model=FairnessAnalysisResponse)
async def analyze_fairness(request: AnalyzeRequest):
    """
    Analyze fairness metrics for uploaded dataset
    
    Computes:
    - Statistical parity difference
    - Disparate impact
    - Equal opportunity difference
    - Predictive parity difference
    """
    request_id = generate_request_id()
    start_time = time.time()
    
    # Debug logging
    print(f"[DEBUG] Analyze request received:")
    print(f"  Session ID: {request.session_id}")
    print(f"  Protected attribute: {request.protected_attribute}")
    print(f"  Outcome column: {request.outcome_column}")
    print(f"  Available sessions: {list(sessions.keys())}")
    
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
    
    # Validate columns exist
    if request.protected_attribute not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid Column",
                "message": f"Protected attribute '{request.protected_attribute}' not found in dataset",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    if request.outcome_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid Column",
                "message": f"Outcome column '{request.outcome_column}' not found in dataset",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    # Validate outcome column is binary
    unique_outcomes = df[request.outcome_column].nunique()
    if unique_outcomes != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid Outcome Column",
                "message": f"Outcome column '{request.outcome_column}' must be binary (have exactly 2 unique values). Found {unique_outcomes} unique values. Please select a binary column.",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )

    
    # Get protected groups (use original dtype values for filtering)
    protected_groups_raw = df[request.protected_attribute].unique().tolist()
    protected_groups = [str(g) for g in protected_groups_raw]
    
    print(f"[DEBUG] Protected groups count: {len(protected_groups)}")
    print(f"[DEBUG] First 10 groups: {protected_groups[:10]}")
    
    # Check for too many groups
    if len(protected_groups) > 10:
        print(f"[ERROR] Too many groups: {len(protected_groups)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Too Many Groups",
                "message": f"Protected attribute '{request.protected_attribute}' has {len(protected_groups)} groups. Maximum 10 groups allowed. Please select a categorical column with fewer groups (e.g., gender, race).",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    # Compute metrics
    try:
        spd_results = compute_statistical_parity_difference(
            df, request.protected_attribute, request.outcome_column
        )
        di_results = compute_disparate_impact(
            df, request.protected_attribute, request.outcome_column
        )
        eod_results = compute_equal_opportunity_difference(
            df, request.protected_attribute, request.outcome_column
        )
        ppd_results = compute_predictive_parity_difference(
            df, request.protected_attribute, request.outcome_column
        )
        confusion_matrices = compute_confusion_matrix(
            df, request.protected_attribute, request.outcome_column
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Computation Error",
                "message": f"Unable to compute metrics: {str(e)}",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        )
    
    # Build metrics response
    metrics = {
        "statistical_parity_difference": MetricResult(
            value=spd_results.get("overall", 0.0),
            threshold_status=classify_threshold(spd_results.get("overall", 0.0), "statistical_parity_difference"),
            by_group=spd_results
        ),
        "disparate_impact": MetricResult(
            value=di_results.get("overall", 1.0),
            threshold_status=classify_threshold(di_results.get("overall", 1.0), "disparate_impact"),
            by_group=di_results
        ),
        "equal_opportunity_difference": MetricResult(
            value=eod_results.get("overall", 0.0),
            threshold_status=classify_threshold(eod_results.get("overall", 0.0), "equal_opportunity_difference"),
            by_group=eod_results
        ),
        "predictive_parity_difference": MetricResult(
            value=ppd_results.get("overall", 0.0),
            threshold_status=classify_threshold(ppd_results.get("overall", 0.0), "predictive_parity_difference"),
            by_group=ppd_results
        )
    }
    
    # Build group statistics — encode outcome for counting
    encoded_outcome = _encode_outcome_column(df, request.outcome_column)
    
    group_stats = {}
    for group_raw, group_str in zip(protected_groups_raw, protected_groups):
        # Use original dtype value for filtering to avoid type mismatch
        group_mask = df[request.protected_attribute] == group_raw
        group_data = df[group_mask]
        total_count = len(group_data)
        positive_outcomes = int(encoded_outcome[group_mask].sum())
        approval_rate = positive_outcomes / total_count if total_count > 0 else 0.0
        
        cm = confusion_matrices.get(group_str, {
            "true_positive": 0,
            "false_positive": 0,
            "true_negative": 0,
            "false_negative": 0
        })
        
        group_stats[group_str] = GroupStatistics(
            total_count=total_count,
            positive_outcomes=positive_outcomes,
            approval_rate=approval_rate,
            confusion_matrix=ConfusionMatrixData(**cm)
        )
    
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Calculate computation time
    computation_time_ms = int((time.time() - start_time) * 1000)
    
    # Store analysis (include protected_attribute and outcome_column for export)
    analysis_result = FairnessAnalysisResponse(
        analysis_id=analysis_id,
        protected_groups=protected_groups,
        metrics=metrics,
        group_statistics=group_stats,
        computation_time_ms=computation_time_ms
    )
    
    analyses[analysis_id] = {
        "session_id": request.session_id,
        "result": analysis_result,
        "protected_attribute": request.protected_attribute,
        "outcome_column": request.outcome_column,
        "timestamp": datetime.utcnow()
    }
    
    return analysis_result
