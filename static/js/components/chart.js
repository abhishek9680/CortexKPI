window.ChartComponent = {
  chartInstance: null,

  render: function(canvasId, timeseriesData) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const labels = timeseriesData.map(d => d.timestamp);
    const actualValues = timeseriesData.map(d => d.value);
    const baselineMeans = timeseriesData.map(d => d.rolling_mean);
    const lowerBounds = timeseriesData.map(d => d.lower_bound);
    const upperBounds = timeseriesData.map(d => d.upper_bound);

    // Anomaly points
    const anomalyPoints = timeseriesData.map(d => d.status === 'ANOMALY_BREACH' ? d.value : null);

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
            fill: '-1', // fill to upper bound dataset
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
                const point = timeseriesData[idx];
                return `${context.dataset.label}: ${context.raw} (Z: ${point.z_score.toFixed(2)})`;
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
  }
};
