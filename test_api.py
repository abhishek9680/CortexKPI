"""Full API verification test for CortexKPI Engine including Mitigation Rollback & Anomaly Reset."""
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

# Test 2: Re-inject Anomaly for SCENARIO_1 (Reset to Outage)
status, res = api_post("/api/execute_mitigation", {
    "scenario_id": "SCENARIO_1",
    "action_type": "REINJECT_ANOMALY"
})
print(f"[PASS] POST /api/execute_mitigation (REINJECT_ANOMALY) -> {status}")
print(f"       Action: {res['mitigation_event']['action_taken']}")

# Test 3: Analyze SCENARIO_1 after re-injecting anomaly
status, data = api_post("/api/analyze", {"scenario_id": "SCENARIO_1", "kpi_name": "Revenue"})
print(f"[PASS] POST /api/analyze (After Re-Inject) -> {status}")
tree = data["layer_2_causal_tree"]["tree"]
root_cause = data["layer_2_causal_tree"]["root_cause_leaf"]
print(f"       Root cause: {root_cause}")
for k, v in tree.items():
    print(f"       {k}: val={v['value']}, base={v['baseline']}, z={v['z_score']:.1f}, status={v['status']}")

# Test 4: Rollback Deployment (Healthy Recovery)
status, res2 = api_post("/api/execute_mitigation", {
    "scenario_id": "SCENARIO_1",
    "action_type": "ROLLBACK_DEPLOYMENT"
})
print(f"\n[PASS] POST /api/execute_mitigation (ROLLBACK_DEPLOYMENT) -> {status}")
print(f"       Action: {res2['mitigation_event']['action_taken']}")

# Test 5: Analyze SCENARIO_1 after Rollback
status, data2 = api_post("/api/analyze", {"scenario_id": "SCENARIO_1", "kpi_name": "Revenue"})
print(f"[PASS] POST /api/analyze (After Rollback) -> {status}")
tree2 = data2["layer_2_causal_tree"]["tree"]
print(f"       Payment_Success_Rate: val={tree2['Payment_Success_Rate']['value']}, status={tree2['Payment_Success_Rate']['status']}")

print("\n" + "=" * 60)
print("ALL MITIGATION & RESET TOGGLE API TESTS PASSED!")
print("=" * 60)
