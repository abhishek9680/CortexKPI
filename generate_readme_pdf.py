import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "CortexKPI_README.pdf")

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("🧠 CortexKPI — Autonomous Executive Storytelling Engine", title_style))
    story.append(Paragraph("<b>Accenture Innovation Challenge 2026</b> | Problem Statement 3: BusinessIntelligence.ai<br/><b>Team:</b> Team cognition (IIT Jodhpur) | <b>Authors:</b> Abhishek Gehlot & Saurav Gupta", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview &amp; Problem Statement", h2_style))
    story.append(Paragraph(
        "When high-stakes enterprise metrics drop (e.g. an unexpected <b>$250,000/day revenue loss</b> in APAC), executive leadership and engineering teams spend 6+ hours sifting through fragmented Datadog APM charts, Jira pull requests, Zendesk support tickets, and Slack alerts trying to answer: <i>What happened, why it happened, and how to fix it?</i><br/><br/>"
        "<b>CortexKPI</b> is a fully production-dynamic AI diagnostic engine that unifies seasonality-adjusted Bayesian anomaly detection, causal DAG decomposition with generalized graph propagation, multimodal RAG log vectorization, and epistemic safeguards into an interactive executive dashboard with <b>1-Click automated mitigation</b>. Zero hardcoded values — the entire 4-layer ML pipeline adapts to any uploaded dataset automatically.",
        body_style
    ))

    # The 4 ML Layers
    story.append(Paragraph("2. Architectural Pillars (The 4 ML Layers)", h2_style))
    
    layer_data = [
        ["Layer / Module", "Underlying ML Algorithm", "Core Purpose &amp; Enterprise Value"],
        ["Step 1: Metric Timeline\n&amp; Anomaly Detection", "Seasonal Day-of-Week Adjustment +\nBayesian Rolling Baselines (Student-t) +\nIsolation Forest Unsupervised ML", "Seasonality factor adjusts baselines by day-of-week patterns; calculates dynamic 95% CI bounds &amp; empirical p-values (p &lt; 0.001). Handles single-row edge cases gracefully."],
        ["Step 2: Causal Metric\nDependency Chain", "Structural Causal DAG (NetworkX) +\nGeneralized Edge Propagation +\nCounterfactual What-If Matrix", "Auto-adapts graph to any uploaded KPI schema. Data-driven variance attribution with zero hardcoded fallback constants. Supports both negative anomalies AND positive growth surges."],
        ["Step 3: Multimodal RAG\nEvidence Fusion", "TF-IDF N-Gram Vectorizer +\nCosine Similarity +\nExponential Temporal Decay", "Dynamically generates search queries from anomaly context. Weights logs by temporal proximity (half-life decay). Ranks across Jira, Zendesk, and Slack sources."],
        ["Step 4: Executive Verdict\n&amp; 1-Click Fix", "4-Pillar Epistemic Safeguards +\nDual-Engine Synthesis +\nLocal Qwen 3.8 / LLM AI Hook", "Surge-aware narrative (green for growth, red for outage). Context-aware action buttons (Scale Infrastructure vs Rollback). Confidence scoring counts GROWTH_SURGE status."]
    ]

    t = Table(layer_data, colWidths=[120, 175, 235])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Production-Level Dynamic Features
    story.append(Paragraph("3. Production-Level Dynamic Features", h2_style))
    story.append(Paragraph(
        "• <b>Zero Hardcoded Values:</b> All fallback defaults derived from live data baselines — no magic numbers (removed 420000, 98.0, 2.85, 120000, 185.0).<br/>"
        "• <b>Seasonality-Adjusted Baselines:</b> Day-of-week seasonal factors actively adjust rolling means to eliminate false weekend alarms.<br/>"
        "• <b>Auto-Detect Scenario Type:</b> Dynamically classifies scenarios as GROWTH_SURGE, ANOMALY_DROP, or STABLE from data patterns.<br/>"
        "• <b>Generalized DAG Propagation:</b> What-If simulator propagates through any parent-child edges, not just hardcoded e-commerce pairs.<br/>"
        "• <b>Memory-Safe File Upload:</b> Streamed to disk via shutil.copyfileobj — handles enterprise-scale datasets without OOM.<br/>"
        "• <b>Surge-Aware UI:</b> Green banners, scale-infrastructure buttons, and SURGE technical logs for positive growth scenarios.<br/>"
        "• <b>Robust Error Handling:</b> All 7 API fetch calls validate HTTP status before JSON parsing.",
        body_style
    ))

    # User Experience &amp; Personas
    story.append(Paragraph("4. Dual-Mode UX &amp; Persona-Aware Dashboard", h2_style))
    story.append(Paragraph(
        "• <b>Simple View vs Technical Diagnostics:</b> Toggle between plain-English executive summaries and deep statistical Z-score matrices.<br/>"
        "• <b>C-Suite Persona:</b> Financial impact (-$250K/day), strategic ROI, and 1-click executive actions.<br/>"
        "• <b>DevOps Persona:</b> Terminal-style logs, Z-scores, deployment triage, and hotfix rollback buttons.<br/>"
        "• <b>BI Analyst Persona:</b> Variance attribution %, p-values, cosine similarity scores, and hypothesis rejection logs.<br/>"
        "• <b>Interactive Node Inspector:</b> Click any metric node to filter evidence logs (with toggle-clear support).<br/>"
        "• <b>What-If Slider:</b> Real-time percentage delta display (+XX.X%) as you drag any metric.",
        body_style
    ))

    # Real-World Data Corpus
    story.append(Paragraph("5. Real-World Datasets Ingested (17,000+ Total Records)", h2_style))
    story.append(Paragraph(
        "• <b>metrics_timeseries.csv:</b> 9,125 rows across 5 global regions (APAC, EU, NA, LATAM, EMEA) over 365 days.<br/>"
        "• <b>jira_deployments.csv:</b> 20 live-crawled deployment logs from GitHub (Stripe, React, FastAPI, Next.js).<br/>"
        "• <b>zendesk_tickets.csv:</b> Customer support tickets with NLP sentiment scores (-0.92 to +0.45).<br/>"
        "• <b>slack_alerts.csv:</b> Datadog APM, PagerDuty, and Cloudflare war room monitoring alerts.<br/>"
        "• <b>Custom CSV Portal:</b> Upload any enterprise dataset — the ML pipeline auto-adapts in &lt;2 seconds.",
        body_style
    ))

    # How to Run Locally
    story.append(Paragraph("6. Local Quickstart &amp; Verification Suite", h2_style))
    code_text = (
        "# 1. Clone & install\n"
        "git clone https://github.com/abhishek9680/CortexKPI.git\n"
        "cd CortexKPI\n"
        "pip install -r requirements.txt\n\n"
        "# 2. Launch FastAPI Server\n"
        "python main.py  # Dashboard live at http://127.0.0.1:8000\n\n"
        "# 3. Run Verification Test Suite\n"
        "python test_production_api.py\n"
        "python test_custom_inputs.py"
    )
    story.append(Paragraph(code_text.replace("\n", "<br/>"), code_style))

    doc.build(story)
    print(f"[SUCCESS] README PDF generated at: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
