window.TreeComponent = {
  render: function(containerId, causalData, onWhatIfChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const tree = causalData.tree || {};
    const failingPath = causalData.failing_path || [];

    // SVG Node Coordinates
    const nodes = {
      Revenue: { x: 260, y: 40 },
      Sessions: { x: 90, y: 150 },
      Conversion_Rate: { x: 260, y: 150 },
      AOV: { x: 430, y: 150 },
      Payment_Success_Rate: { x: 260, y: 260 }
    };

    const edges = [
      { from: 'Revenue', to: 'Sessions' },
      { from: 'Revenue', to: 'Conversion_Rate' },
      { from: 'Revenue', to: 'AOV' },
      { from: 'Conversion_Rate', to: 'Payment_Success_Rate' }
    ];

    let svgHtml = `<svg width="100%" height="320" viewBox="0 0 520 320" xmlns="http://www.w3.org/2000/svg">`;

    // Draw Edges
    edges.forEach(edge => {
      const fromPos = nodes[edge.from];
      const toPos = nodes[edge.to];
      const isFailing = failingPath.includes(edge.from) && failingPath.includes(edge.to);
      const strokeColor = isFailing ? '#EF4444' : 'rgba(255, 255, 255, 0.15)';
      const strokeWidth = isFailing ? 3 : 1.5;
      const strokeDash = isFailing ? 'stroke-dasharray="6" animation="pulse 1.5s infinite"' : '';

      svgHtml += `<line x1="${fromPos.x}" y1="${fromPos.y + 35}" x2="${toPos.x}" y2="${toPos.y - 5}" 
        stroke="${strokeColor}" stroke-width="${strokeWidth}" ${strokeDash} />`;
    });

    // Draw Card Nodes
    Object.keys(nodes).forEach(key => {
      const pos = nodes[key];
      const nData = tree[key] || { name: key, label: key, value: 0, delta_pct: 0, z_score: 0, status: 'HEALTHY' };
      
      const isCritical = nData.status === 'CRITICAL_FAIL';
      const isWarning = nData.status === 'WARNING';
      const borderColor = isCritical ? '#EF4444' : (isWarning ? '#F59E0B' : '#10B981');
      const badgeBg = isCritical ? 'rgba(239,68,68,0.2)' : (isWarning ? 'rgba(245,158,11,0.2)' : 'rgba(16,185,129,0.2)');
      const statusIcon = isCritical ? '🔴' : (isWarning ? '🟡' : '🟢');

      svgHtml += `
        <g transform="translate(${pos.x - 70}, ${pos.y - 10})">
          <!-- Card Container -->
          <rect width="140" height="65" rx="8" ry="8" fill="rgba(17, 24, 39, 0.9)" stroke="${borderColor}" stroke-width="${isCritical ? 2 : 1}" />
          
          <!-- Node Label -->
          <text x="10" y="18" fill="#F9FAFB" font-size="10.5" font-family="Inter" font-weight="700">${nData.label.split(' ')[0]}</text>
          
          <!-- Status Badge -->
          <text x="125" y="18" font-size="10" text-anchor="end">${statusIcon}</text>
          
          <!-- Value & Delta -->
          <text x="10" y="38" fill="#FFFFFF" font-size="12" font-family="JetBrains Mono" font-weight="700">
            ${nData.unit === 'USD' ? '$' : ''}${Number(nData.value).toLocaleString()}${nData.unit === '%' ? '%' : ''}
          </text>
          
          <text x="10" y="54" fill="${nData.delta_pct < 0 ? '#EF4444' : '#10B981'}" font-size="9.5" font-family="JetBrains Mono" font-weight="600">
            ${nData.delta_pct >= 0 ? '+' : ''}${nData.delta_pct}% (Z: ${nData.z_score.toFixed(1)})
          </text>
        </g>
      `;
    });

    svgHtml += `</svg>`;

    // What-If Simulator HTML Controls
    const rootLeaf = causalData.root_cause_leaf || "Payment_Success_Rate";
    const leafVal = tree[rootLeaf] ? tree[rootLeaf].value : 54.2;

    const simulatorHtml = `
      <div class="simulator-box">
        <label>
          <span>⚡ Interactive "What-If" Counterfactual Simulator</span>
          <span id="simulator-val-label" class="impact-value" style="font-size: 0.95rem;">${leafVal}%</span>
        </label>
        <input type="range" min="10" max="100" value="${leafVal}" step="1" class="slider-input" id="whatif-slider">
        <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 6px;">
          Adjust <strong>${rootLeaf}</strong> to simulate instant parent node revenue graph recovery.
        </p>
      </div>
    `;

    container.innerHTML = svgHtml + simulatorHtml;

    // Attach slider event listener
    const slider = document.getElementById("whatif-slider");
    if (slider) {
      slider.addEventListener("input", (e) => {
        const val = parseFloat(e.target.value);
        document.getElementById("simulator-val-label").innerText = val + "%";
        if (onWhatIfChange) onWhatIfChange(rootLeaf, val);
      });
    }
  }
};
