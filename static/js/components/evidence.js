window.EvidenceComponent = {
  /**
   * Renders Layer 3 evidence cards with persona-aware formatting.
   * @param {string} persona - 'csuite', 'devops', or 'bi'
   */
  render: function(containerId, evidenceItems, persona) {
    var container = document.getElementById(containerId);
    if (!container) return;

    persona = persona || "csuite";

    if (!evidenceItems || evidenceItems.length === 0) {
      container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">No corroborating evidence matched.</p>';
      return;
    }

    var html = "";

    // Persona context header
    if (persona === "csuite") {
      html += '<div class="persona-context-bar ctx-csuite">' +
        '\uD83D\uDCC4 Top correlated business events ranked by AI relevance score' +
      '</div>';
    } else if (persona === "devops") {
      html += '<div class="persona-context-bar ctx-devops">' +
        '\uD83D\uDD0D Deployment artifacts, monitoring alerts, and support tickets correlated via TF-IDF NLP matching' +
      '</div>';
    } else if (persona === "bi") {
      html += '<div class="persona-context-bar ctx-bi">' +
        '\uD83E\uDDE0 Evidence ranked by cosine similarity score from TF-IDF vectorized corpus (top-k retrieval)' +
      '</div>';
    }

    html += '<div class="evidence-list">';

    for (var i = 0; i < evidenceItems.length; i++) {
      var item = evidenceItems[i];

      html += '<div class="evidence-item" style="border-left: 3px solid ' + item.color + ';">';

      // Header with source badge and match score
      html += '<div class="evidence-header">' +
        '<span class="badge" style="background: rgba(255,255,255,0.05); color: ' + item.color + ';">' +
          item.source + ' \u2022 ' + item.badge +
        '</span>';

      if (persona === "bi") {
        // BI: Show exact cosine similarity score
        html += '<span class="evidence-match" style="color: var(--accent-purple);">' +
          'cos\u03B8=' + (item.relevance_score || 0.5).toFixed(3) + ' (' + item.relevance_pct + '%)' +
        '</span>';
      } else {
        html += '<span class="evidence-match">' + item.relevance_pct + '% MATCH</span>';
      }

      html += '</div>';

      // Title
      html += '<div class="evidence-title" style="margin-top: 4px;">' + item.id + ': ' + item.title + '</div>';

      // Details — persona-specific formatting
      if (persona === "devops") {
        // DevOps: Show details in monospace terminal style
        html += '<div style="margin-top: 6px; padding: 6px 8px; background: rgba(0,0,0,0.3); border-radius: 4px; ' +
          'font-family: var(--font-mono); font-size: 0.72rem; color: var(--health-green); max-height: 60px; overflow-y: auto;">' +
          item.details +
        '</div>';
      } else if (persona === "bi") {
        // BI: Show truncated details with source metadata
        var truncDetails = item.details.length > 150 ? item.details.substring(0, 150) + "..." : item.details;
        html += '<div class="evidence-details" style="margin-top: 4px;">' + truncDetails + '</div>' +
          '<div style="font-size: 0.68rem; color: var(--accent-purple); margin-top: 4px; font-family: var(--font-mono);">' +
            'Vector Source: ' + item.source + ' | Similarity Rank: #' + (i + 1) + ' | Score: ' + (item.relevance_score || 0.5).toFixed(4) +
          '</div>';
      } else {
        // C-Suite: Show clean summary
        var truncDetails = item.details.length > 200 ? item.details.substring(0, 200) + "..." : item.details;
        html += '<div class="evidence-details" style="margin-top: 4px;">' + truncDetails + '</div>';
      }

      // Timestamp
      html += '<div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 6px;">Timestamp: ' + item.timestamp + '</div>';
      html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
  }
};
