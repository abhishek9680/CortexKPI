document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing CortexKPI Simplified Executive Dashboard...");

  let currentScenarioId = "SCENARIO_1";
  let currentAnalysisData = null;
  let currentPersona = "csuite";
  let currentMode = "simple"; // 'simple' or 'technical'

  const scenarioSelect = document.getElementById("scenario-select");
  const personaButtons = document.querySelectorAll(".persona-btn");
  const pdfExportBtn = document.getElementById("pdf-export-btn");
  const uploadDataBtn = document.getElementById("upload-data-btn");
  const uploadModal = document.getElementById("upload-modal");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const dropZone = document.getElementById("drop-zone");
  const metricsFileInput = document.getElementById("metrics-file-input");
  const uploadForm = document.getElementById("upload-form");
  const selectedFilename = document.getElementById("selected-filename");
  const playSimBtn = document.getElementById("play-sim-btn");
  const llmNarrativeBtn = document.getElementById("llm-narrative-btn");
  const modeSimpleBtn = document.getElementById("mode-simple-btn");
  const modeTechBtn = document.getElementById("mode-tech-btn");

  // Mode Switcher Listeners
  if (modeSimpleBtn && modeTechBtn) {
    modeSimpleBtn.addEventListener("click", () => {
      modeSimpleBtn.classList.add("active");
      modeTechBtn.classList.remove("active");
      document.body.classList.add("mode-simple");
      document.body.classList.remove("mode-technical");
      currentMode = "simple";
      if (currentAnalysisData) renderAllPanels(currentAnalysisData, currentScenarioId, currentPersona);
    });

    modeTechBtn.addEventListener("click", () => {
      modeTechBtn.classList.add("active");
      modeSimpleBtn.classList.remove("active");
      document.body.classList.add("mode-technical");
      document.body.classList.remove("mode-simple");
      currentMode = "technical";
      if (currentAnalysisData) renderAllPanels(currentAnalysisData, currentScenarioId, currentPersona);
    });
  }

  let scenariosMap = {};

  // 1. Fetch Scenarios dynamically
  function loadScenariosList() {
    fetch("/api/scenarios")
      .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
      .then(data => {
        scenarioSelect.innerHTML = "";
        data.scenarios.forEach(scen => {
          scenariosMap[scen.id] = scen;
          const opt = document.createElement("option");
          opt.value = scen.id;
          opt.innerText = scen.name;
          scenarioSelect.appendChild(opt);
        });
        if (data.scenarios.length > 0) {
          currentScenarioId = data.scenarios[0].id;
          scenarioSelect.value = currentScenarioId;
        }
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

  // Upload Dataset Modal Controls
  if (uploadDataBtn && uploadModal) {
    uploadDataBtn.addEventListener("click", () => uploadModal.classList.add("active"));
  }
  if (modalCloseBtn && uploadModal) {
    modalCloseBtn.addEventListener("click", () => uploadModal.classList.remove("active"));
  }
  if (dropZone && metricsFileInput) {
    dropZone.addEventListener("click", () => metricsFileInput.click());
    metricsFileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        selectedFilename.innerText = `Selected: ${e.target.files[0].name} (${(e.target.files[0].size/1024).toFixed(1)} KB)`;
      }
    });
  }
  if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const file = metricsFileInput.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("metrics_file", file);

      const submitBtn = document.getElementById("submit-upload-btn");
      submitBtn.innerText = "⏳ Ingesting & Running ML Pipelines...";
      submitBtn.disabled = true;

      fetch("/api/upload", {
        method: "POST",
        body: formData
      })
      .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
      .then(res => {
        alert("✅ " + res.message);
        uploadModal.classList.remove("active");
        submitBtn.innerText = "⚡ Ingest & Run Full 4-Layer ML Pipeline";
        submitBtn.disabled = false;
        loadScenariosList();
      })
      .catch(err => {
        alert("❌ Ingestion error: " + err);
        submitBtn.innerText = "⚡ Ingest & Run Full 4-Layer ML Pipeline";
        submitBtn.disabled = false;
      });
    });
  }

  // Live Simulation Replay Ticker
  if (playSimBtn) {
    let isPlaying = false;
    let playInterval = null;
    playSimBtn.addEventListener("click", () => {
      if (!currentAnalysisData || !currentAnalysisData.layer_1_timeseries) return;
      const ts = currentAnalysisData.layer_1_timeseries;
      if (isPlaying) {
        clearInterval(playInterval);
        isPlaying = false;
        playSimBtn.innerText = "▶ Live Replay";
        window.ChartComponent.render("timeseries-canvas", ts);
      } else {
        isPlaying = true;
        playSimBtn.innerText = "⏹ Stop Replay";
        let step = Math.max(0, ts.length - 25);
        playInterval = setInterval(() => {
          if (step >= ts.length) {
            clearInterval(playInterval);
            isPlaying = false;
            playSimBtn.innerText = "▶ Live Replay";
            return;
          }
          const sliced = ts.slice(0, step + 1);
          window.ChartComponent.render("timeseries-canvas", sliced);
          step++;
        }, 120);
      }
    });
  }

  // Live AI Briefing (Qwen / LLM) Listener
  if (llmNarrativeBtn) {
    llmNarrativeBtn.addEventListener("click", () => {
      llmNarrativeBtn.innerText = "🤖 Generating...";
      llmNarrativeBtn.disabled = true;

      fetch("/api/llm_narrative", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: currentScenarioId })
      })
      .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
      .then(res => {
        llmNarrativeBtn.innerText = "🤖 AI Briefing (Qwen / LLM)";
        llmNarrativeBtn.disabled = false;
        
        const narrativeEl = document.getElementById("narrative-container");
        if (narrativeEl) {
          const aiBox = document.createElement("div");
          aiBox.className = "glass-panel";
          aiBox.style.cssText = "border: 1px solid #8b5cf6; background: rgba(139, 92, 246, 0.12); padding: 14px; border-radius: 10px; margin-top: 14px;";
          aiBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-weight:700; color:#c084fc; font-size:0.85rem;">🤖 LIVE AI EXECUTIVE REASONING (${res.source})</span>
              <span class="badge badge-purple" style="font-size:0.7rem;">Real-time LLM Output</span>
            </div>
            <p style="font-size:0.85rem; color:#e2e8f0; line-height:1.5; margin:0; white-space:pre-wrap;">${res.narrative}</p>
          `;
          narrativeEl.prepend(aiBox);
        }
      })
      .catch(err => {
        llmNarrativeBtn.innerText = "🤖 AI Briefing (Qwen / LLM)";
        llmNarrativeBtn.disabled = false;
        console.error("LLM reasoning error:", err);
      });
    });
  }

  // 2. Main Analysis Pipeline API Runner
  function runAnalysis(scenarioId) {
    const kpiName = scenariosMap[scenarioId] ? scenariosMap[scenarioId].kpi : "Revenue";
    fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, kpi_name: kpiName })
    })
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(data => {
      currentAnalysisData = data;
      updateExecutiveBanner(data.layer_4_narrative, currentPersona);
      renderAllPanels(data, scenarioId, currentPersona);
    })
    .catch(err => console.error("API Analysis Error:", err));
  }

  let lastSelectedNode = null;

  /**
   * Renders all 4 dashboard panels with persona-aware content.
   */
  function renderAllPanels(data, scenarioId, persona) {
    lastSelectedNode = null; // reset filter state on render

    // Render Step 1: Time Series Chart
    if (window.ChartComponent) {
      window.ChartComponent.render("timeseries-canvas", data.layer_1_timeseries);
    }

    // Render Step 2: Causal Metric Tree & What-If Listener
    if (window.TreeComponent) {
      window.TreeComponent.render("causal-tree-container", data.layer_2_causal_tree, (nodeAdjusted, newValue) => {
        handleWhatIfSimulation(scenarioId, nodeAdjusted, newValue);
      }, (selectedNode) => {
        // Toggle filter or filter Step 3 evidence by selected node
        if (window.EvidenceComponent && data.layer_3_evidence) {
          if (lastSelectedNode === selectedNode) {
            lastSelectedNode = null;
            window.EvidenceComponent.render("evidence-container", data.layer_3_evidence, persona);
          } else {
            lastSelectedNode = selectedNode;
            const searchStr = selectedNode.replace(/_/g, ' ').toLowerCase();
            const filtered = data.layer_3_evidence.filter(e => 
              e.title.toLowerCase().includes(searchStr) || 
              e.details.toLowerCase().includes(searchStr)
            );
            window.EvidenceComponent.render("evidence-container", filtered.length > 0 ? filtered : data.layer_3_evidence, persona);
          }
        }
      });
    }

    // Render Step 3: Evidence Cards
    if (window.EvidenceComponent) {
      window.EvidenceComponent.render("evidence-container", data.layer_3_evidence, persona);
    }

    // Render Step 4: Narrative & Honest Detective
    if (window.NarrativeComponent) {
      window.NarrativeComponent.render("narrative-container", data.layer_4_narrative, scenarioId, (scenId, actionType) => {
        handleMitigationExecution(scenId, actionType);
      }, persona, data.layer_2_causal_tree, currentMode);
    }
  }

  /**
   * Updates executive summary banner
   */
  function updateExecutiveBanner(narrative, persona) {
    const titleEl = document.getElementById("banner-headline");
    const summaryEl = document.getElementById("banner-summary");
    const impactEl = document.getElementById("banner-impact");
    const badgeEl = document.getElementById("banner-badge");

    if (!narrative) return;
    var hd = narrative.honest_detective || {};
    var isSurge = (narrative.financial_loss && narrative.financial_loss.includes("+")) || 
                  (narrative.headline && narrative.headline.includes("surged"));
    document.body.classList.toggle('data-surge', isSurge);

    if (persona === "csuite") {
      if (titleEl) titleEl.innerText = narrative.headline;
      if (summaryEl) summaryEl.innerText = "Confidence: " + hd.confidence_pct + "% (" + hd.confidence_level + ")";
      if (impactEl) {
        impactEl.innerText = narrative.financial_loss;
        impactEl.style.color = isSurge ? "var(--health-green)" : "var(--anomaly-rose)";
      }
      if (badgeEl) {
        badgeEl.innerHTML = isSurge ? "🟢 POSITIVE GROWTH SURGE DETECTED" : "🔴 CRITICAL ANOMALY DETECTED";
        badgeEl.className = isSurge ? "badge badge-green" : "badge badge-rose pulse-anomaly";
      }

    } else if (persona === "devops") {
      if (titleEl) titleEl.innerText = (isSurge ? "📈 SURGE: " : "⚠️ INCIDENT: ") + narrative.headline;
      if (summaryEl) summaryEl.innerText = "Diagnostic Confidence: " + hd.confidence_pct + "% | Automated Triage Active";
      if (impactEl) {
        impactEl.innerText = narrative.financial_loss;
        impactEl.style.color = isSurge ? "var(--health-green)" : "var(--anomaly-rose)";
      }
      if (badgeEl) {
        badgeEl.innerHTML = isSurge ? "⚡ TRAFFIC SURGE ACTIVE" : "⚡ INCIDENT RESPONSE ACTIVE";
        badgeEl.className = isSurge ? "badge badge-green" : "badge badge-rose pulse-anomaly";
      }

    } else if (persona === "bi") {
      if (titleEl) titleEl.innerText = "📈 STATISTICAL ANALYSIS: " + narrative.headline;
      if (summaryEl) summaryEl.innerText = "Model Confidence: " + hd.confidence_pct + "% | P-value < 0.001 | " + hd.confidence_level;
      if (impactEl) {
        impactEl.innerText = narrative.financial_loss;
        impactEl.style.color = isSurge ? "var(--health-green)" : "var(--accent-purple)";
      }
      if (badgeEl) {
        badgeEl.innerHTML = isSurge ? "📊 POSITIVE BREAKOUT: Z > +2.0" : "📊 ANOMALY SIGNIFICANCE: HIGH";
        badgeEl.className = isSurge ? "badge badge-green" : "badge badge-rose pulse-anomaly";
      }
    }
  }

  // Live What-If Counterfactual Simulation Handler
  function handleWhatIfSimulation(scenarioId, nodeAdjusted, newValue) {
    fetch("/api/simulate_whatif", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, node_adjusted: nodeAdjusted, new_value: newValue })
    })
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(simResult => {
      const impactEl = document.getElementById("banner-impact");
      if (impactEl) {
        impactEl.innerText = "$" + Number(simResult.projected_revenue).toLocaleString(undefined, {maximumFractionDigits: 2});
      }

      if (window.TreeComponent && simResult.updated_causal_tree) {
        window.TreeComponent.updateNodeValues(simResult.updated_causal_tree);
      }

      if (window.ChartComponent) {
        window.ChartComponent.updateSimulatedPoint(simResult.projected_revenue);
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
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(res => {
      const isRollback = actionType === "ROLLBACK_DEPLOYMENT";
      const icon = isRollback ? "✅" : "↺";
      const title = isRollback ? "AUTOMATED ROLLBACK EXECUTED" : "OUTAGE ANOMALY RE-INJECTED";

      alert(`${icon} ${title}!\n\nTicket: ${res.mitigation_event.ticket_created}\nAction: ${res.mitigation_event.action_taken}\nStatus: ${res.mitigation_event.projected_recovery}`);
      
      runAnalysis(scenarioId);
      loadScenariosList();
    })
    .catch(err => console.error("Mitigation Execution Error:", err));
  }
});
