window.TreeComponent = {
  render: function(containerId, causalData, onWhatIfChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    this.currentCausalData = JSON.parse(JSON.stringify(causalData));
    this.containerId = containerId;
    this.onWhatIfChange = onWhatIfChange;
    this._debounceTimer = null;
    this._currentSliderValue = null;

    // Create two separate DOM areas so slider survives SVG updates
    container.innerHTML = '<div id="tree-svg-area"></div><div id="tree-slider-area"></div>';

    this._renderSVGTree();
    this._renderSlider();
  },

  /**
   * Determines appropriate slider min/max/step/formatting based on which
   * metric node is the root cause. Prevents the bug where Sessions (106,163)
   * was displayed as "106163%" because the slider assumed all values are percentages.
   */
  _getSliderConfig: function(nodeKey, nodeData) {
    const baseline = parseFloat(nodeData.baseline) || parseFloat(nodeData.value) || 100;
    const currentValue = parseFloat(nodeData.value) || baseline;
    const range = Math.max(baseline, currentValue);

    if (nodeKey === 'Sessions') {
      return {
        min: 0,
        max: Math.round(range * 1.5),
        step: Math.max(1, Math.round(range / 500)),
        formatValue: function(v) { return Number(Math.round(v)).toLocaleString() + ' sessions'; },
        label: 'Sessions (Traffic)'
      };
    } else if (nodeKey === 'AOV') {
      return {
        min: 0,
        max: Math.round(Math.max(baseline, currentValue) * 2.5),
        step: 1,
        formatValue: function(v) { return '$' + Number(v).toFixed(2); },
        label: 'Average Order Value'
      };
    } else if (nodeKey === 'Revenue') {
      return {
        min: 0,
        max: Math.round(range * 2),
        step: Math.max(100, Math.round(range / 500)),
        formatValue: function(v) { return '$' + Number(Math.round(v)).toLocaleString(); },
        label: 'Revenue'
      };
    } else if (nodeKey === 'Conversion_Rate') {
      return {
        min: 0,
        max: 10,
        step: 0.01,
        formatValue: function(v) { return Number(v).toFixed(2) + '%'; },
        label: 'Conversion Rate'
      };
    } else {
      // Payment_Success_Rate or any other percentage metric
      return {
        min: 0,
        max: 100,
        step: 0.5,
        formatValue: function(v) { return Number(v).toFixed(1) + '%'; },
        label: 'Payment Success Rate'
      };
    }
  },

  /**
   * Renders ONLY the SVG tree visualization (nodes + edges).
   * Called separately from the slider so that What-If API responses
   * can update node values without destroying the slider mid-drag.
   */
  _renderSVGTree: function() {
    const svgArea = document.getElementById('tree-svg-area');
    if (!svgArea) return;

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

    let svgHtml = '<svg width="100%" height="320" viewBox="0 0 520 320" xmlns="http://www.w3.org/2000/svg">';

    // Draw Edges with animated glow for failing paths
    edges.forEach(function(edge) {
      const fromPos = nodes[edge.from];
      const toPos = nodes[edge.to];
      const isFailing = failingPath.includes(edge.from) && failingPath.includes(edge.to);
      const strokeColor = isFailing ? '#EF4444' : '#10B981';
      const strokeWidth = isFailing ? 3 : 1.5;
      const strokeDash = isFailing ? 'stroke-dasharray="6"' : '';

      svgHtml += '<line x1="' + fromPos.x + '" y1="' + (fromPos.y + 35) + '" x2="' + toPos.x + '" y2="' + (toPos.y - 5) + '" ' +
        'stroke="' + strokeColor + '" stroke-width="' + strokeWidth + '" ' + strokeDash + ' />';
    });

    // Draw Card Nodes with proper value formatting per metric type
    var nodeKeys = Object.keys(nodes);
    for (var i = 0; i < nodeKeys.length; i++) {
      var key = nodeKeys[i];
      var pos = nodes[key];
      var nData = tree[key] || { name: key, label: key, value: 0, delta_pct: 0, z_score: 0, status: 'HEALTHY' };

      var isCritical = nData.status === 'CRITICAL_FAIL';
      var isWarning = nData.status === 'WARNING';
      var borderColor = isCritical ? '#EF4444' : (isWarning ? '#F59E0B' : '#10B981');
      var statusDot = isCritical ? '#EF4444' : (isWarning ? '#F59E0B' : '#10B981');

      // Format display value based on metric type (not hardcoded %)
      var formattedValue;
      if (key === 'Revenue') {
        formattedValue = '$' + Number(nData.value).toLocaleString(undefined, {maximumFractionDigits: 2});
      } else if (key === 'AOV') {
        formattedValue = '$' + Number(nData.value).toFixed(2);
      } else if (key === 'Payment_Success_Rate' || key === 'Conversion_Rate') {
        formattedValue = Number(nData.value).toFixed(2) + '%';
      } else if (key === 'Sessions') {
        formattedValue = Number(Math.round(nData.value)).toLocaleString();
      } else {
        formattedValue = Number(nData.value).toLocaleString();
      }

      var displayLabel = nData.label ? nData.label.split('(')[0].trim() : key.replace(/_/g, ' ');
      var deltaColor = nData.delta_pct < 0 ? '#EF4444' : '#10B981';
      var deltaSign = nData.delta_pct >= 0 ? '+' : '';
      var zVal = nData.z_score ? Number(nData.z_score).toFixed(1) : '0.0';

      svgHtml += '<g transform="translate(' + (pos.x - 70) + ', ' + (pos.y - 10) + ')">' +
        '<rect width="140" height="65" rx="8" ry="8" fill="rgba(17, 24, 39, 0.95)" stroke="' + borderColor + '" stroke-width="' + (isCritical ? 2.5 : 1.5) + '" />' +
        '<text x="10" y="18" fill="#F9FAFB" font-size="10.5" font-family="Inter, sans-serif" font-weight="700">' + displayLabel + '</text>' +
        '<circle cx="127" cy="14" r="5" fill="' + statusDot + '" />' +
        '<text x="10" y="38" fill="#FFFFFF" font-size="12" font-family="JetBrains Mono, monospace" font-weight="700">' + formattedValue + '</text>' +
        '<text x="10" y="54" fill="' + deltaColor + '" font-size="9.5" font-family="JetBrains Mono, monospace" font-weight="600">' +
          deltaSign + nData.delta_pct + '% (Z: ' + zVal + ')' +
        '</text>' +
        '</g>';
    }

    svgHtml += '</svg>';
    svgArea.innerHTML = svgHtml;
  },

  /**
   * Renders the What-If slider with dynamic range based on the root cause metric type.
   * Only called on initial render, NOT on API response updates.
   */
  _renderSlider: function() {
    const sliderArea = document.getElementById('tree-slider-area');
    if (!sliderArea) return;

    const tree = this.currentCausalData.tree || {};
    const rootLeaf = this.currentCausalData.root_cause_leaf || "Payment_Success_Rate";
    const leafData = tree[rootLeaf] || { value: 50, baseline: 100 };
    const config = this._getSliderConfig(rootLeaf, leafData);

    // Use stored slider value if available, otherwise use the node's current value
    const sliderVal = this._currentSliderValue !== null ? this._currentSliderValue : leafData.value;
    const displayVal = config.formatValue(sliderVal);
    const displayName = rootLeaf.replace(/_/g, ' ');

    sliderArea.innerHTML =
      '<div class="simulator-box">' +
        '<label>' +
          '<span>\u26A1 Interactive "What-If" Counterfactual Simulator</span>' +
          '<span id="simulator-val-label" class="impact-value" style="font-size: 0.95rem;">' + displayVal + '</span>' +
        '</label>' +
        '<input type="range" min="' + config.min + '" max="' + config.max + '" value="' + sliderVal + '" step="' + config.step + '" class="slider-input" id="whatif-slider">' +
        '<p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 6px;">' +
          'Adjust <strong>' + displayName + '</strong> to simulate instant parent node revenue graph recovery.' +
        '</p>' +
      '</div>';

    // Store config for use in event handler
    this._currentConfig = config;
    this._currentRootLeaf = rootLeaf;

    const self = this;
    const slider = document.getElementById("whatif-slider");
    if (slider) {
      slider.addEventListener("input", function(e) {
        const val = parseFloat(e.target.value);
        self._currentSliderValue = val;

        // Update label instantly for responsive feel
        const label = document.getElementById("simulator-val-label");
        if (label) {
          label.innerText = self._currentConfig.formatValue(val);
        }

        // Debounce API calls to avoid hammering the server during fast drags
        if (self._debounceTimer) clearTimeout(self._debounceTimer);
        self._debounceTimer = setTimeout(function() {
          if (self.onWhatIfChange) {
            self.onWhatIfChange(self._currentRootLeaf, val);
          }
        }, 200);
      });
    }
  },

  /**
   * Called by app.js when the What-If API responds.
   * ONLY updates the SVG tree nodes — does NOT recreate the slider.
   * This prevents the slider from being destroyed while the user is dragging.
   */
  updateNodeValues: function(updatedTreeData) {
    if (!updatedTreeData || !updatedTreeData.tree) return;
    this.currentCausalData = updatedTreeData;

    // Only re-render the SVG cards and edges — slider stays intact
    this._renderSVGTree();
  }
};
