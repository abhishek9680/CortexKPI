window.NarrativeComponent = {
  /**
   * Renders Step 4 with persona-aware content, simple/technical toggle support,
   * and dynamic 1-Click Mitigation / Reset button.
   */
  render: function(containerId, narrativeData, scenarioId, onMitigateTrigger, persona, causalTree, mode) {
    var container = document.getElementById(containerId);
    if (!container) return;

    persona = persona || "csuite";
    mode = mode || "simple";
    var hd = narrativeData.honest_detective || {};
    var confPct = hd.confidence_pct || 55;
    var isHighConf = confPct >= 75;

    var html = "";

    // Detect positive growth surge vs anomaly vs resolved state
    var isSurge = (narrativeData.financial_loss && narrativeData.financial_loss.includes("+")) ||
                  (narrativeData.headline && narrativeData.headline.includes("surged"));
    var isResolved = narrativeData.headline.includes("surged +0.0%") || 
                     narrativeData.headline.includes("growth (+0.0%)") || 
                     !(causalTree && causalTree.root_cause_leaf);

    // ============================
    // PERSONA CONTEXT BAR
    // ============================
    if (persona === "csuite") {
      html += '<div class="persona-context-bar ctx-csuite">' +
        '👑 Executive View — Financial impact and strategic recommendations' +
        '</div>';
    } else if (persona === "devops") {
      html += '<div class="persona-context-bar ctx-devops">' +
        '⚙️ DevOps View — Root cause analysis, deployment logs, and system triage' +
        '</div>';
    } else if (persona === "bi") {
      html += '<div class="persona-context-bar ctx-bi">' +
        '📊 BI Analyst View — Statistical significance, model metrics, and hypothesis audit' +
        '</div>';
    }

    // ============================
    // TECHNICAL MODE DIAGNOSTICS (Only shown in technical mode)
    // ============================
    if (mode === "technical") {
      if (persona === "devops") {
        var tree = (causalTree && causalTree.tree) ? causalTree.tree : {};
        var rootCause = (causalTree && causalTree.root_cause_leaf) ? causalTree.root_cause_leaf : "Resolved";
        var rootData = tree[rootCause] || {};
        var rootZ = (rootData.z_score || 0).toFixed(1);
        var rootVal = rootData.value || 0;
        var rootBase = rootData.baseline || 0;

        html += '<div class="devops-log-block" style="margin-bottom:12px;">' +
          '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="' + (isSurge ? 'log-level-info' : (isResolved ? 'log-level-info' : 'log-level-crit')) + '">[' + (isSurge ? 'SURGE' : (isResolved ? 'HEALTHY' : 'CRITICAL')) + ']</span> System State: ' + (isSurge ? 'Positive Growth Surge Detected for ' + rootCause.replace(/_/g, " ") : (isResolved ? 'Baseline Healthy' : 'Anomaly Triggered for ' + rootCause.replace(/_/g, " "))) + '</span>' +
          '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-warn">[TRIAGE]</span> Z-score=' + rootZ + ' | Current=' + Number(rootVal).toLocaleString() + ' | Baseline=' + Number(rootBase).toLocaleString() + '</span>' +
          '<span class="log-line"><span class="log-ts">[' + new Date().toISOString().slice(0, 19) + ']</span> <span class="log-level-info">[INFO]</span> Causal path: Revenue → ' + (causalTree.failing_path || []).join(" → ") + '</span>' +
          '</div>';
      } else if (persona === "bi") {
        var tree = (causalTree && causalTree.tree) ? causalTree.tree : {};
        var revNode = tree["Revenue"] || {};
        var rootCause = (causalTree && causalTree.root_cause_leaf) ? causalTree.root_cause_leaf : "None";
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

        html += '<div class="bi-stats-grid" style="margin-bottom:12px;">' +
          '<div class="bi-stat-card"><div class="stat-label">Revenue Z-Score</div><div class="stat-value">' + (revNode.z_score || 0).toFixed(2) + '</div></div>' +
          '<div class="bi-stat-card"><div class="stat-label">Root Cause Node</div><div class="stat-value" style="font-size:0.85rem;">' + rootCause.replace(/_/g, " ") + '</div></div>' +
          '<div class="bi-stat-card"><div class="stat-label">Model Confidence</div><div class="stat-value">' + confPct + '%</div></div>' +
          '<div class="bi-stat-card"><div class="stat-label">Critical Nodes</div><div class="stat-value" style="color:var(--anomaly-rose);">' + critCount + '</div></div>' +
          '<div class="bi-stat-card"><div class="stat-label">Warning Nodes</div><div class="stat-value" style="color:var(--warning-amber);">' + warnCount + '</div></div>' +
          '<div class="bi-stat-card"><div class="stat-label">Healthy Nodes</div><div class="stat-value" style="color:var(--health-green);">' + healthyCount + '</div></div>' +
          '</div>';
      }
    }

    // ============================
    // CONFIDENCE BADGE + VOICE BUTTON
    // ============================
    html += '<div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">' +
      '<span class="badge ' + (isHighConf ? "badge-blue" : "badge-amber") + '">' +
        (isHighConf ? "🟢 HIGH CONFIDENCE DIAGNOSIS" : "⚠️ AMBIGUOUS / MONITORING") + " (" + confPct + "% Confidence)" +
      '</span>' +
      '<button id="voice-ai-btn" class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px;">' +
        "🔊 Read Aloud" +
      '</button>' +
    '</div>';

    // ============================
    // HEADLINE & EXECUTIVE SUMMARY
    // ============================
    html += '<h3 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 8px; color: #f8fafc;">' + narrativeData.headline + '</h3>';

    html += '<p id="executive-narrative-text" style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 14px;">' +
      narrativeData.executive_summary +
    '</p>';

    // ============================
    // 4-PILLAR HONEST DETECTIVE CONSOLE
    // ============================
    var knownLabel = persona === "devops" ? "✅ Confirmed Indicators" : persona === "bi" ? "✅ Statistically Significant" : "✅ Corroborated Facts";
    var gapLabel = persona === "devops" ? "⚠️ Missing Telemetry" : persona === "bi" ? "⚠️ Data Quality Gaps" : "⚠️ Telemetry Gaps";
    var ruledLabel = persona === "devops" ? "❌ Services Cleared" : persona === "bi" ? "❌ Hypotheses Rejected" : "❌ Ruled Out";
    var sopLabel = persona === "devops" ? "🚀 Remediation Actions" : persona === "bi" ? "🧪 Recommended Experiments" : "🧪 Prescribed SOP Actions";

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
    // 1-CLICK MITIGATION / RESET ACTION BUTTON
    // ============================
    var actionType = isResolved ? "REINJECT_ANOMALY" : "ROLLBACK_DEPLOYMENT";
    var buttonHtml = "";

    if (isSurge) {
      // Positive growth surge — show capitalize/scale button instead of rollback
      var surgeLabel = "📈 Capitalize on Growth Surge — Scale Infrastructure";
      if (persona === "devops") surgeLabel = "⚡ Auto-Scale Capacity to Handle Traffic Surge";
      else if (persona === "bi") surgeLabel = "📊 Run Attribution Analysis on Growth Drivers";

      buttonHtml = '<button id="execute-mitigation-btn" class="btn btn-outline" data-action="REINJECT_ANOMALY" style="border-color: var(--health-green); color: var(--health-green); font-weight: 700; background: rgba(16, 185, 129, 0.1);">' +
        surgeLabel +
      '</button>';
    } else if (isResolved) {
      buttonHtml = '<button id="execute-mitigation-btn" class="btn btn-outline" data-action="REINJECT_ANOMALY" style="border-color: var(--warning-amber); color: var(--warning-amber); font-weight: 700; background: rgba(245, 158, 11, 0.1);">' +
        '↺ Reset Outage State (Re-Inject Anomaly)' +
      '</button>';
    } else {
      var mitigateLabel = "🎮 1-Click Automated SOP Rollback";
      if (persona === "devops") mitigateLabel = "🚀 Execute Hotfix Rollback & Restart Service";
      else if (persona === "bi") mitigateLabel = "📊 Run Controlled A/B Recovery Experiment";

      buttonHtml = '<button id="execute-mitigation-btn" class="btn btn-primary" data-action="ROLLBACK_DEPLOYMENT" style="font-weight: 700; font-size: 0.9rem; padding: 10px 18px;">' +
        mitigateLabel +
      '</button>';
    }

    html += '<div style="margin-top: 16px; display: flex; justify-content: flex-end;">' + buttonHtml + '</div>';

    container.innerHTML = html;

    // ============================
    // EVENT LISTENERS
    // ============================

    // Voice AI Speech Synthesis
    var voiceBtn = document.getElementById("voice-ai-btn");
    if (voiceBtn) {
      voiceBtn.addEventListener("click", function() {
        if (!window.speechSynthesis) {
          alert("Web Speech API is not supported in this browser.");
          return;
        }

        if (window.speechSynthesis.speaking) {
          window.speechSynthesis.cancel();
          voiceBtn.innerText = "🔊 Read Aloud";
          return;
        }

        var textToSpeak = (narrativeData.headline || "") + ". " + (narrativeData.executive_summary || "");
        var utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = function() {
          voiceBtn.innerText = "⏹ Stop Speech";
        };
        utterance.onend = function() {
          voiceBtn.innerText = "🔊 Read Aloud";
        };
        utterance.onerror = function() {
          voiceBtn.innerText = "🔊 Read Aloud";
        };

        window.speechSynthesis.speak(utterance);
      });
    }

    // Dynamic Mitigation / Reset Action Button
    var mitBtn = document.getElementById("execute-mitigation-btn");
    if (mitBtn && onMitigateTrigger) {
      mitBtn.addEventListener("click", function() {
        var action = mitBtn.getAttribute("data-action");
        onMitigateTrigger(scenarioId, action);
      });
    }
  }
};
