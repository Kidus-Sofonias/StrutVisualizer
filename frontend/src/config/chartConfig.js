/**
 * Shared chart configuration for all engineering charts.
 * Provides consistent styling, tooltips with units, and responsive design.
 */

// ── Color Palette ──────────────────────────────────────────────────────
export const COLORS = {
  // Primary series
  cyan: 'rgba(0, 188, 212, 1)',
  cyanLight: 'rgba(0, 188, 212, 0.15)',
  cyanMedium: 'rgba(0, 188, 212, 0.4)',

  orange: 'rgba(255, 152, 0, 1)',
  orangeLight: 'rgba(255, 152, 0, 0.15)',
  orangeMedium: 'rgba(255, 152, 0, 0.4)',

  // Status colors
  pass: 'rgba(76, 175, 80, 0.8)',
  passLight: 'rgba(76, 175, 80, 0.15)',
  fail: 'rgba(244, 67, 54, 0.8)',
  failLight: 'rgba(244, 67, 54, 0.15)',

  // Additional series
  purple: 'rgba(156, 39, 176, 1)',
  purpleLight: 'rgba(156, 39, 176, 0.15)',
  green: 'rgba(76, 175, 80, 1)',
  red: 'rgba(244, 67, 54, 1)',

  // Neutral
  gridLine: 'rgba(148, 163, 184, 0.15)',
  axisLabel: 'rgba(148, 163, 184, 0.8)',
  tooltipBg: 'rgba(15, 23, 42, 0.95)',
  tooltipBorder: 'rgba(148, 163, 184, 0.3)',
}

// ── Unit Labels ────────────────────────────────────────────────────────
export const UNITS = {
  length: 'm',
  force: 'kN',
  stiffness: 'kN/m',
  mass: '×10³ kg',
  moment: 'kN·m',
  percent: '%',
  angle: 'rad',
  time: 's',
  drift: 'm/m',
}

// ── Tooltip Formatter ──────────────────────────────────────────────────
function tooltipFormatter(unit) {
  return function(context) {
    let label = context.dataset.label || ''
    let value = context.parsed.y ?? context.parsed.x
    if (value === null || value === undefined) return ''
    if (typeof value === 'number') {
      value = Math.abs(value) >= 100 ? value.toFixed(0) :
              Math.abs(value) >= 1 ? value.toFixed(2) :
              value.toFixed(4)
    }
    return `${label}: ${value} ${unit || ''}`
  }
}

// ── Base Chart Options ─────────────────────────────────────────────────
function getBaseOptions(unit = '') {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 600,
      easing: 'easeOutQuart',
    },
    plugins: {
      legend: {
        labels: {
          color: COLORS.axisLabel,
          font: { size: 11, family: "'Inter', sans-serif" },
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 16,
        },
      },
      tooltip: {
        backgroundColor: COLORS.tooltipBg,
        titleColor: '#fff',
        bodyColor: 'rgba(255,255,255,0.9)',
        borderColor: COLORS.tooltipBorder,
        borderWidth: 1,
        cornerRadius: 6,
        padding: { top: 8, bottom: 8, left: 12, right: 12 },
        titleFont: { size: 12, weight: 600 },
        bodyFont: { size: 11 },
        callbacks: {
          label: tooltipFormatter(unit),
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: COLORS.axisLabel,
          font: { size: 10, family: "'Inter', sans-serif" },
          maxRotation: 45,
          minRotation: 0,
        },
        grid: { color: COLORS.gridLine, drawBorder: false },
      },
      y: {
        ticks: {
          color: COLORS.axisLabel,
          font: { size: 10, family: "'Inter', sans-serif" },
        },
        grid: { color: COLORS.gridLine, drawBorder: false },
      },
    },
  }
}

// ── Exported Chart Configs ─────────────────────────────────────────────

/**
 * Stiffness distribution bar chart (horizontal)
 * Red bars for NOT OK storeys, cyan/orange for OK
 */
export function stiffnessChart(storeys, direction = 'x') {
  const key = direction === 'x' ? 'kx' : 'ky'
  const statusKey = direction === 'x' ? 'module_3_2_6_status' : 'module_3_2_7_status'
  const color = direction === 'x' ? COLORS.cyan : COLORS.orange

  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [{
        label: `K${direction} (kN/m)`,
        data: storeys.map(s => s[key]),
        backgroundColor: storeys.map(s =>
          s[statusKey] === 'NOT OK' ? COLORS.fail : color
        ),
        borderRadius: 3,
        barThickness: 16,
      }],
    },
    options: {
      ...getBaseOptions(UNITS.stiffness),
      indexAxis: 'y',
      plugins: {
        ...getBaseOptions(UNITS.stiffness).plugins,
        title: {
          display: true,
          text: `Storey Stiffness — ${direction.toUpperCase()} Direction`,
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
        tooltip: {
          ...getBaseOptions(UNITS.stiffness).plugins.tooltip,
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.x
              const storey = storeys[ctx.dataIndex]
              const status = storey[statusKey] || 'N/A'
              return `K${direction}: ${v?.toFixed(0)} kN/m  [${status}]`
            },
          },
        },
      },
      scales: {
        ...getBaseOptions().scales,
        x: {
          ...getBaseOptions().scales.x,
          title: { display: true, text: 'Stiffness (kN/m)', color: COLORS.axisLabel, font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Eccentricity line chart
 */
export function eccentricityChart(storeys) {
  const opts = getBaseOptions(UNITS.length)
  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [
        {
          label: 'eox (m)',
          data: storeys.map(s => s.eox),
          borderColor: COLORS.cyan,
          backgroundColor: COLORS.cyanLight,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
        {
          label: 'eoy (m)',
          data: storeys.map(s => s.eoy),
          borderColor: COLORS.orange,
          backgroundColor: COLORS.orangeLight,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 5,
          borderWidth: 2,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: 'Structural Eccentricity Along Height',
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
        annotation: undefined, // Could add 0-line annotation
      },
      scales: {
        ...opts.scales,
        y: {
          ...opts.scales.y,
          title: { display: true, text: 'Eccentricity (m)', color: COLORS.axisLabel, font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Torsional radius line chart
 */
export function torsionalRadiusChart(storeys) {
  const opts = getBaseOptions(UNITS.length)
  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [
        {
          label: 'rx (m)',
          data: storeys.map(s => s.rx),
          borderColor: COLORS.cyan,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          borderWidth: 2,
        },
        {
          label: 'ry (m)',
          data: storeys.map(s => s.ry),
          borderColor: COLORS.orange,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          borderWidth: 2,
        },
        {
          label: 'ls (m)',
          data: storeys.map(s => s.ls),
          borderColor: COLORS.red,
          borderDash: [6, 4],
          fill: false,
          tension: 0,
          pointRadius: 0,
          borderWidth: 1.5,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: 'Torsional Radii vs Floor Radius',
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
      },
      scales: {
        ...opts.scales,
        y: {
          ...opts.scales.y,
          title: { display: true, text: 'Radius (m)', color: COLORS.axisLabel, font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Mass distribution bar chart
 */
export function massChart(storeys) {
  const opts = getBaseOptions(UNITS.mass)
  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [{
        label: 'Mass (×10³ kg)',
        data: storeys.map(s => s.module_3_2_8_mass),
        backgroundColor: storeys.map(s => {
          if (s.module_3_2_8_status_upper === 'NOT OK' || s.module_3_2_8_status_lower === 'NOT OK')
            return COLORS.fail
          return COLORS.pass
        }),
        borderRadius: 3,
        barThickness: 16,
      }],
    },
    options: {
      ...opts,
      indexAxis: 'y',
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: 'Mass Distribution Along Height',
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
        tooltip: {
          ...opts.plugins.tooltip,
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.x
              const storey = storeys[ctx.dataIndex]
              const upper = storey.module_3_2_8_status_upper || '-'
              const lower = storey.module_3_2_8_status_lower || '-'
              return [`Mass: ${v?.toFixed(1)} ×10³ kg`, `< 2·Mi+1: ${upper}`, `< 2·Mi-1: ${lower}`]
            },
          },
        },
      },
    },
  }
}

/**
 * Force distribution stacked bar chart (for 3.3)
 */
export function forceDistributionChart(storeys, direction = 'x') {
  const opts = getBaseOptions(UNITS.force)
  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [
        {
          label: 'Column %',
          data: storeys.map(s => s.column_pct * 100),
          backgroundColor: COLORS.cyanMedium,
          borderRadius: 2,
        },
        {
          label: 'Wall %',
          data: storeys.map(s => s.wall_pct * 100),
          backgroundColor: COLORS.orangeMedium,
          borderRadius: 2,
        },
      ],
    },
    options: {
      ...opts,
      indexAxis: 'y',
      scales: {
        ...opts.scales,
        x: {
          ...opts.scales.x,
          max: 100,
          title: { display: true, text: 'Percentage (%)', color: COLORS.axisLabel, font: { size: 10 } },
        },
      },
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: `${direction.toUpperCase()}-Direction: Column vs Wall Participation`,
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
      },
    },
  }
}

/**
 * Modal mass participation line chart (for 4.2)
 */
export function modalParticipationChart(modes) {
  const opts = getBaseOptions(UNITS.percent)
  return {
    data: {
      labels: modes.map(m => `Mode ${m.mode}`),
      datasets: [
        {
          label: 'ΣUX (%)',
          data: modes.map(m => m.sum_ux),
          borderColor: COLORS.cyan,
          backgroundColor: COLORS.cyanLight,
          fill: true,
          tension: 0.3,
          pointRadius: 3,
          borderWidth: 2,
        },
        {
          label: 'ΣUY (%)',
          data: modes.map(m => m.sum_uy),
          borderColor: COLORS.orange,
          backgroundColor: COLORS.orangeLight,
          fill: true,
          tension: 0.3,
          pointRadius: 3,
          borderWidth: 2,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: 'Cumulative Modal Mass Participation',
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
      },
      scales: {
        ...opts.scales,
        y: {
          ...opts.scales.y,
          max: 100,
          title: { display: true, text: 'Mass Participation (%)', color: COLORS.axisLabel, font: { size: 10 } },
        },
      },
    },
  }
}

/**
 * Imperfection forces bar chart (for 4.3)
 */
export function imperfectionForcesChart(storeys) {
  const opts = getBaseOptions(UNITS.force)
  return {
    data: {
      labels: storeys.map(s => s.name),
      datasets: [{
        label: 'Hi (kN)',
        data: storeys.map(s => s.hi),
        backgroundColor: COLORS.purple,
        borderRadius: 3,
        barThickness: 16,
      }],
    },
    options: {
      ...opts,
      indexAxis: 'y',
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: 'Transversal Imperfection Force per Storey',
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
      },
    },
  }
}

/**
 * Overturning comparison bar chart (for 4.6)
 */
export function overturningChart(xData, yData) {
  const opts = getBaseOptions(UNITS.moment)
  return {
    data: {
      labels: ['X-Direction', 'Y-Direction'],
      datasets: [
        {
          label: 'Overturning Moment (kN·m)',
          data: [xData.total_ot_moment, yData.total_ot_moment],
          backgroundColor: COLORS.red,
          borderRadius: 4,
          barThickness: 40,
        },
        {
          label: 'Resisting Moment (kN·m)',
          data: [xData.resisting_moment, yData.resisting_moment],
          backgroundColor: COLORS.green,
          borderRadius: 4,
          barThickness: 40,
        },
      ],
    },
    options: {
      ...opts,
      plugins: {
        ...opts.plugins,
        title: {
          display: true,
          text: `Overturning vs Resisting — SF: X=${xData.safety_factor?.toFixed(2)}, Y=${yData.safety_factor?.toFixed(2)}`,
          color: COLORS.axisLabel,
          font: { size: 12, weight: 600 },
          padding: { bottom: 12 },
        },
      },
    },
  }
}

/**
 * ChartCard wrapper component style
 */
export const chartCardStyle = {
  background: 'var(--bg-secondary)',
  borderRadius: 8,
  padding: 20,
  marginBottom: 20,
  border: '1px solid var(--border)',
}
