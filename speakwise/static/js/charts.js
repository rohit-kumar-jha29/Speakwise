/**
 * charts.js - Interactive Visualizations for SpeakWise Progress
 * Uses Chart.js with responsive dark/light theme integration.
 */

const Charts = {
  trendChartInstance: null,
  radarChartInstance: null,

  renderTrendChart(canvasId, trendData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.trendChartInstance) {
      this.trendChartInstance.destroy();
    }

    const labels = trendData.map(d => d.label || `Session ${d.session_num}`);
    const scores = trendData.map(d => d.score);
    const isDark = document.documentElement.getAttribute("data-theme") !== "light";

    const ctx = canvas.getContext("2d");
    const gradient = ctx.createLinearGradient(0, 0, 0, 260);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.45)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0.0)");

    this.trendChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Communication Score",
          data: scores,
          borderColor: "#6366f1",
          borderWidth: 3,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#8b5cf6",
          pointBorderColor: isDark ? "#1e293b" : "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: isDark ? "#1e293b" : "#ffffff",
            titleColor: isDark ? "#f8fafc" : "#0f172a",
            bodyColor: isDark ? "#94a3b8" : "#475569",
            borderColor: "rgba(99, 102, 241, 0.3)",
            borderWidth: 1,
            padding: 10,
            callbacks: {
              label: (context) => `Score: ${context.parsed.y}/100`
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.05)"
            },
            ticks: {
              color: isDark ? "#94a3b8" : "#64748b",
              font: { size: 11 }
            }
          },
          y: {
            min: 50,
            max: 100,
            grid: {
              color: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.05)"
            },
            ticks: {
              color: isDark ? "#94a3b8" : "#64748b",
              stepSize: 10,
              font: { size: 11 }
            }
          }
        }
      }
    });
  },

  renderRadarChart(canvasId, stats) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.radarChartInstance) {
      this.radarChartInstance.destroy();
    }

    const isDark = document.documentElement.getAttribute("data-theme") !== "light";
    const ctx = canvas.getContext("2d");

    const dataValues = [
      stats.avg_grammar || 75,
      stats.avg_vocab || 72,
      stats.avg_clarity || 80,
      stats.avg_tone || 84,
      Math.min(95, (stats.avg_overall || 74) + 3)
    ];

    this.radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["Grammar", "Vocabulary", "Clarity", "Tone", "Confidence"],
        datasets: [{
          label: "Proficiency Index",
          data: dataValues,
          backgroundColor: "rgba(6, 182, 212, 0.25)",
          borderColor: "#06b6d4",
          borderWidth: 2,
          pointBackgroundColor: "#06b6d4",
          pointBorderColor: "#fff",
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          r: {
            angleLines: {
              color: isDark ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.08)"
            },
            grid: {
              color: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)"
            },
            pointLabels: {
              color: isDark ? "#f8fafc" : "#1e293b",
              font: { size: 11, weight: "600" }
            },
            ticks: {
              display: false,
              min: 40,
              max: 100
            }
          }
        }
      }
    });
  }
};
