import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def _encode_outcome_column(df: pd.DataFrame, outcome_column: str) -> pd.Series:
    """
    Ensure outcome column is binary numeric (0/1).
    Handles string labels like '<=50K'/>50K', 'Yes'/'No', etc.
    """
    series = df[outcome_column]

    # Already numeric binary
    if pd.api.types.is_numeric_dtype(series):
        unique_vals = sorted(series.dropna().unique())
        if set(unique_vals).issubset({0, 1}):
            return series
        # Numeric but not 0/1 — map min to 0, max to 1
        if len(unique_vals) == 2:
            return series.map({unique_vals[0]: 0, unique_vals[1]: 1})
        return series

    # String/categorical — encode to 0/1
    unique_vals = sorted(series.dropna().unique())
    if len(unique_vals) == 2:
        # Try to pick the "positive" label intelligently
        positive_keywords = ['>50k', '>50K', 'yes', 'Yes', 'true', 'True', '1',
                            'approved', 'hired', 'accepted', 'admitted', 'positive']
        if any(kw in str(unique_vals[1]) for kw in positive_keywords):
            mapping = {unique_vals[0]: 0, unique_vals[1]: 1}
        elif any(kw in str(unique_vals[0]) for kw in positive_keywords):
            mapping = {unique_vals[0]: 1, unique_vals[1]: 0}
        else:
            # Default: alphabetical order, second value = 1
            mapping = {unique_vals[0]: 0, unique_vals[1]: 1}
        return series.map(mapping)

    # Fallback: use category codes
    return pd.Categorical(series).codes


def compute_statistical_parity_difference(
    df: pd.DataFrame,
    protected_attribute: str,
    outcome_column: str
) -> Dict[str, float]:
    """
    Compute statistical parity difference
    
    Statistical Parity Difference = P(Y=1|A=privileged) - P(Y=1|A=unprivileged)
    Range: [-1, 1], 0 is perfect fairness
    """
    outcome = _encode_outcome_column(df, outcome_column)

    results = {}
    groups = df[protected_attribute].unique()
    
    # Calculate approval rate for each group
    approval_rates = {}
    for group in groups:
        mask = df[protected_attribute] == group
        group_outcome = outcome[mask]
        approval_rate = group_outcome.mean()
        approval_rates[str(group)] = approval_rate
    
    # Calculate pairwise differences
    group_list = list(approval_rates.keys())
    if len(group_list) >= 2:
        # Use first group as reference (privileged)
        privileged_rate = approval_rates[group_list[0]]
        
        for group in group_list[1:]:
            unprivileged_rate = approval_rates[group]
            spd = privileged_rate - unprivileged_rate
            results[f"{group_list[0]}_vs_{group}"] = spd
    
    # Overall SPD (max - min)
    if len(approval_rates) > 0:
        max_rate = max(approval_rates.values())
        min_rate = min(approval_rates.values())
        results["overall"] = max_rate - min_rate
    
    return results


def compute_disparate_impact(
    df: pd.DataFrame,
    protected_attribute: str,
    outcome_column: str
) -> Dict[str, float]:
    """
    Compute disparate impact ratio
    
    Disparate Impact = P(Y=1|A=unprivileged) / P(Y=1|A=privileged)
    Range: [0, inf], 1 is perfect fairness, <0.8 or >1.25 indicates bias
    """
    outcome = _encode_outcome_column(df, outcome_column)

    results = {}
    groups = df[protected_attribute].unique()
    
    # Calculate approval rate for each group
    approval_rates = {}
    for group in groups:
        mask = df[protected_attribute] == group
        group_outcome = outcome[mask]
        approval_rate = group_outcome.mean()
        approval_rates[str(group)] = max(approval_rate, 0.0001)  # Avoid division by zero
    
    # Calculate pairwise ratios
    group_list = list(approval_rates.keys())
    if len(group_list) >= 2:
        privileged_rate = approval_rates[group_list[0]]
        
        for group in group_list[1:]:
            unprivileged_rate = approval_rates[group]
            di = unprivileged_rate / privileged_rate if privileged_rate > 0 else 0
            results[f"{group}_vs_{group_list[0]}"] = di
    
    # Overall DI (min / max)
    if len(approval_rates) > 0:
        max_rate = max(approval_rates.values())
        min_rate = min(approval_rates.values())
        results["overall"] = min_rate / max_rate if max_rate > 0 else 0
    
    return results

def compute_equal_opportunity_difference(
    df: pd.DataFrame,
    protected_attribute: str,
    outcome_column: str,
    predicted_column: str = None
) -> Dict[str, float]:
    """
    Compute equal opportunity difference (True Positive Rate difference)
    
    Equal Opportunity Difference = TPR(privileged) - TPR(unprivileged)
    Range: [-1, 1], 0 is perfect fairness
    """
    outcome = _encode_outcome_column(df, outcome_column)

    # If no predictions, use outcome as both true and predicted
    if predicted_column is None:
        predicted = outcome
    else:
        predicted = _encode_outcome_column(df, predicted_column)
    
    results = {}
    groups = df[protected_attribute].unique()
    
    # Calculate TPR for each group
    tpr_rates = {}
    for group in groups:
        mask = df[protected_attribute] == group
        group_actual = outcome[mask]
        group_predicted = predicted[mask]
        # TPR = TP / (TP + FN) = TP / P (all actual positives)
        actual_positive_mask = group_actual == 1
        if actual_positive_mask.sum() > 0:
            tpr = group_predicted[actual_positive_mask].mean()
            tpr_rates[str(group)] = tpr
        else:
            tpr_rates[str(group)] = 0.0
    
    # Calculate pairwise differences
    group_list = list(tpr_rates.keys())
    if len(group_list) >= 2:
        privileged_tpr = tpr_rates[group_list[0]]
        
        for group in group_list[1:]:
            unprivileged_tpr = tpr_rates[group]
            eod = privileged_tpr - unprivileged_tpr
            results[f"{group_list[0]}_vs_{group}"] = eod
    
    # Overall EOD (max - min)
    if len(tpr_rates) > 0:
        max_tpr = max(tpr_rates.values())
        min_tpr = min(tpr_rates.values())
        results["overall"] = max_tpr - min_tpr
    
    return results

def compute_predictive_parity_difference(
    df: pd.DataFrame,
    protected_attribute: str,
    outcome_column: str,
    predicted_column: str = None
) -> Dict[str, float]:
    """
    Compute predictive parity difference (Positive Predictive Value difference)
    
    Predictive Parity Difference = PPV(privileged) - PPV(unprivileged)
    Range: [-1, 1], 0 is perfect fairness
    """
    outcome = _encode_outcome_column(df, outcome_column)

    # If no predictions, use outcome as both true and predicted
    if predicted_column is None:
        predicted = outcome
    else:
        predicted = _encode_outcome_column(df, predicted_column)
    
    results = {}
    groups = df[protected_attribute].unique()
    
    # Calculate PPV for each group
    ppv_rates = {}
    for group in groups:
        mask = df[protected_attribute] == group
        group_actual = outcome[mask]
        group_predicted = predicted[mask]
        # PPV = TP / (TP + FP) = TP / (all predicted positives)
        predicted_positive_mask = group_predicted == 1
        if predicted_positive_mask.sum() > 0:
            ppv = group_actual[predicted_positive_mask].mean()
            ppv_rates[str(group)] = ppv
        else:
            ppv_rates[str(group)] = 0.0
    
    # Calculate pairwise differences
    group_list = list(ppv_rates.keys())
    if len(group_list) >= 2:
        privileged_ppv = ppv_rates[group_list[0]]
        
        for group in group_list[1:]:
            unprivileged_ppv = ppv_rates[group]
            ppd = privileged_ppv - unprivileged_ppv
            results[f"{group_list[0]}_vs_{group}"] = ppd
    
    # Overall PPD (max - min)
    if len(ppv_rates) > 0:
        max_ppv = max(ppv_rates.values())
        min_ppv = min(ppv_rates.values())
        results["overall"] = max_ppv - min_ppv
    
    return results

def compute_confusion_matrix(
    df: pd.DataFrame,
    protected_attribute: str,
    outcome_column: str,
    predicted_column: str = None
) -> Dict[str, Dict[str, int]]:
    """
    Compute confusion matrix for each protected group
    """
    outcome = _encode_outcome_column(df, outcome_column)

    if predicted_column is None:
        predicted = outcome
    else:
        predicted = _encode_outcome_column(df, predicted_column)
    
    results = {}
    groups = df[protected_attribute].unique()
    
    for group in groups:
        mask = df[protected_attribute] == group
        group_actual = outcome[mask]
        group_predicted = predicted[mask]
        
        tp = int(((group_actual == 1) & (group_predicted == 1)).sum())
        fp = int(((group_actual == 0) & (group_predicted == 1)).sum())
        tn = int(((group_actual == 0) & (group_predicted == 0)).sum())
        fn = int(((group_actual == 1) & (group_predicted == 0)).sum())
        
        results[str(group)] = {
            "true_positive": tp,
            "false_positive": fp,
            "true_negative": tn,
            "false_negative": fn
        }
    
    return results
