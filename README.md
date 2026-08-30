# 🧠 CortexKPI — Autonomous Executive Storytelling & Prescriptive Synthesis Engine

> **Accenture Innovation Challenge 2026 | Problem Statement 3: BusinessIntelligence.ai**
> 
> *An autonomous AI/ML engine that transforms raw multi-region KPI time-series data and unstructured enterprise logs into executive narratives, causal metric tree decompositions, and automated 1-click mitigation workflows.*

---

## 📌 Team & Repository Information
- **Team**: Team cognition (IIT Jodhpur)
- **Collaborators**: [Abhishek Gehlot (@abhishek9680)](https://github.com/abhishek9680) & [Saurav Gupta (@Saurav-Gupta-9741)](https://github.com/Saurav-Gupta-9741)
- **GitHub Repository**: 👉 **[https://github.com/abhishek9680/CortexKPI](https://github.com/abhishek9680/CortexKPI)**

---

## 🎯 Executive Overview & Problem Statement

When high-stakes enterprise metrics drop (e.g., a **$190,000/day revenue loss** in APAC), executive teams spend hours sifting through fragmented dashboards, Datadog alerts, Jira deployment logs, and Zendesk support tickets to find out **what happened, why it happened, and how to fix it**.

**CortexKPI** solves this by unifying statistical anomaly detection, causal dependency graph decomposition, multimodal log vectorization, and epistemic safeguards into an interactive, role-tailored storytelling dashboard.

---

## 🏗️ 4-Step Guided Investigation Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CORTEX KPI ENGINE                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📈 STEP 1: Metric Timeline & Noise-Aware Anomaly Detection                             │
│    • Seasonal STL Decomposition + Bayesian Dynamic Baselining (Student-t bounds)       │
│    • Unsupervised Isolation Forest ML & empirical p-values (p < 0.001)                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🌳 STEP 2: Causal Root Cause Dependency Chain & What-If Simulator                      │
│    • Revenue = Sessions × (Conversion Rate / 100) × AOV                               │
│    • Real-time interactive counterfactual slider linked to Layer 1 projection graph    │
│    • Interactive Node Inspector (Click any node to filter related logs)                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🔍 STEP 3: Multimodal RAG Evidence Fusion & Temporal Decay                             │
│    • N-Gram TF-IDF Vectorizer & Cosine Similarity across Jira, Zendesk, and Slack      │
│    • Exponential Temporal Decay Weighting: w = exp(-λ · |Δt|)                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🕵️ STEP 4: Executive Verdict, Epistemic Safeguards & 1-Click Fix                       │
│    • 4-Pillar Diagnostic Protocol (Known Facts, Telemetry Gaps, Ruled Out, SOP Actions)│
│    • Dual-Engine Synthesis (Deterministic Epistemic Engine + Live Local Qwen 3.8 / LLM)│
│    • 🎮 1-Click Automated SOP Rollback & Outage Reset Toggle                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Dual-Mode & Persona-Aware Executive Dashboard

### 1. Mode Switcher (Simple View vs Technical Diagnostics)
- **🟢 Simple View (Default)**: Plain-English executive summaries, big readable numbers, and 1-click action buttons designed for non-technical leadership.
- **🔬 Technical Diagnostics**: Unlocks full $Z$-score statistical distribution matrices, Isolation Forest decision scores, empirical $p$-values, and raw terminal log streams.

### 2. Persona Perspectives
Toggle between 3 stakeholder perspectives at the top right of the dashboard:

| Persona | Primary Focus | Executive Banner | Step 4 Console | Step 3 Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **👑 C-Suite** | Financial loss ($/day), strategic summary | Critical loss amount in red (`-$190,107/day`) | Strategic executive narrative | Clean business summaries |
| **⚙️ DevOps** | Technical root cause, deployment logs, system triage | Incident response status in green terminal font | Monospace terminal-style incident log block | Code diffs & commit hashes |
| **📊 BI Analyst** | Statistical confidence, Z-scores, model validation | Significance level & p-value metrics | 6-card statistical summary grid | Cosine similarity scores ($\cos \theta$) |

---

## 📁 Datasets Included (Real-World Crawled Data)

All datasets are non-synthetic, multi-region, and stored under `data/`:

| Dataset File | Record Count | Description |
| :--- | :--- | :--- |
| `metrics_timeseries.csv` | **9,125 rows** | 365 days of daily metric time-series across 5 global regions (`APAC`, `EU`, `NORTH_AMERICA`, `LATAM`, `EMEA`) |
| `jira_deployments.csv` | **Real Records** | Crawled live via GitHub REST API across Stripe, React, and FastAPI repositories |
| `zendesk_tickets.csv` | **Real Records** | Customer support tickets with sentiment scores (`-0.92` to `+0.45`) |
| `slack_alerts.csv` | **Real Records** | Datadog, Cloudflare, and PagerDuty APM monitoring alerts |

---

## ⚙️ Tech Stack & Requirements

- **Backend**: Python 3.9+, FastAPI, Uvicorn, Pandas, NumPy, Scikit-Learn, SciPy, NetworkX, Pydantic
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism design system), JavaScript (ES6+), Chart.js
- **Audio & PDF**: Web Speech API, html2pdf.js
- **AI / LLM**: Optional Local Qwen 3.8 / Ollama / OpenAI-compatible endpoint integration

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/abhishek9680/CortexKPI.git
cd CortexKPI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI Server
```bash
python main.py
```

### 4. Open in Browser
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

---

## 🧪 Automated Verification & Testing

Run the automated test suites to verify that all mathematical ML pipelines, What-If simulations, and API endpoints are 100% operational:

```bash
# 1. Run Production Pipeline Verification
python test_production_api.py

# 2. Run Custom Input & Edge-Case Validation Suite
python test_custom_inputs.py
```

---

## 📄 License
Developed for the **Accenture Innovation Challenge 2026**. Licensed under the MIT License.
