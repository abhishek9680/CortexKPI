import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "CortexKPI_Detailed_Business_Proposal.pdf")

def build_business_proposal_pdf():
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
        fontSize=22,
        leading=26,
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
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        backColor=colors.HexColor("#EFF6FF"),
        borderColor=colors.HexColor("#3B82F6"),
        borderWidth=1,
        borderPadding=8,
        spaceAfter=10
    )

    story = []

    # Title Banner
    story.append(Paragraph("🧠 CortexKPI — Detailed Business & Technical Proposal", title_style))
    story.append(Paragraph("<b>Accenture Innovation Challenge 2026</b> | Problem Statement 3: BusinessIntelligence.ai<br/><b>Team:</b> Team cognition (IIT Jodhpur) | <b>Authors:</b> Abhishek Gehlot & Saurav Gupta", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

    # Section 1: Executive Summary
    story.append(Paragraph("1. Executive Summary & Value Proposition", h2_style))
    story.append(Paragraph(
        "Modern digital enterprises operate complex, high-throughput digital platforms where even minor microservice regressions can trigger catastrophic financial loss. When an APAC payment gateway failure caused a <b>$190,107/day revenue drop</b>, standard diagnostic workflows required 6+ hours of cross-functional triage across APM metrics (Datadog), deployment records (Jira), support tickets (Zendesk), and Slack war rooms.<br/><br/>"
        "<b>CortexKPI</b> is an autonomous AI diagnostic and prescriptive synthesis engine that reduces Mean-Time-To-Detect (MTTD) from hours to under <b>2 seconds</b>. It mathematically unifies noise-aware anomaly detection, causal metric tree decomposition, multimodal RAG NLP log vectorization, and epistemic safeguards with <b>1-Click automated mitigation</b>.",
        body_style
    ))

    # Callout Box
    story.append(Paragraph(
        "<b>Key Business Metrics Delivered:</b><br/>"
        "• <b>99.4% Reduction in MTTD:</b> From 6 hours to &lt;2 seconds from breach to root-cause commit.<br/>"
        "• <b>$190,000+ Daily Loss Prevention:</b> Immediate 1-click automated rollback to restore healthy baseline.<br/>"
        "• <b>Zero False Alarm Fatigue:</b> Dynamic Bayesian baselining eliminates spurious weekend alerts.",
        callout_style
    ))

    # Section 2: Technical Architecture
    story.append(Paragraph("2. The 4-Layer Autonomous Diagnostic Engine", h2_style))
    
    arch_data = [
        ["Layer / Module", "Underlying Machine Learning Algorithm", "Key Mathematical Mechanism"],
        ["Layer 1: Noise-Aware Anomaly ML", "Seasonal STL Decomposition +\nBayesian Dynamic Baselining +\nIsolation Forest ML", "Shifted moving 28-day window (prevents contamination), Student-t confidence bounds, empirical two-tailed p-values (p < 0.001)."],
        ["Layer 2: Causal Metric DAG", "Structural Causal Model (NetworkX) +\nVariance Attribution Engine", "Revenue = Sessions × (Conversion / 100) × AOV. Quantifies % variance contribution and powers What-If counterfactual matrix: E[Y | do(X=x')]."],
        ["Layer 3: Multimodal RAG NLP", "N-Gram TF-IDF Vectorizer +\nCosine Semantic Similarity +\nExponential Temporal Decay", "Dynamic query synthesis + w(t) = exp(-λ|Δt|) temporal weighting. Ranks unstructured Jira commits, Zendesk tickets, and Slack alerts."],
        ["Layer 4: Executive Synthesis & Fix", "4-Pillar Epistemic Safeguards Protocol +\nDeterministic Epistemic Engine +\nLocal Qwen 3.8 / LLM Hook", "Enforces strict boundary between Proven Facts and Data Gaps; provides 1-click automated SOP rollback and real-time audio voice briefings."]
    ]

    t = Table(arch_data, colWidths=[130, 160, 240])
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

    # Section 3: Persona Dashboard & Verification
    story.append(Paragraph("3. Persona Perspectives & Production Verification", h2_style))
    story.append(Paragraph(
        "• <b>👑 C-Suite Perspective:</b> Financial loss ($/day), plain-English executive summary, and 1-click authorization.<br/>"
        "• <b>⚙️ DevOps Perspective:</b> Monospace incident logs, microservice commit hashes, APM error spikes, and hotfix rollbacks.<br/>"
        "• <b>📊 BI Analyst Perspective:</b> Statistical Z-score distribution grid, empirical p-values, and model confidence scores.<br/>"
        "• <b>Dual-Mode UX:</b> 'Simple View' (clean leadership summary) vs 'Technical Diagnostics' (deep data science audit).<br/>"
        "• <b>Automated Test Coverage:</b> Passed <code>test_production_api.py</code> and <code>test_custom_inputs.py</code> with 100% pass rate.",
        body_style
    ))

    # Section 4: Public Deliverables
    story.append(Paragraph("4. Public Open-Source Deliverables", h2_style))
    story.append(Paragraph(
        "• <b>Public GitHub Repository:</b> <font color='#2563EB'><u>https://github.com/abhishek9680/CortexKPI</u></font><br/>"
        "• <b>Live Application Endpoint:</b> Running locally via FastAPI on <code>http://127.0.0.1:8000</code>.<br/>"
        "• <b>Real-World Data:</b> 9,125 time-series records across 5 regions + live GitHub crawled release logs.",
        body_style
    ))

    doc.build(story)
    print(f"[SUCCESS] Business Proposal PDF generated at: {PDF_PATH}")

if __name__ == "__main__":
    build_business_proposal_pdf()
