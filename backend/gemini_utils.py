"""
Gemini AI integration for generating natural-language bias explanations
and actionable recommendations from fairness analysis results.
"""

import os
import google.generativeai as genai
from typing import Dict, Optional


def _build_prompt(
    metrics: Dict,
    group_statistics: Dict,
    protected_attribute: str,
    outcome_column: str
) -> str:
    """Build a structured prompt for Gemini to analyze fairness results."""

    # Format metrics summary
    metrics_text = ""
    for name, metric in metrics.items():
        readable_name = name.replace("_", " ").title()
        status = metric.get("threshold_status", "unknown")
        value = metric.get("value", 0)
        metrics_text += f"- {readable_name}: {value:.4f} (Status: {status.upper()})\n"

    # Format group statistics
    groups_text = ""
    for group, stats in group_statistics.items():
        total = stats.get("total_count", 0)
        positive = stats.get("positive_outcomes", 0)
        rate = stats.get("approval_rate", 0)
        groups_text += f"- {group}: {total} total, {positive} positive outcomes, {rate*100:.1f}% approval rate\n"

    prompt = f"""You are a fairness auditing expert. Analyze the following AI bias audit results and provide:

1. **Summary**: A 2-3 sentence plain-English summary of the key findings. State whether significant bias was detected and which groups are most affected.

2. **Key Findings**: 3-4 bullet points highlighting the most important observations from the metrics.

3. **Recommendations**: 3-4 actionable recommendations to address any detected bias.

## Audit Details
- **Protected Attribute**: {protected_attribute}
- **Outcome Column**: {outcome_column}

## Fairness Metrics
{metrics_text}

## Group Statistics
{groups_text}

## Metric Interpretation Guide:
- Statistical Parity Difference: Range [-1,1], fair = [-0.1, 0.1]. Measures equal approval rates.
- Disparate Impact: Range [0, inf], fair = [0.8, 1.25]. The four-fifths rule.
- Equal Opportunity Difference: Range [-1,1], fair = [-0.1, 0.1]. Equal true positive rates.
- Predictive Parity Difference: Range [-1,1], fair = [-0.1, 0.1]. Equal prediction accuracy.

Respond in this exact JSON format:
{{
  "summary": "...",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "risk_level": "low|medium|high|critical"
}}

Only return the JSON object, no other text."""

    return prompt


async def generate_bias_explanation(
    metrics: Dict,
    group_statistics: Dict,
    protected_attribute: str,
    outcome_column: str
) -> Optional[Dict]:
    """
    Call Gemini API to generate natural-language bias explanations.
    Returns None if API key is not configured or call fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        print("[WARN] GEMINI_API_KEY not set — skipping AI explanation generation")
        return None

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.0-flash")

        # Convert Pydantic models to dicts for prompt building
        metrics_dict = {}
        for name, metric in metrics.items():
            if hasattr(metric, 'model_dump'):
                metrics_dict[name] = metric.model_dump()
            elif hasattr(metric, 'dict'):
                metrics_dict[name] = metric.dict()
            else:
                metrics_dict[name] = metric

        stats_dict = {}
        for name, stat in group_statistics.items():
            if hasattr(stat, 'model_dump'):
                stats_dict[name] = stat.model_dump()
            elif hasattr(stat, 'dict'):
                stats_dict[name] = stat.dict()
            else:
                stats_dict[name] = stat

        prompt = _build_prompt(metrics_dict, stats_dict, protected_attribute, outcome_column)

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

        # Parse the JSON response
        import json
        result = json.loads(response.text)

        return {
            "summary": result.get("summary", ""),
            "key_findings": result.get("key_findings", []),
            "recommendations": result.get("recommendations", []),
            "risk_level": result.get("risk_level", "medium"),
            "powered_by": "Gemini 2.0 Flash"
        }

    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        return None
