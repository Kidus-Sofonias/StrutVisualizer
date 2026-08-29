/**
 * Chart configuration matching the EXACT charts from the Excel workbook.
 * 
 * The Excel workbook has exactly 4 charts, all in Section 3.2:
 * 1. Line chart: Stiffness X axis (kN/m) — blue with diamond markers
 * 2. Line chart: Stiffness Y axis (kN/m) — red/orange with diamond markers
 * 3. Horizontal grouped bar: Elastic vs Design displacement X-Direction
 * 4. Horizontal grouped bar: Elastic vs Design displacement Y-Direction
 */

// ── Color Palette (matching Excel styling) ─────────────────────────────
export const COLORS = {
  stiffnessX: '#4472C4',
  stiffnessY: '#ED7D31',
  elasticDisp: '#C00000',
  designDisp: '#4472C4',
  pass: '#059669',
  fail: '#DC2626',
  gridLine: 'rgba(0, 0, 0, 0.06)',
  axisLabel: '#333333',
  axisLine: '#999999',
  titleColor: '#333333',
}

// ── Base Options matching Excel chart style ────────────────────────────
function getBaseOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 400 },
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          color: '#333333',
          font: { size: 11, family: "'Segoe UI', Arial, sans-serif" },
          usePointStyle: true,
          pointStyle: 'line',
          padding: 16,
          boxWidth: 20,
          boxHeight: 2,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(255,255,255,0.96)',
        titleColor: '#333',
        bodyColor: '#333',
        borderColor: '#CCC',
        borderWidth: 1,
        cornerRadius: 4,
        padding: 10,
        titleFont: { size: 12, weight: '600' },
        bodyFont: { size: 11 },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#333333',
          font: { size: 10, family: "'Segoe UI', Arial, sans-serif" },
          maxRotation: 0,
        },
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        border: { color: '#999999' },
      },
      y: {
        ticks: {
          color: '#333333',
          font: { size: 10, family: "'Segoe UI', Arial, sans-serif" },
        },
        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
        border: { color: '#999999' },
      },
    },
  }
}

/**
 * Filter storeys to ROOF FL through 1ST FL only (matching Excel chart scope).
 * Excludes: UP ROOF, GROUND FL, BASE 1, BASE 2
 */
function chartStoreys(storeys) {
  return storeys.filter(s => {
    const n = (s.name || '').toUpperCase()
    return !n.includes('UP ROOF') && !n.includes('GROUND') && !n.includes('BASE')
  })
}

/**
 * Chart 1: Stiffness X axis (kN/m) — LINE chart with diamond markers
 * Excel: blue line, ROOF FL → 1ST FL, values ~89K → ~435K
 */
export function stiffnessXLineChart(storeys) {
  const filtered = chartStoreys(storeys)

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [{
        label: 'Stiffness X axis (kN/m)',
        data: filtered.map(s => s.kx),
        borderColor: COLORS.stiffnessX,
        backgroundColor: COLORS.stiffnessX,
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2.5,
        pointStyle: 'rectRot',
        pointBackgroundColor: COLORS.stiffnessX,
        pointBorderColor: COLORS.stiffnessX,
      }],
    },
    options: {
      ...getBaseOptions(),
      plugins: {
        ...getBaseOptions().plugins,
        title: {
          display: true,
          text: 'Stiffness X axis (kN/m)',
          color: COLORS.titleColor,
          font: { size: 13, weight: '600', family: "'Segoe UI', Arial, sans-serif" },
          padding: { bottom: 12 },
        },
        legend: {
          ...getBaseOptions().plugins.legend,
          labels: {
            ...getBaseOptions().plugins.legend.labels,
            pointStyle: 'line',
          },
        },
      },
      scales: {
        x: {
          ...getBaseOptions().scales.x,
          title: { display: false },
        },
        y: {
          ...getBaseOptions().scales.y,
          beginAtZero: true,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            callback: (v) => v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v,
          },
          title: { display: true, text: 'kN/m', color: '#333', font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Chart 2: Stiffness Y axis (kN/m) — LINE chart with diamond markers
 * Excel: red/orange line, ROOF FL → 1ST FL
 */
export function stiffnessYLineChart(storeys) {
  const filtered = chartStoreys(storeys)

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [{
        label: 'Stiffness Y axis (kN/m)',
        data: filtered.map(s => s.ky),
        borderColor: COLORS.stiffnessY,
        backgroundColor: COLORS.stiffnessY,
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2.5,
        pointStyle: 'rectRot',
        pointBackgroundColor: COLORS.stiffnessY,
        pointBorderColor: COLORS.stiffnessY,
      }],
    },
    options: {
      ...getBaseOptions(),
      plugins: {
        ...getBaseOptions().plugins,
        title: {
          display: true,
          text: 'Stiffness Y axis (kN/m)',
          color: COLORS.titleColor,
          font: { size: 13, weight: '600', family: "'Segoe UI', Arial, sans-serif" },
          padding: { bottom: 12 },
        },
        legend: {
          ...getBaseOptions().plugins.legend,
          labels: {
            ...getBaseOptions().plugins.legend.labels,
            pointStyle: 'line',
          },
        },
      },
      scales: {
        x: {
          ...getBaseOptions().scales.x,
          title: { display: false },
        },
        y: {
          ...getBaseOptions().scales.y,
          beginAtZero: true,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            callback: (v) => v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v,
          },
          title: { display: true, text: 'kN/m', color: '#333', font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Chart 3: Elastic vs Design Displacement X — HORIZONTAL GROUPED BAR
 * Excel: storeys on y-axis (1ST FL at top, ROOF FL at bottom),
 * two bars per storey: ELASTIC DISP (dark red) and Design DISP (blue)
 * Uses ux_eqx displacements for both elastic and design (they're equal from ETABS)
 */
export function displacementXBarChart(storeys) {
  // ROOF FL at top (first), 1ST FL at bottom — reverse so Chart.js renders correctly
  const filtered = chartStoreys(storeys).reverse()

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [
        {
          label: 'RSEQX ELASTIC DISP',
          data: filtered.map(s => Math.abs(s.ux_eqx || 0)),
          backgroundColor: COLORS.elasticDisp,
          borderRadius: 2,
          barPercentage: 0.8,
          categoryPercentage: 0.85,
        },
        {
          label: 'RSEQX Design DISP',
          data: filtered.map(s => Math.abs(s.ux_eqx || 0)),
          backgroundColor: COLORS.designDisp,
          borderRadius: 2,
          barPercentage: 0.8,
          categoryPercentage: 0.85,
        },
      ],
    },
    options: {
      ...getBaseOptions(),
      indexAxis: 'y',
      plugins: {
        ...getBaseOptions().plugins,
        title: {
          display: true,
          text: 'Elastic spectrum deflection versus Design spectrum deflection\nAlong X-Direction',
          color: COLORS.titleColor,
          font: { size: 13, weight: '600', family: "'Segoe UI', Arial, sans-serif" },
          padding: { bottom: 12 },
        },
        legend: {
          ...getBaseOptions().plugins.legend,
          labels: {
            ...getBaseOptions().plugins.legend.labels,
            pointStyle: 'rect',
            boxWidth: 14,
            boxHeight: 10,
          },
        },
      },
      scales: {
        x: {
          ...getBaseOptions().scales.x,
          beginAtZero: true,
          title: { display: true, text: 'Displacement (m)', color: '#333', font: { size: 10 } },
        },
        y: {
          ...getBaseOptions().scales.y,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            font: { size: 10, family: "'Segoe UI', Arial, sans-serif" },
          },
        },
      },
    },
  }
}

/**
 * Chart 4: Elastic vs Design Displacement Y — HORIZONTAL GROUPED BAR
 * Same as Chart 3 but for Y direction
 */
export function displacementYBarChart(storeys) {
  const filtered = chartStoreys(storeys).reverse()

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [
        {
          label: 'RSEQY ELASTIC DISP',
          data: filtered.map(s => Math.abs(s.uy_eqy || 0)),
          backgroundColor: COLORS.elasticDisp,
          borderRadius: 2,
          barPercentage: 0.8,
          categoryPercentage: 0.85,
        },
        {
          label: 'RSEQY Design DISP',
          data: filtered.map(s => Math.abs(s.uy_eqy || 0)),
          backgroundColor: COLORS.designDisp,
          borderRadius: 2,
          barPercentage: 0.8,
          categoryPercentage: 0.85,
        },
      ],
    },
    options: {
      ...getBaseOptions(),
      indexAxis: 'y',
      plugins: {
        ...getBaseOptions().plugins,
        title: {
          display: true,
          text: 'Elastic spectrum deflection versus Design spectrum deflection\nAlong Y-Direction',
          color: COLORS.titleColor,
          font: { size: 13, weight: '600', family: "'Segoe UI', Arial, sans-serif" },
          padding: { bottom: 12 },
        },
        legend: {
          ...getBaseOptions().plugins.legend,
          labels: {
            ...getBaseOptions().plugins.legend.labels,
            pointStyle: 'rect',
            boxWidth: 14,
            boxHeight: 10,
          },
        },
      },
      scales: {
        x: {
          ...getBaseOptions().scales.x,
          beginAtZero: true,
          title: { display: true, text: 'Displacement (m)', color: '#333', font: { size: 10 } },
        },
        y: {
          ...getBaseOptions().scales.y,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            font: { size: 10, family: "'Segoe UI', Arial, sans-serif" },
          },
        },
      },
    },
  }
}
