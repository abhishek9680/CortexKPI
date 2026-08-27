window.NarrativeComponent = {
  render: function(containerId, narrativeData, scenarioId, onMitigateTrigger) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const hd = narrativeData.honest_detective || {};
    const confPct = hd.confidence_pct || 96;
    const isHighConf = confPct >= 80;

    let html = `
      <div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
        <span class="badge ${isHighConf ? 'badge-blue' : 'badge-amber'}">
          ${isHighConf ? '🟢 HIGH CONFIDENCE DIAGNOSIS' : '⚠️ AMBIGUOUS EVIDENCE DETECTED'} (${confPct}% Score)
        </span>
        <button id="voice-ai-btn" class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px;">
          🔊 Listen to Executive Briefing
        </button>
      </div>

      <h3 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 8px;">${narrativeData.headline}</h3>
      
      <p id="executive-narrative-text" style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 14px;">
        ${narrativeData.executive_summary}
      </p>

      <!-- 4-Pillar Honest Detective Console -->
      <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px;">
        🕵️ Honest Detective Safeguards Protocol
      </div>

      <div class="honest-grid">
        <div class="pillar-box pillar-knowns">
          <h4>✅ Corroborated Facts</h4>
          <ul>
            ${(hd.knowns || []).map(k => `<li>${k}</li>`).join('')}
          </ul>
        </div>

        <div class="pillar-box pillar-gaps">
          <h4>⚠️ Telemetry Gaps</h4>
          <ul>
            ${(hd.telemetry_gaps || []).map(g => `<li>${g}</li>`).join('')}
          </ul>
        </div>

        <div class="pillar-box pillar-ruled">
          <h4>❌ Ruled Out</h4>
          <ul>
            ${(hd.ruled_out || []).map(r => `<li>${r}</li>`).join('')}
          </ul>
        </div>

        <div class="pillar-box pillar-sop">
          <h4>🧪 Prescribed SOP Actions</h4>
          <ul>
            ${(hd.prescribed_actions || []).map(a => `<li>${a}</li>`).join('')}
          </ul>
        </div>
      </div>

      <!-- Automated Mitigation Trigger Button -->
      <div style="margin-top: 14px; text-align: right;">
        <button id="execute-mitigation-btn" class="btn btn-primary">
          🎮 Trigger Automated SOP Rollback
        </button>
      </div>
    `;

    container.innerHTML = html;

    // Attach Voice AI Speech Synthesis
    const voiceBtn = document.getElementById("voice-ai-btn");
    if (voiceBtn) {
      voiceBtn.addEventListener("click", () => {
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(`${narrativeData.headline}. ${narrativeData.executive_summary}`);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          window.speechSynthesis.speak(utterance);
          voiceBtn.innerText = "🔊 Playing Briefing...";
          utterance.onend = () => { voiceBtn.innerText = "🔊 Listen to Executive Briefing"; };
        } else {
          alert("Web Speech API is not supported in this browser.");
        }
      });
    }

    // Attach Mitigation Action Trigger
    const mitBtn = document.getElementById("execute-mitigation-btn");
    if (mitBtn && onMitigateTrigger) {
      mitBtn.addEventListener("click", () => {
        mitBtn.disabled = true;
        mitBtn.innerText = "⚡ Executing Automated Rollback...";
        onMitigateTrigger(scenarioId);
      });
    }
  }
};
