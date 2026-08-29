document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing CortexKPI Executive Dashboard...");

  let currentScenarioId = "SCENARIO_1";
  let currentAnalysisData = null;
  let currentPersona = "csuite";

  const scenarioSelect = document.getElementById("scenario-select");
  const personaButtons = document.querySelectorAll(".persona-btn");
  const pdfExportBtn = document.getElementById("pdf-export-btn");

  // 1. Fetch Scenarios dynamically
  function loadScenariosList() {
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
  }

  loadScenariosList();

  // Scenario Switch Listener
  scenarioSelect.addEventListener("change", (e) => {
    currentScenarioId = e.target.value;
    runAnalysis(currentScenarioId);
  });

  // Persona Switcher Listener
  personaButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      personaButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const persona = btn.getAttribute("data-persona");

      document.body.classList.remove("persona-csuite", "persona-devops", "persona-bi");
      document.body.classList.add("persona-" + persona);
      currentPersona = persona;

      if (currentAnalysisData) {
        updateExecutiveBanner(currentAnalysisData.layer_4_narrative, persona);
        renderAllPanels(currentAnalysisData, currentScenarioId, persona);
      }
    });
  });

  // Reset Outage Header Button Listener
  const resetOutageBtn = document.getElementById("reset-outage-btn");
  if (resetOutageBtn) {
    resetOutageBtn.addEventListener("click", () => {
      handleMitigationExecution(currentScenarioId, "REINJECT_ANOMALY");
    });
  }

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
      updateExecutiveBanner(data.layer_4_narrative, currentPersona);
      renderAllPanels(data, scenarioId, currentPersona);
    })
    .catch(err => console.error("API Analysis Error:", err));
  }

  /**
   * Renders all 4 dashboard panels with persona-aware content.
   */
  function renderAllPanels(data, scenarioId, persona) {
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

    // Render Layer 3: Evidence Cards
    if (window.EvidenceComponent) {
      window.EvidenceComponent.render("evidence-container", data.layer_3_evidence, persona);
    }

    // Render Layer 4: Narrative & Honest Detective with Mitigation / Reset Action
    if (window.NarrativeComponent) {
      window.NarrativeComponent.render("narrative-container", data.layer_4_narrative, scenarioId, (scenId, actionType) => {
        handleMitigationExecution(scenId, actionType);
      }, persona, data.layer_2_causal_tree);
    }
  }

  /**
   * Updates executive summary banner
   */
  function updateExecutiveBanner(narrative, persona) {
    const titleEl = document.getElementById("banner-headline");
    const summaryEl = document.getElementById("banner-summary");
    const impactEl = document.getElementById("banner-impact");
    const badgeEl = document.querySelector(".executive-banner .badge-rose");

    if (!narrative) return;
    var hd = narrative.honest_detective || {};

    if (persona === "csuite") {
      if (titleEl) titleEl.innerText = narrative.headline;
      if (summaryEl) summaryEl.innerText = "Confidence: " + hd.confidence_pct + "% (" + hd.confidence_level + ")";
      if (impactEl) impactEl.innerText = narrative.financial_loss;
      if (badgeEl) badgeEl.innerHTML = "\uD83D\uDD34 CRITICAL ANOMALY DETECTED";

    } else if (persona === "devops") {
      if (titleEl) titleEl.innerText = "\u26A0\uFE0F INCIDENT: " + narrative.headline;
      if (summaryEl) summaryEl.innerText = "Diagnostic Confidence: " + hd.confidence_pct + "% | Automated Triage Active";
      if (impactEl) {
        impactEl.innerText = narrative.financial_loss;
        impactEl.style.color = "var(--health-green)";
      }
      if (badgeEl) badgeEl.innerHTML = "\u26A1 INCIDENT RESPONSE ACTIVE";

    } else if (persona === "bi") {
      if (titleEl) titleEl.innerText = "\uD83D\uDCC8 STATISTICAL ANALYSIS: " + narrative.headline;
      if (summaryEl) summaryEl.innerText = "Model Confidence: " + hd.confidence_pct + "% | P-value < 0.001 | " + hd.confidence_level;
      if (impactEl) {
        impactEl.innerText = narrative.financial_loss;
        impactEl.style.color = "var(--accent-purple)";
      }
      if (badgeEl) badgeEl.innerHTML = "\uD83D\uDCCA ANOMALY SIGNIFICANCE: HIGH";
    }
  }

  // Live What-If Counterfactual Simulation Handler
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
        impactEl.innerText = "$" + simResult.projected_revenue.toLocaleString();
      }
      if (window.TreeComponent && simResult.updated_causal_tree) {
        window.TreeComponent.updateNodeValues(simResult.updated_causal_tree);
      }
    })
    .catch(err => console.error("What-If Simulation Error:", err));
  }

  // Live Mitigation Execution / Reset Handler
  function handleMitigationExecution(scenarioId, actionType) {
    actionType = actionType || "ROLLBACK_DEPLOYMENT";
    fetch("/api/execute_mitigation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, action_type: actionType })
    })
    .then(res => res.json())
    .then(res => {
      const isRollback = actionType === "ROLLBACK_DEPLOYMENT";
      const icon = isRollback ? "✅" : "↺";
      const title = isRollback ? "AUTOMATED ROLLBACK EXECUTED" : "OUTAGE ANOMALY RE-INJECTED";

      alert(`${icon} ${title}!\n\nTicket: ${res.mitigation_event.ticket_created}\nAction: ${res.mitigation_event.action_taken}\nStatus: ${res.mitigation_event.projected_recovery}`);
      
      // Re-run Analysis Pipeline to visually update dashboard metrics!
      runAnalysis(scenarioId);
      loadScenariosList();
    })
    .catch(err => console.error("Mitigation Execution Error:", err));
  }
});
