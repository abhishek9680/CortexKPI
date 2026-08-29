import os
import math
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from models.anomaly_detection import AnomalyDetectorML
from models.causal_tree import CausalMetricTreeML
from models.nlp_vectorizer import MultimodalLogRAGML
from models.narrative_generator import HonestDetectiveNarrativeML

app = FastAPI(title="CortexKPI Engine API", version="2.6.0")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Instantiate ML Models
anomaly_detector = AnomalyDetectorML(window_size=28)
causal_tree_decomposer = CausalMetricTreeML()
log_rag_vectorizer = MultimodalLogRAGML()
narrative_engine = HonestDetectiveNarrativeML()

def safe_float(val, default=0.0):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except Exception:
        return default

# Load Datasets dynamically
def load_datasets():
    metrics_path = os.path.join(DATA_DIR, "metrics_timeseries.csv")
    jira_path = os.path.join(DATA_DIR, "jira_deployments.csv")
    zendesk_path = os.path.join(DATA_DIR, "zendesk_tickets.csv")
    slack_path = os.path.join(DATA_DIR, "slack_alerts.csv")

    if not os.path.exists(metrics_path):
        raise RuntimeError("Datasets missing! Run 'python crawl_and_collect_data.py' first.")

    df_metrics = pd.read_csv(metrics_path)
    df_jira = pd.read_csv(jira_path)
    df_zendesk = pd.read_csv(zendesk_path)
    df_slack = pd.read_csv(slack_path)

    return df_metrics, df_jira, df_zendesk, df_slack

class AnalyzeRequest(BaseModel):
    scenario_id: str = "SCENARIO_1"
    kpi_name: str = "Revenue"

class WhatIfRequest(BaseModel):
    scenario_id: str = "SCENARIO_1"
    node_adjusted: str = "Payment_Success_Rate"
    new_value: float = 85.0

class MitigationRequest(BaseModel):
    scenario_id: str = "SCENARIO_1"
    action_type: str = "ROLLBACK_DEPLOYMENT"

@app.get("/api/scenarios")
def get_scenarios():
    df_metrics, _, _, _ = load_datasets()
    unique_scenarios = [s for s in df_metrics['scenario_id'].unique().tolist() if str(s) != "SCENARIO_NORMAL" and pd.notna(s)]
    
    scenarios_result = []
    for sid in unique_scenarios:
        df_s = df_metrics[df_metrics['scenario_id'] == sid]
        reg_series = df_s['region'].dropna()
        reg = str(reg_series.iloc[0]) if not reg_series.empty else "GLOBAL"
        if reg.lower() == "nan":
            reg = "GLOBAL"
        
        rev_rows = df_s[df_s['kpi_name'] == 'Revenue'].sort_values('timestamp')
        if not rev_rows.empty:
            proc = anomaly_detector.analyze_timeseries(rev_rows)
            min_z = safe_float(proc['z_score'].min(), 0.0)
            
            if min_z <= -2.0:
                type_tag = "CRITICAL_FAILURE"
                icon = "🔴"
            elif min_z <= -1.0:
                type_tag = "AMBIGUOUS_WARNING"
                icon = "🟡"
            else:
                type_tag = "HEALTHY_RESOLVED"
                icon = "🟢"
        else:
            type_tag = "ANOMALY"
            icon = "📊"

        scenarios_result.append({
            "id": str(sid),
            "name": f"{icon} {sid} ({reg} Region Analysis)",
            "kpi": "Revenue",
            "region": reg,
            "type": type_tag
        })

    return {"scenarios": scenarios_result}

@app.post("/api/analyze")
def analyze_scenario(req: AnalyzeRequest):
    df_metrics, df_jira, df_zendesk, df_slack = load_datasets()

    df_scen = df_metrics[df_metrics['scenario_id'] == req.scenario_id]
    if df_scen.empty:
        df_scen = df_metrics[df_metrics['scenario_id'] == 'SCENARIO_1']

    df_kpi = df_scen[df_scen['kpi_name'] == req.kpi_name].sort_values('timestamp')
    if df_kpi.empty:
        df_kpi = df_metrics[df_metrics['kpi_name'] == req.kpi_name].sort_values('timestamp')

    # LAYER 1: Bayesian Dynamic Baselining ML
    df_processed = anomaly_detector.analyze_timeseries(df_kpi)

    timeseries_data = []
    for idx, row in df_processed.iterrows():
        timeseries_data.append({
            "timestamp": str(row['timestamp']),
            "value": safe_float(row['value']),
            "rolling_mean": safe_float(row['rolling_mean']),
            "lower_bound": safe_float(row['lower_bound']),
            "upper_bound": safe_float(row['upper_bound']),
            "z_score": safe_float(row['z_score']),
            "status": str(row['status'])
        })

    peak_row = df_processed.loc[df_processed['z_score'].abs().idxmax()] if not df_processed.empty else df_processed.iloc[-1]
    peak_date = str(peak_row['timestamp'])

    available_kpis = df_scen['kpi_name'].unique().tolist()
    metric_snapshot = {}

    for kpi in available_kpis:
        kpi_rows = df_scen[df_scen['kpi_name'] == kpi].sort_values('timestamp')
        if not kpi_rows.empty:
            kpi_proc = anomaly_detector.analyze_timeseries(kpi_rows)
            match_row = kpi_proc[kpi_proc['timestamp'] == peak_date]
            if not match_row.empty:
                r = match_row.iloc[0]
                metric_snapshot[kpi] = {
                    "value": safe_float(r['value']),
                    "baseline": safe_float(r['rolling_mean']),
                    "z_score": safe_float(r['z_score'])
                }
            else:
                last_r = kpi_proc.iloc[-1]
                metric_snapshot[kpi] = {
                    "value": safe_float(last_r['value']),
                    "baseline": safe_float(last_r['rolling_mean']),
                    "z_score": safe_float(last_r['z_score'])
                }

    # LAYER 2: Causal Metric Tree Decomposition ML
    causal_results = causal_tree_decomposer.decompose_anomaly(metric_snapshot)

    # LAYER 3: Multimodal RAG Log Vectorization ML
    reg_s = df_scen['region'].dropna()
    anomaly_context = {
        "kpi": causal_results.get("root_cause_leaf", "Conversion_Rate"),
        "region": str(reg_s.iloc[0]) if not reg_s.empty else "GLOBAL",
        "timestamp": peak_date
    }
    evidence_items = log_rag_vectorizer.search_corroborating_evidence(anomaly_context, df_jira, df_zendesk, df_slack)

    # LAYER 4: Honest Detective Safeguards & Narrative Synthesis
    narrative_results = narrative_engine.synthesize_narrative(req.scenario_id, {"timestamp": peak_date}, causal_results, evidence_items)

    return {
        "scenario_id": req.scenario_id,
        "peak_date": peak_date,
        "layer_1_timeseries": timeseries_data,
        "layer_2_causal_tree": causal_results,
        "layer_3_evidence": evidence_items,
        "layer_4_narrative": narrative_results
    }

@app.post("/api/simulate_whatif")
def simulate_whatif(req: WhatIfRequest):
    df_metrics, _, _, _ = load_datasets()
    df_scen = df_metrics[df_metrics['scenario_id'] == req.scenario_id]

    available_kpis = df_scen['kpi_name'].unique().tolist()
    metric_snapshot = {}
    for kpi in available_kpis:
        kpi_rows = df_scen[df_scen['kpi_name'] == kpi].sort_values('timestamp')
        if not kpi_rows.empty:
            kpi_proc = anomaly_detector.analyze_timeseries(kpi_rows)
            last_r = kpi_proc.iloc[-1]
            metric_snapshot[kpi] = {
                "value": safe_float(last_r['value']),
                "baseline": safe_float(last_r['rolling_mean']),
                "z_score": safe_float(last_r['z_score'])
            }

    updated_causal_tree = causal_tree_decomposer.simulate_whatif(metric_snapshot, req.node_adjusted, req.new_value)
    
    rev_val = safe_float(updated_causal_tree["tree"]["Revenue"]["value"], 420000.0)
    rev_base = safe_float(updated_causal_tree["tree"]["Revenue"]["baseline"], 420000.0)
    diff = rev_val - rev_base

    return {
        "node_adjusted": req.node_adjusted,
        "new_value": safe_float(req.new_value, 90.0),
        "updated_causal_tree": updated_causal_tree,
        "projected_revenue": rev_val,
        "projected_diff": round(diff, 2),
        "impact_summary": f"Projected Revenue: ${rev_val:,.2f} ({'+' if diff>=0 else ''}${diff:,.2f} vs baseline)"
    }

@app.post("/api/execute_mitigation")
def execute_mitigation(req: MitigationRequest):
    metrics_path = os.path.join(DATA_DIR, "metrics_timeseries.csv")
    df_metrics = pd.read_csv(metrics_path)
    
    is_rollback = req.action_type != "REINJECT_ANOMALY"

    if req.scenario_id == "SCENARIO_2":
        mask_cvr = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Conversion_Rate')
        df_metrics.loc[mask_cvr, 'value'] = 2.85 if is_rollback else 1.65

        mask_rev = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Revenue')
        df_metrics.loc[mask_rev, 'value'] = 631800.0 if is_rollback else 364320.0

        mask_pay = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Payment_Success_Rate')
        df_metrics.loc[mask_pay, 'value'] = 98.2 if is_rollback else 98.1

    elif req.scenario_id == "SCENARIO_3":
        mask_sess = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Sessions')
        df_metrics.loc[mask_sess, 'value'] = 120000.0 if is_rollback else 177600.0

        mask_cvr = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Conversion_Rate')
        df_metrics.loc[mask_cvr, 'value'] = 2.85 if is_rollback else 3.45

        mask_aov = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'AOV')
        df_metrics.loc[mask_aov, 'value'] = 185.0 if is_rollback else 195.0

        mask_rev = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Revenue')
        df_metrics.loc[mask_rev, 'value'] = 631800.0 if is_rollback else 1194762.0

    else:
        # Default / SCENARIO_1: Payment Success Rate Anomaly
        mask_pay = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Payment_Success_Rate')
        df_metrics.loc[mask_pay, 'value'] = 98.2 if is_rollback else 54.2

        mask_cvr = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Conversion_Rate')
        df_metrics.loc[mask_cvr, 'value'] = 2.85 if is_rollback else 1.12

        mask_rev = (df_metrics['scenario_id'] == req.scenario_id) & (df_metrics['kpi_name'] == 'Revenue')
        df_metrics.loc[mask_rev, 'value'] = 631800.0 if is_rollback else 244608.0

    df_metrics.to_csv(metrics_path, index=False)

    if is_rollback:
        action_msg = "Automated Deployment Rollback Executed (Restored healthy baseline metrics)."
        status_msg = "Payment authorization and conversion rates restored to baseline. System Healthy."
    else:
        action_msg = "Scenario Anomaly Re-injected (Reset outage state for demonstration)."
        status_msg = "Original incident anomaly re-applied. System returned to critical outage state."

    return {
        "status": "SUCCESS",
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type": req.action_type,
        "mitigation_event": {
            "ticket_created": f"INC-{pd.Timestamp.now().strftime('%Y')}-8890",
            "action_taken": action_msg,
            "slack_notified": f"Posted update to #war-room ({'Resolution' if is_rollback else 'Outage Simulation'})",
            "projected_recovery": status_msg
        }
    }

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CortexKPI Engine API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
