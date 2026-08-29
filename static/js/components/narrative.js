window.NarrativeComponent = {
  /**
   * Renders Layer 4 with persona-aware content.
   * @param {string} persona - 'csuite', 'devops', or 'bi'
   * @param {object} causalTree - Layer 2 causal tree data for BI stats
   */
  render: function(containerId, narrativeData, scenarioId, onMitigateTrigger, persona, causalTree) {
    var container = document.getElementById(containerId);
    if (!container) return;

    persona = persona || "csuite";
    var hd = narrativeData.honest_detective || {};
    var confPct = hd.confidence_pct || 55;
    var isHighConf = confPct >= 80;

    var html = "";

    // ============================
    // PERSONA CONTEXT BAR
    // ============================
    if (persona === "csuite") {
      html += '<div class="persona-context-bar ctx-csuite">' +
        '\uD83D\uDC51 C-Suite Executive View — Financial impact and strategic recommendations' +
        '</div>';
    } else if (persona === "devops") {
      html += '<div class="persona-context-bar ctx-devops">' +
        '\u2699\uFE0F DevOps Engineering View — Root cause analysis, deployment logs, and system triage' +
        '</div>';
    } else if (persona === "bi") {
      html += '<div class="persona-context-bar ctx-bi">' +
        '\uD83D\uDCCA BI Analyst View — Statistical significance, model metrics, and data quality audit' +
        '</div>';
    }

    // ============================
    // DEVOPS: Terminal-style incident log
    // ============================
    if (persona === "devops") {
      var tree = (causalTree && causalTree.tree) ? causalTree.tree : {};
      var rootCause = (causalTree && causalTree.root_cause_leaf) ? causalTree.root_cause_leaf : "Unknown";
      var rootData = tree[rootCause] || {};
      var rootZ = (rootData.z_score || 0).toFixed(1);
      var rootVal = rootData.value || 0;
      var rootBase = rootData.baseline || 0;

      html += '<div class="devops-log-block">' +
        '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-crit">[CRITICAL]</span> Anomaly detector triggered for ' + rootCause.replace(/_/g, " ") + '</span>' +
        '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-warn">[TRIAGE]</span> Z-score=' + rootZ + ' | Current=' + Number(rootVal).toLocaleString() + ' | Baseline=' + Number(rootBase).toLocaleString() + '</span>' +
        '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-info">[INFO]</span> Causal decomposition: Revenue \u2192 ' + (causalTree.failing_path || []).join(" \u2192 ") + '</span>' +
        '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-info">[INFO]</span> Confidence score: ' + confPct + '% | Model: Bayesian + IsolationForest + TF-IDF RAG</span>' +
        '</div>';
    }

    // ============================
    // BI ANALYST: Statistical summary cards
    // ============================
    if (persona === "bi") {
      var tree = (causalTree && causalTree.tree) ? causalTree.tree : {};
      var revNode = tree["Revenue"] || {};
      var rootCause = (causalTree && causalTree.root_cause_leaf) ? causalTree.root_cause_leaf : "N/A";
      var rootData = tree[rootCause] || {};
      var critCount = 0;
      var warnCount = 0;
      var healthyCount = 0;
      var keys = Object.keys(tree);
      for (var i = 0; i < keys.length; i++) {
        var status = tree[keys[i]].status;
        if (status === "CRITICAL_FAIL") critCount++;
        else if (status === "WARNING") warnCount++;
        else healthyCount++;
      }

      html += '<div class="bi-stats-grid">' +
        '<div class="bi-stat-card"><div class="stat-label">Revenue Z-Score</div><div class="stat-value">' + (revNode.z_score || 0).toFixed(2) + '</div></div>' +
        '<div class="bi-stat-card"><div class="stat-label">Root Cause Node</div><div class="stat-value" style="font-size:0.85rem;">' + rootCause.replace(/_/g, " ") + '</div></div>' +
        '<div class="bi-stat-card"><div class="stat-label">Model Confidence</div><div class="stat-value">' + confPct + '%</div></div>' +
        '<div class="bi-stat-card"><div class="stat-label">Critical Nodes</div><div class="stat-value" style="color:var(--anomaly-rose);">' + critCount + '</div></div>' +
        '<div class="bi-stat-card"><div class="stat-label">Warning Nodes</div><div class="stat-value" style="color:var(--warning-amber);">' + warnCount + '</div></div>' +
        '<div class="bi-stat-card"><div class="stat-label">Healthy Nodes</div><div class="stat-value" style="color:var(--health-green);">' + healthyCount + '</div></div>' +
        '</div>';
    }

    // ============================
    // CONFIDENCE BADGE + VOICE BUTTON
    // ============================
    html += '<div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">' +
      '<span class="badge ' + (isHighConf ? "badge-blue" : "badge-amber") + '">' +
        (isHighConf ? "\uD83D\uDFE2 HIGH CONFIDENCE DIAGNOSIS" : "\u26A0\uFE0F AMBIGUOUS EVIDENCE DETECTED") + " (" + confPct + "% Score)" +
      '</span>' +
      '<button id="voice-ai-btn" class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px;">' +
        "\uD83D\uDD0A Listen to " + (persona === "devops" ? "Incident Brief" : persona === "bi" ? "Analysis Summary" : "Executive Briefing") +
      '</button>' +
    '</div>';

    // ============================
    // HEADLINE
    // ============================
    var headlinePrefix = "";
    if (persona === "devops") headlinePrefix = "\uD83D\uDEE0\uFE0F ";
    else if (persona === "bi") headlinePrefix = "\uD83D\uDD2C ";

    html += '<h3 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 8px;">' + headlinePrefix + narrativeData.headline + '</h3>';

    // ============================
    // EXECUTIVE SUMMARY (persona-adapted)
    // ============================
    html += '<p id="executive-narrative-text" style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 14px;">' +
      narrativeData.executive_summary +
    '</p>';

    // ============================
    // 4-PILLAR HONEST DETECTIVE CONSOLE
    // ============================
    var protocolLabel = "\uD83D\uDD75\uFE0F Honest Detective Safeguards Protocol";
    if (persona === "devops") protocolLabel = "\uD83D\uDD27 Incident Triage Console";
    else if (persona === "bi") protocolLabel = "\uD83D\uDCCB Data Quality & Hypothesis Audit";

    html += '<div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">' +
      protocolLabel +
    '</div>';

    // Pillar labels adapt to persona
    var knownLabel = persona === "devops" ? "\u2705 Confirmed Indicators" : persona === "bi" ? "\u2705 Statistically Significant" : "\u2705 Corroborated Facts";
    var gapLabel = persona === "devops" ? "\u26A0\uFE0F Missing Telemetry" : persona === "bi" ? "\u26A0\uFE0F Data Quality Gaps" : "\u26A0\uFE0F Telemetry Gaps";
    var ruledLabel = persona === "devops" ? "\u274C Services Cleared" : persona === "bi" ? "\u274C Hypotheses Rejected" : "\u274C Ruled Out";
    var sopLabel = persona === "devops" ? "\uD83D\uDE80 Remediation Actions" : persona === "bi" ? "\uD83E\uDDEA Recommended Experiments" : "\uD83E\uDDEA Prescribed SOP Actions";

    html += '<div class="honest-grid">' +
      '<div class="pillar-box pillar-knowns">' +
        '<h4>' + knownLabel + '</h4>' +
        '<ul>' + (hd.knowns || []).map(function(k) { return "<li>" + k + "</li>"; }).join("") + '</ul>' +
      '</div>' +
      '<div class="pillar-box pillar-gaps">' +
        '<h4>' + gapLabel + '</h4>' +
        '<ul>' + (hd.telemetry_gaps || []).map(function(g) { return "<li>" + g + "</li>"; }).join("") + '</ul>' +
      '</div>' +
      '<div class="pillar-box pillar-ruled">' +
        '<h4>' + ruledLabel + '</h4>' +
        '<ul>' + (hd.ruled_out || []).map(function(r) { return "<li>" + r + "</li>"; }).join("") + '</ul>' +
      '</div>' +
      '<div class="pillar-box pillar-sop">' +
        '<h4>' + sopLabel + '</h4>' +
        '<ul>' + (hd.prescribed_actions || []).map(function(a) { return "<li>" + a + "</li>"; }).join("") + '</ul>' +
      '</div>' +
    '</div>';

    // ============================
    // MITIGATION BUTTON (persona-adapted label)
    // ============================
    var mitigateLabel = "\uD83C\uDFAE Trigger Automated SOP Rollback";
    if (persona === "devops") mitigateLabel = "\uD83D\uDE80 Execute Hotfix Rollback & Restart Service";
    else if (persona === "bi") mitigateLabel = "\uD83D\uDCCA Run Controlled A/B Recovery Experiment";

    html += '<div style="margin-top: 14px; text-align: right;">' +
      '<button id="execute-mitigation-btn" class="btn btn-primary">' + mitigateLabel + '</button>' +
    '</div>';

    container.innerHTML = html;

    // ============================
    // EVENT LISTENERS
    // ============================

    // Voice AI Speech Synthesis
    var voiceBtn = document.getElementById("voice-ai-btn");
    if (voiceBtn) {
      voiceBtn.addEventListener("click", function() {
        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
          var utterance = new SpeechSynthesisUtterance(narrativeData.headline + ". " + narrativeData.executive_summary);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          window.speechSynthesis.speak(utterance);
          voiceBtn.innerText = "\uD83D\uDD0A Playing...";
          utterance.onend = function() {
            voiceBtn.innerText = "\uD83D\uDD0A Listen to " + (persona === "devops" ? "Incident Brief" : persona === "bi" ? "Analysis Summary" : "Executive Briefing");
          };
        } else {
          alert("Web Speech API is not supported in this browser.");
        }
      });
    }

    // Mitigation Action Trigger
    var mitBtn = document.getElementById("execute-mitigation-btn");
    if (mitBtn && onMitigateTrigger) {
      mitBtn.addEventListener("click", function() {
        mitBtn.disabled = true;
        mitBtn.innerText = "\u26A1 Executing...";
        onMitigateTrigger(scenarioId);
      });
    }
  }
};
