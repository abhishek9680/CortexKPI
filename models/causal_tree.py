import networkx as nx

class CausalMetricTreeML:
    """
    Layer 2: Causal Metric Dependency Graph Variance Attribution Model
    Mathematical graph decomposition isolating failing leaf nodes & powering 'What-If' simulations.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_metric_graph()

    def _build_metric_graph(self):
        """
        Build directed metric dependency graph:
        Revenue = Sessions * Conversion_Rate * AOV
        Conversion_Rate = Payment_Success_Rate * Checkout_CVR
        """
        # Nodes: (name, formula_type, label)
        self.graph.add_node("Revenue", label="Revenue ($)", type="ROOT", unit="USD")
        self.graph.add_node("Sessions", label="Sessions (Traffic)", type="SUB_METRIC", unit="count")
        self.graph.add_node("Conversion_Rate", label="Conversion Rate (%)", type="SUB_METRIC", unit="%")
        self.graph.add_node("AOV", label="Average Order Value ($)", type="SUB_METRIC", unit="USD")
        self.graph.add_node("Payment_Success_Rate", label="Payment Success Rate (%)", type="LEAF", unit="%")

        # Edges
        self.graph.add_edge("Revenue", "Sessions", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Revenue", "Conversion_Rate", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Revenue", "AOV", relationship="MULTIPLICATIVE")
        self.graph.add_edge("Conversion_Rate", "Payment_Success_Rate", relationship="DIRECT_FACTOR")

    def decompose_anomaly(self, metric_snapshot):
        """
        Input: dict of metric snapshots at anomaly date:
        {
          "Revenue": {"value": 245000, "baseline": 420000, "z_score": -3.85},
          "Sessions": {"value": 120000, "baseline": 118000, "z_score": +0.2},
          "Conversion_Rate": {"value": 1.12, "baseline": 1.94, "z_score": -4.12},
          "AOV": {"value": 182, "baseline": 183, "z_score": -0.3},
          "Payment_Success_Rate": {"value": 54.2, "baseline": 98.0, "z_score": -4.65}
        }
        """
        tree_results = {}
        failing_path = []
        max_negative_z = 0.0
        root_cause_node = None

        for node in self.graph.nodes():
            data = metric_snapshot.get(node, {"value": 100, "baseline": 100, "z_score": 0.0})
            val = float(data["value"])
            base = float(data["baseline"])
            z = float(data["z_score"])
            delta_pct = round(((val - base) / base) * 100, 2) if base != 0 else 0.0
            
            # Status classification
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

        # Calculate relative variance contributions for child nodes of Revenue
        rev_base_delta = abs(tree_results["Revenue"]["delta_pct"])
        if rev_base_delta > 0:
            for child in ["Sessions", "Conversion_Rate", "AOV"]:
                child_delta = abs(tree_results[child]["delta_pct"])
                contribution = round(min(100.0, (child_delta / (rev_base_delta + 0.0001)) * 100), 1)
                tree_results[child]["variance_contribution_pct"] = contribution
        
        # Build failing causal path array
        if root_cause_node:
            failing_path = ["Revenue", "Conversion_Rate", root_cause_node]

        return {
            "tree": tree_results,
            "root_cause_leaf": root_cause_node,
            "failing_path": failing_path,
            "edges": list(self.graph.edges())
        }

    def simulate_whatif(self, metric_snapshot, node_adjusted, new_value):
        """
        Counterfactual 'What-If' Simulation Model:
        Recalculate parent nodes if node_adjusted is modified to new_value.
        """
        snapshot = {k: dict(v) for k, v in metric_snapshot.items()}
        if node_adjusted in snapshot:
            snapshot[node_adjusted]["value"] = new_value
            
            # Recalculate Conv_Rate if Payment_Success_Rate changed
            if node_adjusted == "Payment_Success_Rate":
                base_auth = metric_snapshot["Payment_Success_Rate"]["baseline"]
                conv_baseline = metric_snapshot["Conversion_Rate"]["baseline"]
                ratio = new_value / (base_auth + 1e-5)
                snapshot["Conversion_Rate"]["value"] = round(conv_baseline * ratio, 2)

            # Recalculate Revenue = Sessions * Conversion_Rate * AOV
            sess = snapshot["Sessions"]["value"]
            cvr = snapshot["Conversion_Rate"]["value"] / 100.0 if snapshot["Conversion_Rate"]["value"] > 1 else snapshot["Conversion_Rate"]["value"]
            aov = snapshot["AOV"]["value"]
            snapshot["Revenue"]["value"] = round(sess * cvr * aov, 2)

        return self.decompose_anomaly(snapshot)
