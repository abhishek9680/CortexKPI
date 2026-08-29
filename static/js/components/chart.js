window.ChartComponent = {
  chartInstance: null,
  timeseriesData: null,

  render: function(canvasId, timeseriesData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    this.timeseriesData = JSON.parse(JSON.stringify(timeseriesData));

    const labels = timeseriesData.map(d => d.timestamp);
    const actualValues = timeseriesData.map(d => d.value);
    const baselineMeans = timeseriesData.map(d => d.rolling_mean);
    const lowerBounds = timeseriesData.map(d => d.lower_bound);
    const upperBounds = timeseriesData.map(d => d.upper_bound);

    // Anomaly points (|Z| > 2.0)
    const anomalyPoints = timeseriesData.map(d => (d.status === 'ANOMALY_BREACH' || Math.abs(d.z_score) > 2.0) ? d.value : null);

    // Initial counterfactual projection (null everywhere)
    const counterfactualData = new Array(timeseriesData.length).fill(null);

    this.chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Actual Metric',
            data: actualValues,
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2.5,
            tension: 0.2,
            pointRadius: 1
          },
          {
            label: 'Bayesian 28-Day Baseline',
            data: baselineMeans,
            borderColor: 'rgba(255, 255, 255, 0.5)',
            borderWidth: 1.5,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false
          },
          {
            label: '95% Upper Bound',
            data: upperBounds,
            borderColor: 'transparent',
            pointRadius: 0,
            fill: false
          },
          {
            label: '95% Confidence Band',
            data: lowerBounds,
            borderColor: 'transparent',
            backgroundColor: 'rgba(59, 130, 246, 0.12)',
            fill: '-1',
            pointRadius: 0
          },
          {
            label: '🔴 Anomaly Breach (|Z| > 2.0)',
            data: anomalyPoints,
            borderColor: '#EF4444',
            backgroundColor: '#EF4444',
            pointRadius: 6,
            pointHoverRadius: 8,
            showLine: false
          },
          {
            label: '⚡ What-If Counterfactual Projection',
            data: counterfactualData,
            borderColor: '#F59E0B',
            backgroundColor: 'rgba(245, 158, 11, 0.2)',
            borderWidth: 3,
            borderDash: [4, 4],
            pointRadius: 6,
            pointBackgroundColor: '#F59E0B',
            pointBorderColor: '#FFFFFF',
            pointBorderWidth: 2,
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#9CA3AF', font: { family: 'Inter', size: 11 } }
          },
          tooltip: {
            backgroundColor: 'rgba(17, 24, 39, 0.95)',
            titleColor: '#F9FAFB',
            bodyColor: '#D1D5DB',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            callbacks: {
              label: function(context) {
                const idx = context.dataIndex;
                const point = timeseriesData[idx] || {};
                const zVal = point.z_score ? point.z_score.toFixed(2) : '0.00';
                return `${context.dataset.label}: ${Number(context.raw).toLocaleString()} (Z: ${zVal})`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#6B7280', font: { size: 10 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#6B7280', font: { size: 10 } }
          }
        }
      }
    });
  },

  /**
   * Dynamically updates the Layer 1 line graph in real-time when the Layer 2 slider moves.
   * Shows a yellow dashed counterfactual trajectory on the graph.
   */
  updateSimulatedPoint: function(simulatedRevenue) {
    if (!this.chartInstance || !this.timeseriesData) return;

    const len = this.timeseriesData.length;
    if (len < 2) return;

    // 1. Update actual values dataset last point
    this.chartInstance.data.datasets[0].data[len - 1] = simulatedRevenue;

    // 2. Update simulated projection dataset (dataset 5)
    if (this.chartInstance.data.datasets[5]) {
      const projData = new Array(len).fill(null);
      projData[len - 2] = this.timeseriesData[len - 2].value;
      projData[len - 1] = simulatedRevenue;
      this.chartInstance.data.datasets[5].data = projData;
    }

    // 3. Update anomaly marker dataset (dataset 4)
    if (this.chartInstance.data.datasets[4]) {
      const lastPoint = this.timeseriesData[len - 1];
      const mean = lastPoint.rolling_mean || lastPoint.value;
      const std = lastPoint.rolling_std || (mean * 0.05) || 1.0;
      const calcZ = Math.abs((simulatedRevenue - mean) / std);

      // If simulated value brings Z-score back inside healthy range (|Z| <= 2.0), hide red dot
      this.chartInstance.data.datasets[4].data[len - 1] = calcZ > 2.0 ? simulatedRevenue : null;
    }

    // Render smooth graph update without redrawing whole canvas
    this.chartInstance.update('none');
  }
};
