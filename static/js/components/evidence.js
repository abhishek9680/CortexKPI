window.EvidenceComponent = {
  render: function(containerId, evidenceItems) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!evidenceItems || evidenceItems.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem;">No corroborating evidence matched.</p>`;
      return;
    }

    let html = `<div class="evidence-list">`;

    evidenceItems.forEach(item => {
      html += `
        <div class="evidence-item" style="border-left: 3px solid ${item.color};">
          <div class="evidence-header">
            <span class="badge" style="background: rgba(255,255,255,0.05); color: ${item.color};">
              ${item.source} • ${item.badge}
            </span>
            <span class="evidence-match">${item.relevance_pct}% MATCH</span>
          </div>
          <div class="evidence-title" style="margin-top: 4px;">${item.id}: ${item.title}</div>
          <div class="evidence-details" style="margin-top: 4px;">${item.details}</div>
          <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 6px;">Timestamp: ${item.timestamp}</div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  }
};
