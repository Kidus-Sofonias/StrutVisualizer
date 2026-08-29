/**
 * Chart configuration matching the EXACT charts from the Excel workbook.
 * 
 * The Excel workbook has exactly 4 charts, all in Section 3.2:
 * 1. Line chart: Stiffness X axis (kN/m) — blue with diamond markers
 * 2. Line chart: Stiffness Y axis (kN/m) — red with diamond markers
 * 3. Horizontal grouped bar: Elastic vs Design displacement X-Direction
 * 4. Horizontal grouped bar: Elastic vs Design displacement Y-Direction
 */

// ── Color Palette (matching Excel styling) ─────────────────────────────
export const COLORS = {
  // Excel chart colors
  stiffnessX: '#4472C4',       // Blue (Excel default series 1)
  stiffnessY: '#ED7D31',       // Red/Orange (Excel default series 2)
  elasticDisp: '#C00000',      // Dark red (Excel elastic)
  designDisp: '#4472C4',       // Blue (Excel design)

  // Status colors
  pass: '#059669',
  fail: '#DC2626',

  // Neutral
  gridLine: 'rgba(0, 0, 0, 0.06)',
  axisLabel: '#333333',
  axisLine: '#999999',
  tooltipBg: 'rgba(255, 255, 255, 0.96)',
  tooltipBorder: '#CCCCCC',
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
 * Chart 1: Stiffness X axis (kN/m) — LINE chart with markers
 * Matches Excel: blue line, diamond markers, ROOF FL to 1ST FL on x-axis
 */
export function stiffnessXLineChart(storeys) {
  // Filter to storeys that appear in Excel: ROOF FL through 1ST FL only
  const filtered = storeys.filter(s => {
    const n = s.name?.toUpperCase() || ''
    return !n.includes('UP ROOF') && !n.includes('BASE')
  })

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
        pointStyle: 'rectRot', // diamond shape like Excel
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
        ...getBaseOptions().scales,
        y: {
          ...getBaseOptions().scales.y,
          beginAtZero: true,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            callback: (v) => v.toLocaleString(),
          },
        },
      },
    },
  }
}

/**
 * Chart 2: Stiffness Y axis (kN/m) — LINE chart with markers
 * Matches Excel: red/orange line, diamond markers
 */
export function stiffnessYLineChart(storeys) {
  const filtered = storeys.filter(s => {
    const n = s.name?.toUpperCase() || ''
    return !n.includes('UP ROOF') && !n.includes('BASE')
  })

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
        ...getBaseOptions().scales,
        y: {
          ...getBaseOptions().scales.y,
          beginAtZero: true,
          ticks: {
            ...getBaseOptions().scales.y.ticks,
            callback: (v) => v.toLocaleString(),
          },
        },
      },
    },
  }
}

/**
 * Chart 3: Elastic vs Design Displacement X — HORIZONTAL GROUPED BAR
 * Matches Excel: storeys on y-axis (1ST FL at bottom, ROOF FL at top),
 * two bars per storey: RSEQX ELASTIC DISP (red) and RSEQX Design DISP (blue)
 */
export function displacementXBarChart(storeys) {
  // Filter to ROOF FL through 1ST FL only, reverse for bottom-to-top display
  const filtered = storeys.filter(s => {
    const n = s.name?.toUpperCase() || ''
    return !n.includes('UP ROOF') && !n.includes('BASE') && !n.includes('GROUND')
  }).reverse()

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [
        {
          label: 'RSEQX ELASTIC DISP',
          data: filtered.map(s => s.module_3_2_4_limit_x ? null : null), // placeholder
          backgroundColor: COLORS.elasticDisp,
          borderRadius: 2,
          barPercentage: 0.85,
          categoryPercentage: 0.8,
        },
        {
          label: 'RSEQX Design DISP',
          data: filtered.map(s => s.module_3_2_4_limit_x ? null : null), // placeholder
          backgroundColor: COLORS.designDisp,
          borderRadius: 2,
          barPercentage: 0.85,
          categoryPercentage: 0.8,
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
          title: { display: true, text: 'Displacement (m)', color: '#333', font: { size: 10 } },
          beginAtZero: true,
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
  const filtered = storeys.filter(s => {
    const n = s.name?.toUpperCase() || ''
    return !n.includes('UP ROOF') && !n.includes('BASE') && !n.includes('GROUND')
  }).reverse()

  return {
    data: {
      labels: filtered.map(s => s.name),
      datasets: [
        {
          label: 'RSEQY ELASTIC DISP',
          data: filtered.map(() => null),
          backgroundColor: COLORS.elasticDisp,
          borderRadius: 2,
          barPercentage: 0.85,
          categoryPercentage: 0.8,
        },
        {
          label: 'RSEQY Design DISP',
          data: filtered.map(() => null),
          backgroundColor: COLORS.designDisp,
          borderRadius: 2,
          barPercentage: 0.85,
          categoryPercentage: 0.8,
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
          title: { display: true, text: 'Displacement (m)', color: '#333', font: { size: 10 } },
          beginAtZero: true,
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
