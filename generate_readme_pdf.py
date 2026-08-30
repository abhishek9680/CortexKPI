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
    story.append(Paragraph("1. Executive Overview & Problem Statement", h2_style))
    story.append(Paragraph(
        "When high-stakes enterprise metrics drop (e.g. an unexpected <b>$190,000/day revenue loss</b> in APAC), executive leadership and engineering teams spend 6+ hours sifting through fragmented Datadog APM charts, Jira pull requests, Zendesk support tickets, and Slack alerts trying to answer: <i>What happened, why it happened, and how to fix it?</i><br/><br/>"
        "<b>CortexKPI</b> is an autonomous AI diagnostic engine that unifies seasonal Bayesian anomaly detection, causal dependency graph decomposition, multimodal RAG log vectorization, and epistemic safeguards into an interactive executive dashboard with <b>1-Click automated mitigation</b>.",
        body_style
    ))

    # The 4 ML Layers
    story.append(Paragraph("2. Architectural Pillars (The 4 ML Layers)", h2_style))
    
    layer_data = [
        ["Layer / Module", "Underlying ML Algorithm", "Core Purpose & Enterprise Value"],
        ["📈 Step 1: Metric Timeline & Anomaly Detection", "Seasonal STL Decomposition +\nBayesian Baselining (Student-t) +\nIsolation Forest Unsupervised ML", "Eliminates false alarms from normal weekend dips; calculates dynamic 95% confidence bands & empirical p-values (p < 0.001)."],
        ["🌳 Step 2: Causal Metric Dependency Chain", "Structural Causal DAG (NetworkX) +\nMathematical Variance Attribution +\nCounterfactual Intervention Matrix", "Decomposes Revenue into Sessions × Conversion × AOV. Isolates root cause failing leaf node and powers What-If recovery simulations."],
        ["🔍 Step 3: Multimodal RAG Evidence Fusion", "TF-IDF N-Gram Vectorizer +\nCosine Similarity +\nExponential Temporal Decay", "Scans unstructured Jira deployments, Zendesk support tickets, and Slack alerts. Weights logs closest to the incident window."],
        ["🕵️ Step 4: Executive Verdict & 1-Click Fix", "4-Pillar Epistemic Safeguards +\nDual-Engine Synthesis +\nLocal Qwen 3.8 / LLM AI Hook", "Generates concise 3-bullet executive briefings; categorizes facts vs gaps; provides 1-click automated rollback to restore healthy baseline."]
    ]

    t = Table(layer_data, colWidths=[150, 160, 220])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # User Experience & Personas
    story.append(Paragraph("3. Dual-Mode UX & Persona-Aware Dashboard", h2_style))
    story.append(Paragraph(
        "• <b>Simple View vs Technical Diagnostics:</b> Toggle between plain-English executive summaries for leadership and deep statistical Z-score/distribution matrices for data scientists.<br/>"
        "• <b>👑 C-Suite Persona:</b> Emphasizes daily financial impact (-$190,107/day) and strategic ROI.<br/>"
        "• <b>⚙️ DevOps Persona:</b> Displays microservice commit hashes, pull requests, APM logs, and 1-click rollback buttons.<br/>"
        "• <b>📊 BI Analyst Persona:</b> Displays variance attribution %, p-values, and cosine similarity match scores.<br/>"
        "• <b>Interactive Node Inspector:</b> Clicking any metric in the causal tree immediately filters all system logs to that specific sub-system.",
        body_style
    ))

    # Real-World Data Corpus
    story.append(Paragraph("4. Real-World Datasets Ingested (17,000+ Total Records)", h2_style))
    story.append(Paragraph(
        "• <b>metrics_timeseries.csv:</b> 9,125 rows across 5 global regions (APAC, EU, NORTH_AMERICA, LATAM, EMEA) over 365 days.<br/>"
        "• <b>jira_deployments.csv:</b> Live-crawled deployment logs across major cloud repositories (Stripe, React, FastAPI, Next.js).<br/>"
        "• <b>zendesk_tickets.csv:</b> Customer care complaints with sentiment scores (-0.92 to +0.45).<br/>"
        "• <b>slack_alerts.csv:</b> Datadog APM, PagerDuty, and Cloudflare DNS war room monitoring alerts.<br/>"
        "• <b>📁 Custom CSV Portal:</b> Ingest any custom enterprise dataset dynamically via the top-header portal in &lt;2 seconds.",
        body_style
    ))

    # How to Run Locally
    story.append(Paragraph("5. Local Quickstart & Verification Suite", h2_style))
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
