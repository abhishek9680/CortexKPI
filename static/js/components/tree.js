window.TreeComponent = {
  render: function(containerId, causalData, onWhatIfChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    this.currentCausalData = JSON.parse(JSON.stringify(causalData));
    this.containerId = containerId;
    this.onWhatIfChange = onWhatIfChange;

    this._drawSVG(container);
  },

  _drawSVG: function(container) {
    const tree = this.currentCausalData.tree || {};
    const failingPath = this.currentCausalData.failing_path || [];

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
      const strokeColor = isFailing ? '#EF4444' : '#10B981';
      const strokeWidth = isFailing ? 3 : 1.5;
      const strokeDash = isFailing ? 'stroke-dasharray="6"' : '';

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
      const statusIcon = isCritical ? '🔴' : (isWarning ? '🟡' : '🟢');

      svgHtml += `
        <g transform="translate(${pos.x - 70}, ${pos.y - 10})">
          <rect width="140" height="65" rx="8" ry="8" fill="rgba(17, 24, 39, 0.95)" stroke="${borderColor}" stroke-width="${isCritical ? 2 : 1.5}" />
          <text x="10" y="18" fill="#F9FAFB" font-size="10.5" font-family="Inter" font-weight="700">${nData.label ? nData.label.split(' ')[0] : key}</text>
          <text x="125" y="18" font-size="10" text-anchor="end">${statusIcon}</text>
          <text x="10" y="38" fill="#FFFFFF" font-size="12" font-family="JetBrains Mono" font-weight="700">
            ${nData.unit === 'USD' || key === 'Revenue' || key === 'AOV' ? '$' : ''}${Number(nData.value).toLocaleString()}${nData.unit === '%' || key.includes('Rate') ? '%' : ''}
          </text>
          <text x="10" y="54" fill="${nData.delta_pct < 0 ? '#EF4444' : '#10B981'}" font-size="9.5" font-family="JetBrains Mono" font-weight="600">
            ${nData.delta_pct >= 0 ? '+' : ''}${nData.delta_pct}% (Z: ${nData.z_score ? nData.z_score.toFixed(1) : 0})
          </text>
        </g>
      `;
    });

    svgHtml += `</svg>`;

    const rootLeaf = this.currentCausalData.root_cause_leaf || "Payment_Success_Rate";
    const leafVal = tree[rootLeaf] ? tree[rootLeaf].value : 54.2;

    const simulatorHtml = `
      <div class="simulator-box">
        <label>
          <span>⚡ Interactive "What-If" Counterfactual Simulator</span>
          <span id="simulator-val-label" class="impact-value" style="font-size: 0.95rem;">${leafVal}%</span>
        </label>
        <input type="range" min="10" max="100" value="${leafVal}" step="1" class="slider-input" id="whatif-slider">
        <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 6px;">
          Drag <strong>${rootLeaf}</strong> slider to dynamically simulate real-time parent graph recovery.
        </p>
      </div>
    `;

    container.innerHTML = svgHtml + simulatorHtml;

    const slider = document.getElementById("whatif-slider");
    if (slider) {
      slider.addEventListener("input", (e) => {
        const val = parseFloat(e.target.value);
        document.getElementById("simulator-val-label").innerText = val + "%";
        if (this.onWhatIfChange) this.onWhatIfChange(rootLeaf, val);
      });
    }
  },

  updateNodeValues: function(updatedTreeData) {
    if (!updatedTreeData || !updatedTreeData.tree) return;
    this.currentCausalData = updatedTreeData;
    const container = document.getElementById(this.containerId);
    if (container) {
      this._drawSVG(container);
    }
  }
};
