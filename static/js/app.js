document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing CortexKPI Executive Dashboard...");

  let currentScenarioId = "SCENARIO_1";
  let currentAnalysisData = null;

  const scenarioSelect = document.getElementById("scenario-select");
  const personaButtons = document.querySelectorAll(".persona-btn");
  const pdfExportBtn = document.getElementById("pdf-export-btn");

  // 1. Fetch Scenarios
  fetch("/api/scenarios")
    .then(res => res.json())
    .then(data => {
      scenarioSelect.innerHTML = "";
      data.scenarios.forEach(scen => {
        const opt = document.createElement("option");
        opt.value = scen.id;
        opt.innerText = scen.name;
        scenarioSelect.appendChild(opt);
      });
      scenarioSelect.value = currentScenarioId;
      runAnalysis(currentScenarioId);
    })
    .catch(err => {
      console.error("Error fetching scenarios:", err);
      runAnalysis(currentScenarioId);
    });

  // Scenario Switch Listener
  scenarioSelect.addEventListener("change", (e) => {
    currentScenarioId = e.target.value;
    runAnalysis(currentScenarioId);
  });

  // Persona Switcher Listener (C-Suite vs DevOps vs BI Analyst)
  personaButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      personaButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const persona = btn.getAttribute("data-persona");
      
      document.body.classList.remove("persona-csuite", "persona-devops", "persona-bi");
      document.body.classList.add(`persona-${persona}`);
    });
  });

  // PDF Export Listener
  if (pdfExportBtn) {
    pdfExportBtn.addEventListener("click", () => {
      if (window.PDFExportComponent && currentAnalysisData) {
        window.PDFExportComponent.exportReport(currentAnalysisData);
      }
    });
  }

  // 2. Main Analysis Pipeline API Runner
  function runAnalysis(scenarioId) {
    fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, kpi_name: "Revenue" })
    })
    .then(res => res.json())
    .then(data => {
      currentAnalysisData = data;
      updateExecutiveBanner(data.layer_4_narrative);
      
      // Render Layer 1: Time Series Chart
      if (window.ChartComponent) {
        window.ChartComponent.render("timeseries-canvas", data.layer_1_timeseries);
      }

      // Render Layer 2: Causal Metric Tree & What-If Listener
      if (window.TreeComponent) {
        window.TreeComponent.render("causal-tree-container", data.layer_2_causal_tree, (nodeAdjusted, newValue) => {
          handleWhatIfSimulation(scenarioId, nodeAdjusted, newValue);
        });
      }

      // Render Layer 3: Multimodal RAG Evidence Cards
      if (window.EvidenceComponent) {
        window.EvidenceComponent.render("evidence-container", data.layer_3_evidence);
      }

      // Render Layer 4: Honest Detective Console & Mitigation Trigger
      if (window.NarrativeComponent) {
        window.NarrativeComponent.render("narrative-container", data.layer_4_narrative, scenarioId, (scenId) => {
          handleMitigationExecution(scenId);
        });
      }
    })
    .catch(err => console.error("API Analysis Error:", err));
  }

  function updateExecutiveBanner(narrative) {
    const titleEl = document.getElementById("banner-headline");
    const summaryEl = document.getElementById("banner-summary");
    const impactEl = document.getElementById("banner-impact");

    if (narrative) {
      if (titleEl) titleEl.innerText = narrative.headline;
      if (summaryEl) summaryEl.innerText = `Confidence: ${narrative.honest_detective.confidence_pct}% (${narrative.honest_detective.confidence_level})`;
      if (impactEl) impactEl.innerText = narrative.financial_loss;
    }
  }

  function handleWhatIfSimulation(scenarioId, nodeAdjusted, newValue) {
    fetch("/api/simulate_whatif", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, node_adjusted: nodeAdjusted, new_value: newValue })
    })
    .then(res => res.json())
    .then(simResult => {
      const impactEl = document.getElementById("banner-impact");
      if (impactEl) {
        impactEl.innerText = `$${simResult.projected_revenue.toLocaleString()}`;
      }
    })
    .catch(err => console.error("What-If Simulation Error:", err));
  }

  function handleMitigationExecution(scenarioId) {
    fetch("/api/execute_mitigation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, action_type: "ROLLBACK_DEPLOYMENT" })
    })
    .then(res => res.json())
    .then(res => {
      alert(`✅ AUTOMATED MITIGATION EXECUTED SUCCESSFULLY!\n\nTicket: ${res.mitigation_event.ticket_created}\nAction: ${res.mitigation_event.action_taken}\nStatus: ${res.mitigation_event.projected_recovery}`);
      const btn = document.getElementById("execute-mitigation-btn");
      if (btn) {
        btn.innerText = "✅ Rollback Triggered (INC-2026-8890)";
        btn.style.background = "#10B981";
      }
    })
    .catch(err => console.error("Mitigation Execution Error:", err));
  }
});
