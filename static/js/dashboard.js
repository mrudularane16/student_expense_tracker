(function () {
  var dataEl = document.getElementById("chart-data");
  if (!dataEl || typeof Chart === "undefined") return;

  var data = JSON.parse(dataEl.textContent);
  var charts = [];

  var PALETTE = ["#6366F1", "#F59E0B", "#10B981", "#EF4444", "#3B82F6", "#EC4899", "#14B8A6"];

  var money = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 });
  var compact = new Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 });

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function rupees(value) {
    return "₹" + money.format(value);
  }

  function destroyAll() {
    charts.forEach(function (c) { c.destroy(); });
    charts = [];
  }

  function build() {
    destroyAll();

    Chart.defaults.color = css("--muted");
    Chart.defaults.font.family = "Inter, system-ui, sans-serif";
    Chart.defaults.borderColor = css("--border");

    var gridColor = css("--border");
    var money_axis = {
      beginAtZero: true,
      grid: { color: gridColor },
      ticks: { callback: function (v) { return "₹" + compact.format(v); } }
    };

    // 1. Spending breakdown (doughnut)
    var catCanvas = document.getElementById("chart-category");
    if (catCanvas && data.category.values.length) {
      charts.push(new Chart(catCanvas, {
        type: "doughnut",
        data: {
          labels: data.category.labels,
          datasets: [{
            data: data.category.values,
            backgroundColor: data.category.labels.map(function (_, i) { return PALETTE[i % PALETTE.length]; }),
            borderColor: css("--surface"),
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "62%",
          plugins: {
            legend: { position: "bottom", labels: { boxWidth: 12, padding: 14 } },
            tooltip: { callbacks: { label: function (ctx) { return " " + ctx.label + ": " + rupees(ctx.parsed); } } }
          }
        }
      }));
    }

    // 2. Income vs expenses (grouped bars)
    var monthlyCanvas = document.getElementById("chart-monthly");
    if (monthlyCanvas) {
      charts.push(new Chart(monthlyCanvas, {
        type: "bar",
        data: {
          labels: data.monthly.labels,
          datasets: [
            { label: "Income", data: data.monthly.income, backgroundColor: css("--pos"), borderRadius: 4 },
            { label: "Expenses", data: data.monthly.expense, backgroundColor: css("--neg"), borderRadius: 4 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { x: { grid: { display: false } }, y: money_axis },
          plugins: {
            legend: { position: "bottom", labels: { boxWidth: 12, padding: 14 } },
            tooltip: { callbacks: { label: function (ctx) { return " " + ctx.dataset.label + ": " + rupees(ctx.parsed.y); } } }
          }
        }
      }));
    }

    // 3. Balance trend (line)
    var balanceCanvas = document.getElementById("chart-balance");
    if (balanceCanvas) {
      var line = css("--bar");
      charts.push(new Chart(balanceCanvas, {
        type: "line",
        data: {
          labels: data.monthly.labels,
          datasets: [{
            label: "Balance",
            data: data.monthly.balance,
            borderColor: line,
            backgroundColor: css("--soft"),
            pointBackgroundColor: line,
            pointRadius: 4,
            borderWidth: 3,
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: gridColor }, ticks: { callback: function (v) { return "₹" + compact.format(v); } } }
          },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: function (ctx) { return " Balance: " + rupees(ctx.parsed.y); } } }
          }
        }
      }));
    }
  }

  build();

  // Redraw with the right colours when the dark mode toggle is used
  new MutationObserver(build).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"]
  });
})();