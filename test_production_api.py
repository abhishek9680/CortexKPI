import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def api_get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def api_post(path, data):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

print("============================================================")
print("RUNNING CORTEXKPI PRODUCTION SUITE VERIFICATION")
print("============================================================")

# 1. Test Scenarios
status, data = api_get("/api/scenarios")
assert status == 200, f"Failed GET /api/scenarios: {status}"
print(f"[PASS] GET /api/scenarios -> {status}, found {len(data['scenarios'])} scenarios")

# 2. Test Analyze across Scenarios
for scen in ["SCENARIO_1", "SCENARIO_2", "SCENARIO_3"]:
    status, res = api_post("/api/analyze", {"scenario_id": scen, "kpi_name": "Revenue"})
    assert status == 200, f"Failed analyze on {scen}"
    print(f"[PASS] POST /api/analyze ({scen}) -> 200")
    print(f"       Headline: {res['layer_4_narrative']['headline']}")
    print(f"       Financial: {res['layer_4_narrative']['financial_loss']}")
    print(f"       Confidence: {res['layer_4_narrative']['honest_detective']['confidence_pct']}% ({res['layer_4_narrative']['honest_detective']['confidence_level']})")
    print(f"       Top Evidence: {len(res['layer_3_evidence'])} items matched")

# 3. Test What-If Counterfactual Simulation
status, res = api_post("/api/simulate_whatif", {
    "scenario_id": "SCENARIO_1",
    "node_adjusted": "Payment_Success_Rate",
    "new_value": 98.2
})
assert status == 200, "Failed whatif"
print(f"[PASS] POST /api/simulate_whatif -> 200")
print(f"       {res['impact_summary']}")

# 4. Test Mitigation Rollback
status, res = api_post("/api/execute_mitigation", {
    "scenario_id": "SCENARIO_1",
    "action_type": "ROLLBACK_DEPLOYMENT"
})
assert status == 200, "Failed mitigation"
print(f"[PASS] POST /api/execute_mitigation (ROLLBACK) -> 200: {res['mitigation_event']['action_taken']}")

# 5. Test LLM Narrative Endpoint
status, res = api_post("/api/llm_narrative", {
    "scenario_id": "SCENARIO_1"
})
assert status == 200, "Failed LLM narrative"
print(f"[PASS] POST /api/llm_narrative -> 200 (Source: {res['source']})")

print("============================================================")
print("ALL PRODUCTION ENGINE TESTS PASSED WITH ZERO FLIGHT FLAWS!")
print("============================================================")
