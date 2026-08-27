window.PDFExportComponent = {
  exportReport: function(currentData) {
    if (!currentData) return;

    const printWindow = window.open('', '_blank');
    const narrative = currentData.layer_4_narrative || {};
    const hd = narrative.honest_detective || {};
    const peakDate = currentData.peak_date || '2026-08-25';

    const reportHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>CortexKPI Executive Incident Briefing - ${peakDate}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 40px; color: #111; line-height: 1.6; }
          h1 { color: #1D4ED8; border-bottom: 2px solid #1D4ED8; padding-bottom: 8px; }
          .header-table { width: 100%; margin-bottom: 20px; border-collapse: collapse; }
          .header-table td { padding: 8px; border-bottom: 1px solid #ddd; }
          .box { background: #f8fafc; border: 1px solid #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
          .badge { background: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
          ul { padding-left: 20px; }
        </style>
      </head>
      <body>
        <h1>🧠 CortexKPI Executive Incident Briefing</h1>
        
        <table class="header-table">
          <tr>
            <td><strong>Incident Date:</strong> ${peakDate}</td>
            <td><strong>Severity:</strong> <span class="badge">CRITICAL ANOMALY BREACH</span></td>
          </tr>
          <tr>
            <td><strong>Financial Loss Impact:</strong> ${narrative.financial_loss}</td>
            <td><strong>Honest Detective Confidence:</strong> ${hd.confidence_pct}%</td>
          </tr>
        </table>

        <div class="box">
          <h3>${narrative.headline}</h3>
          <p>${narrative.executive_summary}</p>
        </div>

        <h3>🕵️ Honest Detective 4-Pillar Safeguards</h3>
        
        <div class="box">
          <h4>✅ Corroborated Facts</h4>
          <ul>${(hd.knowns || []).map(k => `<li>${k}</li>`).join('')}</ul>

          <h4>⚠️ Telemetry Gaps</h4>
          <ul>${(hd.telemetry_gaps || []).map(g => `<li>${g}</li>`).join('')}</ul>

          <h4>❌ Ruled Out Alternate Hypotheses</h4>
          <ul>${(hd.ruled_out || []).map(r => `<li>${r}</li>`).join('')}</ul>

          <h4>🧪 Prescribed SOP Actions</h4>
          <ul>${(hd.prescribed_actions || []).map(a => `<li>${a}</li>`).join('')}</ul>
        </div>

        <p style="font-size: 0.8rem; color: #666; margin-top: 40px;">
          Generated automatically by CortexKPI Autonomous Engine • Accenture Innovation Challenge 2026
        </p>
      </body>
      </html>
    `;

    printWindow.document.write(reportHtml);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 500);
  }
};
