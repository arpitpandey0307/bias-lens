from jinja2 import Template
from datetime import datetime
from typing import Dict, Any, List
import base64
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BiasLens Fairness Audit Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f8f9ff;
            color: #0b1c30;
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .header {
            background: linear-gradient(135deg, #003d9b 0%, #0052cc 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 8px;
            margin-bottom: 40px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .stamp {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 4px;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 12px 40px rgba(11, 28, 48, 0.06);
        }
        .section h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #003d9b;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            padding: 20px;
            border-radius: 8px;
            background: #f8f9ff;
        }
        .metric-card h3 {
            font-size: 0.875rem;
            color: #44474f;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-pass { background: #d1fae5; color: #065f46; }
        .status-warning { background: #fef3c7; color: #92400e; }
        .status-fail { background: #ffdad6; color: #410002; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e6f0;
        }
        th {
            background: #eff4ff;
            font-weight: 600;
            color: #003d9b;
        }
        .chart-container {
            margin: 30px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .recommendation {
            background: #dbeafe;
            padding: 15px;
            border-left: 4px solid #1e40af;
            margin: 10px 0;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            padding: 40px 20px;
            color: #44474f;
            font-size: 0.875rem;
        }
        @media print {
            .section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BiasLens Fairness Audit Report</h1>
            <p>{{ dataset_name }}</p>
            <div class="stamp">Generated: {{ generated_at }}</div>
        </div>

        {% if include_sections.executive_summary %}
        <div class="section">
            <h2>Executive Summary</h2>
            <p style="margin-bottom: 20px;">
                This report analyzes fairness across {{ num_groups }} protected groups 
                using {{ num_metrics }} industry-standard fairness metrics.
            </p>
            <div class="metric-grid">
                <div class="metric-card">
                    <h3>Metrics Passed</h3>
                    <div class="metric-value" style="color: #065f46;">{{ metrics_passed }}</div>
                </div>
                <div class="metric-card">
                    <h3>Warnings</h3>
                    <div class="metric-value" style="color: #92400e;">{{ metrics_warning }}</div>
                </div>
                <div class="metric-card">
                    <h3>Failed</h3>
                    <div class="metric-value" style="color: #ba1a1a;">{{ metrics_failed }}</div>
                </div>
            </div>
        </div>
        {% endif %}

        {% if include_sections.data_overview %}
        <div class="section">
            <h2>Data Overview</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Rows</td><td>{{ row_count }}</td></tr>
                <tr><td>Protected Attribute</td><td>{{ protected_attribute }}</td></tr>
                <tr><td>Outcome Column</td><td>{{ outcome_column }}</td></tr>
                <tr><td>Protected Groups</td><td>{{ protected_groups|join(', ') }}</td></tr>
            </table>
        </div>
        {% endif %}

        {% if include_sections.fairness_metrics %}
        <div class="section">
            <h2>Fairness Metrics</h2>
            {% for metric_name, metric_data in metrics.items() %}
            <div class="metric-card" style="margin-bottom: 20px;">
                <h3>{{ metric_name }}</h3>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="metric-value">{{ "%.3f"|format(metric_data.value) }}</div>
                    <span class="status-badge status-{{ metric_data.threshold_status }}">
                        {{ metric_data.threshold_status }}
                    </span>
                </div>
                <p style="margin-top: 10px; font-size: 0.875rem; color: #44474f;">
                    {{ metric_descriptions[metric_name] }}
                </p>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if include_sections.visualizations and chart_image %}
        <div class="section">
            <h2>Group Statistics</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{{ chart_image }}" alt="Approval Rate by Group">
            </div>
            <table>
                <tr>
                    <th>Group</th>
                    <th>Total Count</th>
                    <th>Positive Outcomes</th>
                    <th>Approval Rate</th>
                </tr>
                {% for group, stats in group_statistics.items() %}
                <tr>
                    <td>{{ group }}</td>
                    <td>{{ stats.total_count }}</td>
                    <td>{{ stats.positive_outcomes }}</td>
                    <td>{{ "%.1f"|format(stats.approval_rate * 100) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}

        {% if include_sections.recommendations %}
        <div class="section">
            <h2>Recommendations</h2>
            {% for rec in recommendations %}
            <div class="recommendation">
                <strong>{{ rec.title }}</strong>
                <p>{{ rec.description }}</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by BiasLens Fairness Auditor v1.0.0</p>
            <p>Report ID: {{ report_id }}</p>
        </div>
    </div>
</body>
</html>
"""

METRIC_DESCRIPTIONS = {
    "Statistical Parity Difference": "Measures the difference in positive outcome rates between groups. Values close to 0 indicate fairness.",
    "Disparate Impact": "Ratio of positive outcome rates. Values close to 1.0 indicate fairness.",
    "Equal Opportunity Difference": "Measures difference in true positive rates between groups. Values close to 0 indicate fairness.",
    "Predictive Parity Difference": "Measures difference in precision between groups. Values close to 0 indicate fairness."
}

def generate_approval_rate_chart(group_statistics: Dict[str, Any]) -> str:
    """Generate approval rate bar chart as base64 image"""
    groups = list(group_statistics.keys())
    rates = [stats['approval_rate'] * 100 for stats in group_statistics.values()]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(groups, rates, color='#003d9b')
    ax.set_xlabel('Approval Rate (%)', fontsize=12)
    ax.set_title('Approval Rate by Protected Group', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 100)
    
    for i, (bar, rate) in enumerate(zip(bars, rates)):
        ax.text(rate + 2, i, f'{rate:.1f}%', va='center', fontsize=10)
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64

def generate_recommendations(metrics: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actionable recommendations based on metrics"""
    recommendations = []
    
    for metric_name, metric_data in metrics.items():
        if metric_data['threshold_status'] == 'fail':
            if 'Parity' in metric_name:
                recommendations.append({
                    "title": f"Address {metric_name}",
                    "description": "Consider reweighing your training data or adjusting decision thresholds to reduce disparity between groups."
                })
            elif 'Impact' in metric_name:
                recommendations.append({
                    "title": f"Improve {metric_name}",
                    "description": "The ratio of positive outcomes is significantly different. Review your model's feature importance and consider bias mitigation techniques."
                })
    
    if not recommendations:
        recommendations.append({
            "title": "Maintain Current Standards",
            "description": "Your model shows good fairness across all measured metrics. Continue monitoring with regular audits."
        })
    
    return recommendations

def generate_html_report(
    analysis_data: Dict[str, Any],
    report_id: str,
    include_sections: Dict[str, bool]
) -> str:
    """Generate HTML fairness report"""
    
    # Count metric statuses
    metrics_passed = sum(1 for m in analysis_data['metrics'].values() if m['threshold_status'] == 'pass')
    metrics_warning = sum(1 for m in analysis_data['metrics'].values() if m['threshold_status'] == 'warning')
    metrics_failed = sum(1 for m in analysis_data['metrics'].values() if m['threshold_status'] == 'fail')
    
    # Generate chart
    chart_image = None
    if include_sections.get('visualizations', True):
        chart_image = generate_approval_rate_chart(analysis_data['group_statistics'])
    
    # Generate recommendations
    recommendations = generate_recommendations(analysis_data['metrics'])
    
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        dataset_name=analysis_data.get('dataset_name', 'Fairness Analysis'),
        generated_at=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        report_id=report_id,
        num_groups=len(analysis_data['protected_groups']),
        num_metrics=len(analysis_data['metrics']),
        metrics_passed=metrics_passed,
        metrics_warning=metrics_warning,
        metrics_failed=metrics_failed,
        row_count=analysis_data.get('row_count', 'N/A'),
        protected_attribute=analysis_data.get('protected_attribute', 'N/A'),
        outcome_column=analysis_data.get('outcome_column', 'N/A'),
        protected_groups=analysis_data['protected_groups'],
        metrics=analysis_data['metrics'],
        metric_descriptions=METRIC_DESCRIPTIONS,
        group_statistics=analysis_data['group_statistics'],
        chart_image=chart_image,
        recommendations=recommendations,
        include_sections=include_sections
    )
    
    return html_content
