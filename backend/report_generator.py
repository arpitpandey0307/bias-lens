from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
import os

def create_pdf_report(
    analysis_data: dict,
    session_data: dict,
    output_path: str = None
) -> BytesIO:
    """
    Generate a PDF report for fairness analysis
    
    Args:
        analysis_data: Analysis results from /api/analyze
        session_data: Session metadata
        output_path: Optional file path to save PDF
    
    Returns:
        BytesIO buffer containing the PDF
    """
    # Create buffer
    buffer = BytesIO()
    
    # Create document
    if output_path:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
    else:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003d9b'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0b1c30'),
        spaceAfter=10,
        spaceBefore=20
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#0b1c30'),
        spaceAfter=8
    )
    
    # Cover Page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph("BiasLens Fairness Audit Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Compliance stamp
    stamp_style = ParagraphStyle(
        'Stamp',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#065f46'),
        alignment=TA_CENTER,
        borderColor=colors.HexColor('#065f46'),
        borderWidth=2,
        borderPadding=10
    )
    elements.append(Paragraph("COMPLIANCE READY", stamp_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Metadata
    metadata_data = [
        ['Dataset:', session_data.get('filename', 'N/A')],
        ['Analysis Date:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
        ['Total Records:', str(session_data.get('row_count', 0))],
        ['Protected Groups:', ', '.join(analysis_data.get('protected_groups', []))],
        ['Computation Time:', f"{analysis_data.get('computation_time_ms', 0)}ms"]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0b1c30')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(metadata_table)
    
    elements.append(PageBreak())
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    
    # Count metrics by status
    metrics = analysis_data.get('metrics', {})
    pass_count = sum(1 for m in metrics.values() if m['threshold_status'] == 'pass')
    warning_count = sum(1 for m in metrics.values() if m['threshold_status'] == 'warning')
    fail_count = sum(1 for m in metrics.values() if m['threshold_status'] == 'fail')
    
    summary_text = f"""
    This report presents a comprehensive fairness analysis of the dataset "{session_data.get('filename', 'N/A')}" 
    containing {session_data.get('row_count', 0)} records across {len(analysis_data.get('protected_groups', []))} 
    demographic groups.
    <br/><br/>
    <b>Fairness Assessment:</b><br/>
    • {pass_count} metric(s) passed fairness thresholds<br/>
    • {warning_count} metric(s) showed potential concerns<br/>
    • {fail_count} metric(s) indicated significant bias
    """
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Fairness Metrics Section
    elements.append(Paragraph("Fairness Metrics", heading_style))
    
    metric_names = {
        'statistical_parity_difference': 'Statistical Parity Difference',
        'disparate_impact': 'Disparate Impact',
        'equal_opportunity_difference': 'Equal Opportunity Difference',
        'predictive_parity_difference': 'Predictive Parity Difference'
    }
    
    for metric_key, metric_data in metrics.items():
        metric_name = metric_names.get(metric_key, metric_key)
        status = metric_data['threshold_status']
        value = metric_data['value']
        
        # Status color
        if status == 'pass':
            status_color = colors.HexColor('#065f46')
            status_text = 'PASS ✓'
        elif status == 'warning':
            status_color = colors.HexColor('#7b2600')
            status_text = 'WARNING ⚠'
        else:
            status_color = colors.HexColor('#ba1a1a')
            status_text = 'FAIL ✕'
        
        metric_header = f"<b>{metric_name}</b>"
        elements.append(Paragraph(metric_header, body_style))
        
        metric_info = [
            ['Value:', f"{value:.4f}"],
            ['Status:', status_text],
        ]
        
        metric_table = Table(metric_info, colWidths=[1.5*inch, 4.5*inch])
        metric_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0b1c30')),
            ('TEXTCOLOR', (1, 1), (1, 1), status_color),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(metric_table)
        elements.append(Spacer(1, 0.2*inch))
    
    elements.append(PageBreak())

    
    # Group Statistics Section
    elements.append(Paragraph("Group Statistics", heading_style))
    
    group_stats = analysis_data.get('group_statistics', {})
    
    # Create table data
    table_data = [['Group', 'Total Count', 'Approved', 'Approval Rate']]
    
    for group, stats in group_stats.items():
        table_data.append([
            group,
            str(stats['total_count']),
            str(stats['positive_outcomes']),
            f"{stats['approval_rate']*100:.1f}%"
        ])
    
    # Create table
    stats_table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eff4ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0b1c30')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c3c6d6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')])
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Confusion Matrices Section
    elements.append(Paragraph("Confusion Matrices", heading_style))
    
    for group, stats in group_stats.items():
        cm = stats['confusion_matrix']
        
        elements.append(Paragraph(f"<b>{group}</b>", body_style))
        
        cm_data = [
            ['', 'Predicted Positive', 'Predicted Negative'],
            ['Actual Positive', str(cm['true_positive']), str(cm['false_negative'])],
            ['Actual Negative', str(cm['false_positive']), str(cm['true_negative'])]
        ]
        
        cm_table = Table(cm_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
        cm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eff4ff')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff4ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0b1c30')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c3c6d6')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(cm_table)
        elements.append(Spacer(1, 0.2*inch))
    
    elements.append(PageBreak())
    
    # Recommendations Section
    elements.append(Paragraph("Recommendations", heading_style))
    
    recommendations = []
    
    if fail_count > 0:
        recommendations.append(
            "• <b>Critical Action Required:</b> Significant bias detected in one or more metrics. "
            "Immediate review and mitigation strategies are recommended."
        )
    
    if warning_count > 0:
        recommendations.append(
            "• <b>Monitor Closely:</b> Some metrics show potential fairness concerns. "
            "Consider implementing bias mitigation techniques and ongoing monitoring."
        )
    
    if pass_count == len(metrics):
        recommendations.append(
            "• <b>Good Standing:</b> All fairness metrics are within acceptable thresholds. "
            "Continue regular monitoring to maintain fairness standards."
        )
    
    recommendations.append(
        "• <b>Regular Audits:</b> Conduct fairness audits quarterly to ensure ongoing compliance "
        "with fairness standards and regulatory requirements."
    )
    
    recommendations.append(
        "• <b>Stakeholder Review:</b> Share this report with legal, compliance, and executive teams "
        "to ensure organizational awareness of fairness metrics."
    )
    
    for rec in recommendations:
        elements.append(Paragraph(rec, body_style))
        elements.append(Spacer(1, 0.1*inch))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Generated by BiasLens Fairness Auditor | {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    if output_path:
        return None
    else:
        buffer.seek(0)
        return buffer
