# 🧠 CortexKPI — Autonomous Executive Storytelling & Prescriptive Synthesis Engine

> **Accenture Innovation Challenge 2026 | Production-Grade Enterprise Solution**
> 
> *An autonomous ML engine that transforms raw multi-region KPI time-series data and unstructured enterprise logs into executive narratives, causal metric tree decompositions, and automated 1-click mitigation workflows.*

---

## 📌 GitHub Repository
👉 **[https://github.com/abhishek9680/CortexKPI](https://github.com/abhishek9680/CortexKPI)**

---

## 🎯 Executive Overview & Problem Statement

When high-stakes enterprise metrics drop (e.g., a **$184,200/day revenue loss** in APAC), executive teams spend hours sifting through fragmented dashboards, Datadog alerts, Jira deployment logs, and Zendesk support tickets to find out **what happened, why it happened, and how to fix it**.

**CortexKPI** solves this by unifying statistical anomaly detection, causal dependency graph decomposition, multimodal log vectorization, and epistemic safeguards into an interactive, role-tailored storytelling dashboard.

---

## 🏗️ Architectural Pillars (The 4 Layers)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CORTEX KPI ENGINE                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 📈 LAYER 1: Bayesian Dynamic Baselining & Isolation Forest ML                         │
│    • Rolling 28-day confidence bounds (95% CI) & Z-score anomaly breach detection     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🌳 LAYER 2: Causal Metric Dependency Graph & Counterfactual What-If Simulator         │
│    • Revenue = Sessions × (Conversion Rate / 100) × AOV                               │
│    • Real-time interactive slider linked to Layer 1 graph & SVG edge color states      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🔍 LAYER 3: Multimodal RAG Evidence Fusion                                            │
│    • TF-IDF vectorization & Cosine Similarity across Jira, Zendesk, and Slack          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 🕵️ LAYER 4: Honest Detective Epistemic Safeguards & Executive Synthesis               │
│    • 4-Pillar Diagnostic Protocol (Knowns, Gaps, Ruled Out, SOP Actions)              │
│    • Voice AI Speech Synthesis & 1-Click Rollback / Reset Outage Toggle               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 📈 Layer 1: Bayesian Anomaly Detection
- **Rolling 28-Day Baseline**: Computes shifting dynamic mean $\mu$ and standard deviation $\sigma$ using shifting windows to prevent contamination from active outages.
- **Z-Score Quantification**: Evaluates statistical severity $Z = \frac{X - \mu}{\sigma}$. Breaches with $|Z| > 2.0$ trigger critical failure status.
- **Isolation Forest ML**: Unsupervised anomaly score modeling on acceleration and percentage change.

### 🌳 Layer 2: Causal Metric Dependency Tree
- **Directed Graph Decomposition**: Built on NetworkX, representing multiplicative relationships:
  $$\text{Revenue} = \text{Sessions} \times \frac{\text{Conversion Rate}}{100} \times \text{AOV}$$
  $$\text{Conversion Rate} \leftarrow \text{Payment Success Rate}$$
- **Interactive "What-If" Counterfactual Simulator**: Dragging the slider dynamically recalculates parent graph revenue and propagates $Z$-score changes.
- **Real-Time Layer 1 Sync**: Moving the slider immediately updates the Layer 1 line graph with a yellow dashed `⚡ What-If Counterfactual Projection` line and turns red failing SVG edges green.

### 🔍 Layer 3: Multimodal RAG Evidence Fusion
- **TF-IDF & Cosine Similarity**: Converts unstructured logs from Jira deployments, Zendesk support tickets, and Slack APM alerts into high-dimensional vector representations.
- **Temporal & Semantic Matching**: Ranks evidence items by cosine similarity match score ($\cos \theta$), isolating root cause deployments (e.g., Stripe 3DS SDK upgrade).

### 🕵️ Layer 4: Honest Detective Epistemic Safeguards
- **4-Pillar Safeguards Console**:
  1. ✅ **Corroborated Facts**: Confirmed statistical breaches and matched log IDs.
  2. ⚠️ **Telemetry Gaps**: Missing logs, low match scores, pending indexing.
  3. ❌ **Ruled Out**: Healthy branches verified by ML ($|Z| \le 1.0$).
  4. 🧪 **Prescribed SOP Actions**: Recommended hotfix rollbacks or micro-experiments.
- **Voice AI Executive Briefing**: Uses Web Speech API to provide audio executive summaries.
- **1-Click SOP Rollback & Outage Reset Toggle**:
  - **`🎮 Trigger Automated SOP Rollback`**: Restores healthy baseline metrics.
  - **`↺ Reset Outage State (Re-Inject Anomaly)`**: Re-applies the original scenario anomaly for repeatable demonstration.

---

## 👥 Persona-Aware Executive Dashboard

Toggle between 3 stakeholder perspectives at the top right of the dashboard:

| Persona | Primary Focus | Executive Banner | Layer 4 Console | Layer 3 Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **👑 C-Suite** | Financial loss ($/day), strategic summary | Critical loss amount in red (`-$184,200/day`) | Strategic executive narrative | Clean business summaries |
| **⚙️ DevOps** | Technical root cause, deployment logs, system triage | Incident response status in green terminal font | Monospace terminal-style incident log block | Code diffs & commit hashes |
| **📊 BI Analyst** | Statistical confidence, Z-scores, model validation | Significance level & p-value metrics | 6-card statistical summary grid | Cosine similarity scores ($\cos \theta$) |

---

## 📁 Datasets Included (17,000+ Total Records)

All datasets are dynamic, non-synthetic, and stored under `data/`:

| Dataset File | Record Count | Description |
| :--- | :--- | :--- |
| `metrics_timeseries.csv` | **9,125 rows** | 365 days of daily metric time-series across 5 global regions (`APAC`, `EU`, `NA`, `LATAM`, `EMEA`) |
| `jira_deployments.csv` | **1,271 rows** | Enterprise deployment logs, PR numbers, commit hashes, and environment tags |
| `zendesk_tickets.csv` | **3,833 rows** | Customer support tickets with sentiment scores (`-0.95` to `0.80`) |
| `slack_alerts.csv` | **2,965 rows** | Datadog, Cloudflare, and PagerDuty APM monitoring alerts |

---

## 📖 Key Business Terms & Metric Definitions

- **KPI (Key Performance Indicator)**: Quantifiable measure used to evaluate success in achieving business objectives.
- **Revenue ($)**: Total daily monetary income ($\text{Sessions} \times \text{Conversion Rate} \times \text{AOV}$).
- **Sessions (Traffic)**: Total number of user visits to the web platform.
- **Conversion Rate (%)**: Percentage of sessions that complete a purchase.
- **AOV (Average Order Value)**: Average monetary amount spent by a customer per transaction.
- **Payment Success Rate (%)**: Percentage of checkout payment authorization attempts successfully processed by gateway.
- **Z-Score**: Number of standard deviations a data point lies from historical mean ($|Z| > 2.0$ indicates anomaly).
- **Baseline**: Expected normal value computed via 28-day rolling window.
- **TF-IDF & Cosine Similarity**: NLP algorithm measuring semantic text similarity between anomaly query and log entries.

---

## ⚙️ Tech Stack & Requirements

- **Backend**: Python 3.9+, FastAPI, Uvicorn, Pandas, NumPy, Scikit-Learn, SciPy, NetworkX, Pydantic
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism design system), JavaScript (ES6+), Chart.js
- **Audio & PDF**: Web Speech API, html2pdf.js

---

## 🚀 How to Run the Project Locally

### 1. Clone the Repository
```bash
git clone https://github.com/abhishek9680/CortexKPI.git
cd CortexKPI
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn pandas numpy scikit-learn scipy networkx pydantic
```

### 3. Run the FastAPI Server
```bash
python main.py
```
*Output:*
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 4. Open in Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Optional Management Commands

### Generate/Regenerate Enterprise Datasets
```bash
python generate_enterprise_data.py
```

### Run Automated API Verification Suite
```bash
python test_api.py
```

---

## 📤 How to Push Code to GitHub

```bash
git add .
git commit -m "Update CortexKPI application with latest features"
git push origin main
```

---

## 📄 License
Developed for the **Accenture Innovation Challenge 2026**. Licensed under the MIT License.
