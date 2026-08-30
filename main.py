import os
import math
import random
import shutil
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from models.anomaly_detection import AnomalyDetectorML
from models.causal_tree import CausalMetricTreeML
from models.nlp_vectorizer import MultimodalLogRAGML
from models.narrative_generator import HonestDetectiveNarrativeML

app = FastAPI(title="CortexKPI Production Engine API", version="3.0.0")

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
        raise RuntimeError("Datasets missing! Please upload a dataset or generate initial data.")

    df_metrics = pd.read_csv(metrics_path, keep_default_na=False)
    df_jira = pd.read_csv(jira_path, keep_default_na=False) if os.path.exists(jira_path) else pd.DataFrame()
    df_zendesk = pd.read_csv(zendesk_path, keep_default_na=False) if os.path.exists(zendesk_path) else pd.DataFrame()
    df_slack = pd.read_csv(slack_path, keep_default_na=False) if os.path.exists(slack_path) else pd.DataFrame()

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

class LLMNarrativeRequest(BaseModel):
    scenario_id: str = "SCENARIO_1"
    prompt: Optional[str] = None
    api_base: Optional[str] = "http://127.0.0.1:8080/v1"
    api_key: Optional[str] = "none"
    model: Optional[str] = "qwen3-8b"

@app.get("/api/scenarios")
def get_scenarios():
    df_metrics, _, _, _ = load_datasets()
    all_scenarios = [s for s in df_metrics['scenario_id'].unique().tolist() if pd.notna(s)]
    unique_scenarios = [s for s in all_scenarios if str(s) != "SCENARIO_NORMAL"]
    if not unique_scenarios:
        unique_scenarios = all_scenarios[:3]
    
    # Hardcoded display names for known demo scenarios; custom uploads get auto-generated names
    scenario_titles = {
        "SCENARIO_1": "🔴 Scenario 1: APAC Payment Gateway Outage",
        "SCENARIO_2": "🟡 Scenario 2: EU Conversion Degradation",
        "SCENARIO_3": "🟢 Scenario 3: NA Marketing Surge"
    }

    scenarios_result = []
    for sid in unique_scenarios:
        df_s = df_metrics[df_metrics['scenario_id'] == sid]
        reg_series = df_s['region'].dropna() if 'region' in df_s.columns else pd.Series()
        reg = str(reg_series.iloc[0]) if not reg_series.empty and len(reg_series) > 0 else "GLOBAL"
        if reg.lower() == "nan" or not reg:
            reg = "GLOBAL"
        
        # Auto-detect scenario type from data: check if primary KPI is surging or dropping
        primary_kpi = 'Revenue' if 'Revenue' in df_s['kpi_name'].values else df_s['kpi_name'].iloc[0] if not df_s.empty else 'Revenue'
        kpi_vals = df_s[df_s['kpi_name'] == primary_kpi]['value'].astype(float)
        if len(kpi_vals) >= 10:
            recent_mean = kpi_vals.tail(5).mean()
            baseline_mean = kpi_vals.head(len(kpi_vals) - 5).mean()
            delta_pct = ((recent_mean - baseline_mean) / (abs(baseline_mean) + 1e-5)) * 100
            scenario_type = "GROWTH_SURGE" if delta_pct > 10 else ("ANOMALY_DROP" if delta_pct < -10 else "STABLE")
        else:
            scenario_type = "ANOMALY_DROP"
            delta_pct = 0
        
        # Generate dynamic display name for unknown scenarios
        if sid in scenario_titles:
            display_name = scenario_titles[sid]
        else:
            type_emoji = "🟢" if scenario_type == "GROWTH_SURGE" else "🔴" if scenario_type == "ANOMALY_DROP" else "🟡"
            type_label = "Growth Surge" if scenario_type == "GROWTH_SURGE" else "Anomaly" if scenario_type == "ANOMALY_DROP" else "Monitoring"
            display_name = f"{type_emoji} {sid}: {reg} {type_label} ({delta_pct:+.0f}%)"

        scenarios_result.append({
            "id": str(sid),
            "name": display_name,
            "kpi": primary_kpi,
            "region": reg,
            "type": scenario_type
        })

    return {"scenarios": scenarios_result}

@app.post("/api/analyze")
def analyze_scenario(req: AnalyzeRequest):
    df_metrics, df_jira, df_zendesk, df_slack = load_datasets()

    df_scen = df_metrics[df_metrics['scenario_id'] == req.scenario_id]
    if df_scen.empty:
        df_scen = df_metrics[df_metrics['scenario_id'] == 'SCENARIO_1']
        if df_scen.empty:
            df_scen = df_metrics

    reg_series = df_scen['region'].dropna() if 'region' in df_scen.columns else pd.Series()
    reg = str(reg_series.iloc[0]) if not reg_series.empty else "GLOBAL"
    if reg.lower() == "nan" or not reg:
        reg = "APAC"

    df_reg = df_metrics[df_metrics['region'] == reg].sort_values('timestamp')
    if df_reg.empty:
        df_reg = df_metrics.sort_values('timestamp')

    df_kpi = df_reg[df_reg['kpi_name'] == req.kpi_name].sort_values('timestamp')
    if df_kpi.empty:
        df_kpi = df_metrics[df_metrics['kpi_name'] == req.kpi_name].sort_values('timestamp')
    if df_kpi.empty:
        available_kpi_names = df_metrics['kpi_name'].unique().tolist()
        if available_kpi_names:
            df_kpi = df_metrics[df_metrics['kpi_name'] == available_kpi_names[0]].sort_values('timestamp')

    # LAYER 1: Dynamic Seasonal Bayesian Baselining & ML
    df_processed = anomaly_detector.analyze_timeseries(df_kpi)

    scen_proc = df_processed[df_processed['scenario_id'] == req.scenario_id] if 'scenario_id' in df_processed.columns else df_processed
    eval_proc = scen_proc if not scen_proc.empty else df_processed

    timeseries_data = []
    for idx, row in eval_proc.iterrows():
        timeseries_data.append({
            "timestamp": str(row['timestamp']),
            "value": safe_float(row['value']),
            "rolling_mean": safe_float(row['rolling_mean']),
            "lower_bound": safe_float(row['lower_bound']),
            "upper_bound": safe_float(row['upper_bound']),
            "z_score": safe_float(row['z_score']),
            "p_value": safe_float(row.get('p_value', 0.05)),
            "status": str(row['status'])
        })

    # Pick the most statistically significant anomaly breach point inside scenario window
    peak_row = eval_proc.loc[eval_proc['z_score'].abs().idxmax()] if not eval_proc.empty else df_processed.iloc[-1]
    peak_date = str(peak_row['timestamp'])

    available_kpis = df_metrics['kpi_name'].unique().tolist()
    metric_snapshot = {}

    for kpi in available_kpis:
        kpi_rows = df_reg[df_reg['kpi_name'] == kpi].sort_values('timestamp')
        if not kpi_rows.empty:
            kpi_proc = anomaly_detector.analyze_timeseries(kpi_rows)
            match_row = kpi_proc[kpi_proc['timestamp'] == peak_date]
            if not match_row.empty:
                r = match_row.iloc[0]
                metric_snapshot[kpi] = {
                    "value": safe_float(r['value']),
                    "baseline": safe_float(r['rolling_mean']),
                    "z_score": safe_float(r['z_score']),
                    "p_value": safe_float(r.get('p_value', 0.05))
                }
            else:
                last_r = kpi_proc.iloc[-1]
                metric_snapshot[kpi] = {
                    "value": safe_float(last_r['value']),
                    "baseline": safe_float(last_r['rolling_mean']),
                    "z_score": safe_float(last_r['z_score']),
                    "p_value": safe_float(last_r.get('p_value', 0.05))
                }

    # LAYER 2: Generalized Causal Metric Tree Decomposition ML
    causal_results = causal_tree_decomposer.decompose_anomaly(metric_snapshot)

    # LAYER 3: Dynamic Multimodal Temporal RAG Log Vectorization
    anomaly_context = {
        "kpi": causal_results.get("root_cause_leaf", "Conversion_Rate"),
        "region": reg,
        "timestamp": peak_date,
        "z_score": safe_float(peak_row.get('z_score', -2.0)),
        "p_value": safe_float(peak_row.get('p_value', 0.01))
    }
    evidence_items = log_rag_vectorizer.search_corroborating_evidence(anomaly_context, df_jira, df_zendesk, df_slack)
    for item in evidence_items:
        if "color" not in item:
            item["color"] = "#ff4444"
        if "badge" not in item:
            item["badge"] = "Alert"

    # LAYER 4: Epistemic Safeguards & Executive Synthesis
    narrative_results = narrative_engine.synthesize_narrative(req.scenario_id, {"timestamp": peak_date, "p_value": safe_float(peak_row.get('p_value', 0.01))}, causal_results, evidence_items)

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
    if df_scen.empty:
        df_scen = df_metrics

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
    
    root_node_name = "Revenue" if "Revenue" in updated_causal_tree["tree"] else list(updated_causal_tree["tree"].keys())[0]
    root_tree_data = updated_causal_tree["tree"][root_node_name]
    fallback_val = safe_float(root_tree_data.get("baseline"), 0.0)
    rev_val = safe_float(root_tree_data.get("value"), fallback_val)
    rev_base = safe_float(root_tree_data.get("baseline"), fallback_val)
    diff = rev_val - rev_base

    return {
        "node_adjusted": req.node_adjusted,
        "new_value": safe_float(req.new_value, safe_float(metric_snapshot.get(req.node_adjusted, {}).get("baseline"), 0.0)),
        "updated_causal_tree": updated_causal_tree,
        "projected_revenue": rev_val,
        "projected_diff": round(diff, 2),
        "impact_summary": f"Projected {root_node_name}: ${rev_val:,.2f} ({'+' if diff>=0 else ''}${diff:,.2f} vs baseline)"
    }

@app.post("/api/execute_mitigation")
def execute_mitigation(req: MitigationRequest):
    """
    100% Generalized Mathematical Mitigation Engine.
    Uses calculated rolling baselines rather than hardcoded scenario branches.
    """
    metrics_path = os.path.join(DATA_DIR, "metrics_timeseries.csv")
    df_metrics = pd.read_csv(metrics_path)
    
    is_rollback = req.action_type != "REINJECT_ANOMALY"
    mask_scen = df_metrics['scenario_id'] == req.scenario_id
    scen_dates = sorted(df_metrics[mask_scen]['timestamp'].unique())
    incident_window = scen_dates[-15:] if len(scen_dates) >= 15 else scen_dates

    # Dynamically restore metrics to their pre-incident rolling baselines
    for kpi in df_metrics[mask_scen]['kpi_name'].unique():
        kpi_mask = mask_scen & (df_metrics['kpi_name'] == kpi)
        kpi_series = df_metrics[kpi_mask].sort_values('timestamp')
        
        # Calculate pre-incident mean and std
        baseline_rows = kpi_series[~kpi_series['timestamp'].isin(incident_window)]
        base_mean = baseline_rows['value'].mean() if not baseline_rows.empty else kpi_series['value'].mean()
        base_std = baseline_rows['value'].std() if not baseline_rows.empty else (base_mean * 0.02)
        if math.isnan(base_std) or base_std <= 0:
            base_std = max(1.0, abs(base_mean) * 0.02)

        for d in incident_window:
            d_mask = kpi_mask & (df_metrics['timestamp'] == d)
            if is_rollback:
                # Restore to healthy baseline value with small realistic variance
                healthy_val = round(base_mean + random.gauss(0, base_std * 0.5), 2)
                df_metrics.loc[d_mask, 'value'] = healthy_val
            else:
                # Re-apply simulated anomaly breach dynamically
                # For rate metrics: drop to 55% of baseline
                # For volume metrics: apply 3-sigma deviation
                if kpi in ['Payment_Success_Rate', 'Conversion_Rate']:
                    anomaly_val = round(base_mean * 0.55 + random.gauss(0, base_std * 0.5), 2)
                elif kpi in ['Sessions', 'AOV']:
                    anomaly_val = round(base_mean * 1.35 + random.gauss(0, base_std), 2)
                else:
                    anomaly_val = round(base_mean - 3 * base_std + random.gauss(0, base_std * 0.5), 2)
                df_metrics.loc[d_mask, 'value'] = anomaly_val

    # Recompute Revenue = Sessions * (Conversion_Rate / 100) * AOV for consistency
    if 'Revenue' in df_metrics['kpi_name'].values:
        for d in incident_window:
            d_scen_mask = mask_scen & (df_metrics['timestamp'] == d)
            s_val = df_metrics.loc[d_scen_mask & (df_metrics['kpi_name'] == 'Sessions'), 'value'].values
            c_val = df_metrics.loc[d_scen_mask & (df_metrics['kpi_name'] == 'Conversion_Rate'), 'value'].values
            a_val = df_metrics.loc[d_scen_mask & (df_metrics['kpi_name'] == 'AOV'), 'value'].values
            if len(s_val) > 0 and len(c_val) > 0 and len(a_val) > 0:
                calc_rev = round(float(s_val[0]) * (float(c_val[0]) / 100.0) * float(a_val[0]), 2)
                df_metrics.loc[d_scen_mask & (df_metrics['kpi_name'] == 'Revenue'), 'value'] = calc_rev

    df_metrics.to_csv(metrics_path, index=False)

    if is_rollback:
        action_msg = "Automated Production Rollback Executed (Restored healthy baseline metrics)."
        status_msg = "Root-cause service patch applied. Key metrics restored to baseline (Z-score: 0.0)."
    else:
        action_msg = "Scenario Anomaly Re-Injected (Outage state reset for demonstration)."
        status_msg = "Original incident state re-applied. Critical anomaly breach active."

    return {
        "status": "SUCCESS",
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_type": req.action_type,
        "mitigation_event": {
            "ticket_created": f"INC-{pd.Timestamp.now().strftime('%Y')}-{random.randint(1000,9999)}",
            "action_taken": action_msg,
            "slack_notified": f"Posted update to #incident-response ({'Resolution' if is_rollback else 'Outage Active'})",
            "projected_recovery": status_msg
        }
    }

@app.post("/api/upload")
async def upload_dataset(
    metrics_file: UploadFile = File(...),
    jira_file: Optional[UploadFile] = File(None),
    zendesk_file: Optional[UploadFile] = File(None),
    slack_file: Optional[UploadFile] = File(None)
):
    """
    Enterprise Data Ingestion: Ingests any custom CSV datasets and refreshes ML pipelines.
    """
    try:
        # Stream files to disk (memory-safe for large enterprise datasets)
        with open(os.path.join(DATA_DIR, "metrics_timeseries.csv"), "wb") as f:
            shutil.copyfileobj(metrics_file.file, f)

        if jira_file:
            with open(os.path.join(DATA_DIR, "jira_deployments.csv"), "wb") as f:
                shutil.copyfileobj(jira_file.file, f)

        if zendesk_file:
            with open(os.path.join(DATA_DIR, "zendesk_tickets.csv"), "wb") as f:
                shutil.copyfileobj(zendesk_file.file, f)

        if slack_file:
            with open(os.path.join(DATA_DIR, "slack_alerts.csv"), "wb") as f:
                shutil.copyfileobj(slack_file.file, f)

        return {"status": "SUCCESS", "message": "Enterprise datasets ingested successfully into CortexKPI!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to ingest dataset: {str(e)}")

@app.post("/api/llm_narrative")
def get_llm_narrative(req: LLMNarrativeRequest):
    """
    Calls local Qwen 3.8 / Ollama / OpenAI endpoint or falls back to epistemic synthesis.
    """
    df_metrics, df_jira, df_zendesk, df_slack = load_datasets()
    df_scen = df_metrics[df_metrics['scenario_id'] == req.scenario_id]
    if df_scen.empty:
        df_scen = df_metrics

    # Perform analysis
    analysis = analyze_scenario(AnalyzeRequest(scenario_id=req.scenario_id, kpi_name="Revenue"))
    
    prompt = req.prompt or f"""
    You are an executive enterprise analytics AI.
    Scenario: {req.scenario_id}
    Anomaly Headline: {analysis['layer_4_narrative']['headline']}
    Financial Loss: {analysis['layer_4_narrative']['financial_loss']}
    Executive Summary: {analysis['layer_4_narrative']['executive_summary']}
    Top Evidence: {analysis['layer_3_evidence']}
    Write a 3-bullet executive briefing with:
    1. Root Cause Breakdown
    2. Corroborated Evidence
    3. Actionable Mitigation Plan
    """

    llm_output = narrative_engine.generate_llm_reasoning(
        prompt=prompt,
        api_base=req.api_base,
        api_key=req.api_key,
        model=req.model
    )

    if llm_output:
        return {"status": "SUCCESS", "source": "LOCAL_LLM", "narrative": llm_output}
    else:
        return {"status": "FALLBACK", "source": "EPISTEMIC_ML_ENGINE", "narrative": analysis['layer_4_narrative']['executive_summary']}

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
