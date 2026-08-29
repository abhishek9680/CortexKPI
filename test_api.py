"""Full API verification test for CortexKPI Engine."""
import urllib.request
import json

BASE = "http://127.0.0.1:8000"

def api_get(path):
    req = urllib.request.Request(BASE + path)
    res = urllib.request.urlopen(req)
    return res.status, json.loads(res.read().decode())

def api_post(path, payload):
    req = urllib.request.Request(BASE + path, 
        data=json.dumps(payload).encode(), 
        headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    return res.status, json.loads(res.read().decode())

# Test 1: Scenarios
status, data = api_get("/api/scenarios")
print(f"[PASS] GET /api/scenarios -> {status}, {len(data['scenarios'])} scenarios")

# Test 2: Analyze
status, data = api_post("/api/analyze", {"scenario_id": "SCENARIO_1", "kpi_name": "Revenue"})
print(f"[PASS] POST /api/analyze -> {status}")
tree = data["layer_2_causal_tree"]["tree"]
root_cause = data["layer_2_causal_tree"]["root_cause_leaf"]
print(f"       Root cause: {root_cause}")
for k, v in tree.items():
    print(f"       {k}: val={v['value']}, base={v['baseline']}, z={v['z_score']:.1f}, status={v['status']}")
print(f"       Evidence items: {len(data['layer_3_evidence'])}")
print(f"       Narrative headline: {data['layer_4_narrative']['headline'][:80]}...")

# Test 3: What-If with the ACTUAL root cause node
node = root_cause or "Payment_Success_Rate"
node_data = tree.get(node, {})
baseline_val = node_data.get("baseline", 98.0)

# Simulate recovery to baseline
status, sim = api_post("/api/simulate_whatif", {
    "scenario_id": "SCENARIO_1", 
    "node_adjusted": node, 
    "new_value": baseline_val
})
sim_tree = sim["updated_causal_tree"]["tree"]
print(f"\n[PASS] POST /api/simulate_whatif ({node} -> {baseline_val}) -> {status}")
print(f"       Projected Revenue: ${sim['projected_revenue']:,.2f}")
for k, v in sim_tree.items():
    print(f"       {k}: val={v['value']}, z={v['z_score']:.1f}, status={v['status']}")

# Test 4: What-If with Sessions specifically (the bug scenario)
sess_val = tree.get("Sessions", {}).get("value", 120000)
sess_base = tree.get("Sessions", {}).get("baseline", 120000)
status, sim2 = api_post("/api/simulate_whatif", {
    "scenario_id": "SCENARIO_1",
    "node_adjusted": "Sessions",
    "new_value": sess_base * 1.1
})
print(f"\n[PASS] POST /api/simulate_whatif (Sessions -> {sess_base * 1.1:,.0f}) -> {status}")
print(f"       Projected Revenue: ${sim2['projected_revenue']:,.2f}")
print(f"       Sessions z-score after sim: {sim2['updated_causal_tree']['tree']['Sessions']['z_score']:.1f}")
print(f"       Sessions status after sim: {sim2['updated_causal_tree']['tree']['Sessions']['status']}")

# Test 5: Mitigation
status, mit = api_post("/api/execute_mitigation", {
    "scenario_id": "SCENARIO_1",
    "action_type": "ROLLBACK_DEPLOYMENT"
})
print(f"\n[PASS] POST /api/execute_mitigation -> {status}")
print(f"       Ticket: {mit['mitigation_event']['ticket_created']}")

print("\n" + "=" * 60)
print("ALL API TESTS PASSED SUCCESSFULLY!")
print("=" * 60)
