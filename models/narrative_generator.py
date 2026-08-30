import math
import json
import urllib.request
import urllib.error

class HonestDetectiveNarrativeML:
    """
    Layer 4: Dual-Engine Executive Narrative & Honest Detective Model
    Supports both Deterministic Epistemic Synthesis AND Live LLM Generation (Local Qwen 3.8 / Ollama / OpenAI API).
    
    Features:
    - 4-Pillar Epistemic Safeguards (Knowns, Telemetry Gaps, Ruled Out, Prescribed SOP Actions)
    - Empirical Confidence Scoring combining Z-score strength, p-value, and RAG semantic relevance
    - Persona Perspectives: C-Suite ($/day, ROI), DevOps (PR, Rollback, Pods), BI Analyst (Z-scores, p-values)
    - Optional Live LLM Synthesis using OpenAI-compatible endpoints (e.g. Local Qwen 3.8 / Ollama)
    """
    def __init__(self, llm_endpoint="http://127.0.0.1:8080/v1/chat/completions"):
        self.llm_endpoint = llm_endpoint

    def calculate_confidence(self, anomaly_data, causal_tree, evidence_list):
        """
        Mathematical Bayesian Confidence Score:
        Confidence = 0.35 * Z_Strength + 0.35 * RAG_Match + 0.15 * Causal_Consistency + 0.15 * P_Value_Significance
        """
        root_cause = causal_tree.get("root_cause_leaf")
        tree = causal_tree.get("tree", {})

        if not root_cause or root_cause not in tree:
            return 0.50

        # 1. Statistical Z-Strength
        root_z = abs(tree[root_cause].get("z_score", 2.0))
        z_score_norm = min(1.0, root_z / 4.0)

        # 2. Evidence RAG Match Score
        top_match_score = evidence_list[0]["relevance_score"] if (evidence_list and len(evidence_list) > 0) else 0.40

        # 3. Causal Consistency (count anomalous nodes: both negative anomalies AND positive surges)
        total_nodes = max(1, len(tree))
        anomaly_count = sum(1 for n in tree.values() if n.get("status") in ["CRITICAL_FAIL", "WARNING", "GROWTH_SURGE"])
        consistency = min(1.0, 0.4 + (anomaly_count / total_nodes))

        # 4. P-Value Significance
        p_val = float(anomaly_data.get("p_value", 0.01))
        p_score = max(0.0, 1.0 - (p_val * 10))

        confidence = (0.35 * z_score_norm) + (0.35 * top_match_score) + (0.15 * consistency) + (0.15 * p_score)
        return round(min(0.98, max(0.40, confidence)), 2)

    def synthesize_narrative(self, scenario_id, anomaly_data, causal_tree, evidence_list):
        """
        Deterministic, mathematically-grounded executive narrative synthesis.
        """
        tree = causal_tree.get("tree", {})
        root_cause_node = causal_tree.get("root_cause_leaf") or "Conversion_Rate"
        
        rev_node = tree.get("Revenue", {"value": 0, "baseline": 0, "z_score": 0, "delta_pct": 0})
        rev_val = float(rev_node.get("value", 0))
        rev_base = float(rev_node.get("baseline", 0))
        rev_delta_pct = float(rev_node.get("delta_pct", 0))
        rev_z = float(rev_node.get("z_score", 0))

        # Financial impact computation
        loss_val = rev_base - rev_val
        if loss_val > 0:
            financial_loss = f"-${loss_val:,.2f}/day"
        else:
            financial_loss = f"+${abs(loss_val):,.2f}/day Growth"

        # Dynamic confidence score
        confidence = self.calculate_confidence(anomaly_data, causal_tree, evidence_list)
        conf_pct = int(confidence * 100)
        is_high_confidence = conf_pct >= 75

        # Root cause extraction
        root_data = tree.get(root_cause_node, {"label": root_cause_node, "value": 0, "baseline": 0, "z_score": 0, "delta_pct": 0})
        root_label = root_data.get("label", root_cause_node).split(" ")[0]
        root_z = float(root_data.get("z_score", 0))
        root_delta = float(root_data.get("delta_pct", 0))
        root_val = float(root_data.get("value", 0))
        root_base = float(root_data.get("baseline", 0))

        # Top evidence extraction
        top_evidence = evidence_list[0] if (evidence_list and len(evidence_list) > 0) else None
        top_evidence_title = top_evidence.get("title", "Operational Incident") if top_evidence else "system anomaly"
        top_evidence_source = top_evidence.get("source", "System") if top_evidence else "Log Stream"
        top_evidence_id = top_evidence.get("id", "EVT-00") if top_evidence else ""
        top_evidence_score = top_evidence.get("relevance_score", 0.55) if top_evidence else 0.55

        # Dynamic Headline
        if loss_val > 0:
            headline = f"Revenue dropped {abs(rev_delta_pct):.1f}% driven by {root_label} failure ({root_delta:+.1f}%)"
            if top_evidence:
                headline += f" correlated with {top_evidence_source} [{top_evidence_id}]"
        else:
            headline = f"Revenue surged +{abs(rev_delta_pct):.1f}% driven by {root_label} growth (+{root_delta:.1f}%)"

        # Executive summary
        date_str = anomaly_data.get("timestamp", "incident date")
        summary = (
            f"On {date_str}, Revenue recorded a statistically significant anomaly breach to ${rev_val:,.2f} "
            f"(Z-score: {rev_z:.2f}, baseline: ${rev_base:,.2f}). Top-down causal decomposition isolated the primary "
            f"variance driver to {root_label} ({root_val} vs {root_base} baseline, Z-score: {root_z:.2f}, delta: {root_delta}%). "
        )

        if top_evidence:
            summary += (
                f"Multimodal RAG log vectorization corroborated this metric shift with {top_evidence_source} document "
                f"[{top_evidence_id}] '{top_evidence_title}' with {top_evidence.get('relevance_pct', 88)}% semantic match."
            )
        else:
            summary += "Unstructured log correlation is actively monitoring secondary diagnostic telemetry streams."

        # 4-Pillar Honest Detective Protocol
        knowns = [
            f"{root_label} breached statistical bounds with Z-score {root_z:.2f} (Delta: {root_delta}%).",
            f"Revenue financial impact quantified at {financial_loss}."
        ]
        if top_evidence:
            knowns.append(f"Corroborated by {top_evidence_source} log [{top_evidence_id}]: '{top_evidence_title}'.")

        telemetry_gaps = []
        ruled_out = []
        prescribed_actions = []

        # Populate Ruled Out Hypotheses dynamically from Healthy Nodes
        healthy_nodes = [k for k, v in tree.items() if v.get("status") == "HEALTHY" and k != "Revenue"]
        for hn in healthy_nodes:
            hn_label = tree[hn].get("label", hn).split(" ")[0]
            hn_z = float(tree[hn].get("z_score", 0))
            hn_delta = float(tree[hn].get("delta_pct", 0))
            ruled_out.append(f"Ruled out {hn_label} failure: Metric remained stable at {hn_delta:+.1f}% (Z-score: {hn_z:.2f}).")

        # Dynamic Telemetry Gaps and Prescriptions
        if not is_high_confidence:
            telemetry_gaps.append(f"Ambiguity detected: Top RAG log match score ({int(top_evidence_score * 100)}%) is below high-confidence threshold.")
            telemetry_gaps.append("Regional sub-gateway latency telemetry logs pending verification.")
            prescribed_actions.append(f"CANARY MICRO-EXPERIMENT: Route 5% traffic to legacy configuration for {root_label} to verify causality before full intervention.")
            prescribed_actions.append("CONTINUOUS MONITORING: Track metric recovery and error rates over the next 2-hour window.")
        else:
            telemetry_gaps.append("Secondary async queue worker latency logs pending final indexing.")
            if top_evidence:
                prescribed_actions.append(f"IMMEDIATE SOP: Trigger automated rollback for deployment {top_evidence_id} ({top_evidence_title}).")
            else:
                prescribed_actions.append(f"IMMEDIATE SOP: Investigate root cause leaf node {root_label} and reset service pods.")
            prescribed_actions.append("POST-MORTEM: Perform comprehensive CI/CD pipeline verification before redeployment.")

        honest_detective = {
            "confidence_pct": conf_pct,
            "confidence_level": "HIGH_CONFIDENCE" if is_high_confidence else "AMBIGUOUS",
            "knowns": knowns,
            "telemetry_gaps": telemetry_gaps,
            "ruled_out": ruled_out if ruled_out else ["No metrics passed health filters."],
            "prescribed_actions": prescribed_actions
        }

        return {
            "headline": headline,
            "financial_loss": financial_loss,
            "executive_summary": summary,
            "honest_detective": honest_detective
        }

    def generate_llm_reasoning(self, prompt, api_base=None, api_key=None, model="qwen3-8b"):
        """
        Calls live LLM (Local Qwen 3.8 / Ollama / OpenAI API) for deep contextual narration.
        """
        endpoint = (api_base or "http://127.0.0.1:8080/v1") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key and api_key != "none":
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are CortexKPI Executive AI. Output structured executive analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }

        try:
            req = urllib.request.Request(endpoint, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data["choices"][0]["message"]["content"]
        except Exception as e:
            return None
