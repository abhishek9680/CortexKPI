import math
import numpy as np
import networkx as nx

def safe_float(val, default=0.0):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except Exception:
        return default

class CausalMetricTreeML:
    """
    Layer 2: Causal Metric Dependency Graph Variance Attribution Model
    Mathematical graph decomposition isolating failing leaf nodes & powering 'What-If' simulations.
    Safely sanitizes all numerical floats for JSON output.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_metric_graph()

    def _build_metric_graph(self):
        self.graph.add_node("Revenue", label="Revenue ($)", type="ROOT", unit="USD")
        self.graph.add_node("Sessions", label="Sessions (Traffic)", type="SUB_METRIC", unit="count")
        self.graph.add_node("Conversion_Rate", label="Conversion Rate (%)", type="SUB_METRIC", unit="%")
        self.graph.add_node("AOV", label="Average Order Value ($)", type="SUB_METRIC", unit="USD")
        self.graph.add_node("Payment_Success_Rate", label="Payment Success Rate (%)", type="LEAF", unit="%")

        self.graph.add_edge("Revenue", "Sessions", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Revenue", "Conversion_Rate", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Revenue", "AOV", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Conversion_Rate", "Payment_Success_Rate", relationship="DIRECT_FACTOR")

    def decompose_anomaly(self, metric_snapshot):
        tree_results = {}
        failing_path = []
        max_negative_z = 0.0
        root_cause_node = None

        for node in self.graph.nodes():
            data = metric_snapshot.get(node, {"value": 100, "baseline": 100, "z_score": 0.0})
            val = safe_float(data.get("value"), 100.0)
            base = safe_float(data.get("baseline"), 100.0)
            z = safe_float(data.get("z_score"), 0.0)
            
            delta_pct = round(((val - base) / (base + 1e-5)) * 100, 2) if base != 0 else 0.0
            delta_pct = safe_float(delta_pct, 0.0)

            if z <= -2.0:
                status = "CRITICAL_FAIL"
                if z < max_negative_z:
                    max_negative_z = z
                    root_cause_node = node
            elif z <= -1.0:
                status = "WARNING"
            else:
                status = "HEALTHY"

            tree_results[node] = {
                "name": node,
                "label": self.graph.nodes[node]["label"],
                "value": val,
                "baseline": base,
                "z_score": z,
                "delta_pct": delta_pct,
                "status": status,
                "type": self.graph.nodes[node]["type"]
            }

        rev_base_delta = abs(tree_results["Revenue"]["delta_pct"])
        if rev_base_delta > 0:
            for child in ["Sessions", "Conversion_Rate", "AOV"]:
                child_delta = abs(tree_results[child]["delta_pct"])
                contribution = round(min(100.0, (child_delta / (rev_base_delta + 0.0001)) * 100), 1)
                tree_results[child]["variance_contribution_pct"] = safe_float(contribution, 0.0)
        
        if root_cause_node:
            failing_path = ["Revenue", "Conversion_Rate", root_cause_node]

        return {
            "tree": tree_results,
            "root_cause_leaf": root_cause_node,
            "failing_path": failing_path,
            "edges": list(self.graph.edges())
        }

    def simulate_whatif(self, metric_snapshot, node_adjusted, new_value):
        snapshot = {k: dict(v) for k, v in metric_snapshot.items()}
        if node_adjusted in snapshot:
            snapshot[node_adjusted]["value"] = safe_float(new_value, 90.0)
            
            if node_adjusted == "Payment_Success_Rate":
                base_auth = safe_float(metric_snapshot["Payment_Success_Rate"]["baseline"], 98.0)
                conv_baseline = safe_float(metric_snapshot["Conversion_Rate"]["baseline"], 2.85)
                ratio = new_value / (base_auth + 1e-5)
                snapshot["Conversion_Rate"]["value"] = round(conv_baseline * ratio, 2)

            sess = safe_float(snapshot["Sessions"]["value"], 120000)
            cvr = safe_float(snapshot["Conversion_Rate"]["value"], 2.85) / 100.0 if snapshot["Conversion_Rate"]["value"] > 1 else safe_float(snapshot["Conversion_Rate"]["value"], 0.0285)
            aov = safe_float(snapshot["AOV"]["value"], 185.0)
            snapshot["Revenue"]["value"] = round(sess * cvr * aov, 2)

        return self.decompose_anomaly(snapshot)
