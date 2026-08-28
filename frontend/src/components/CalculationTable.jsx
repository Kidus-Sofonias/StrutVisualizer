import { motion } from 'framer-motion'
import { useState } from 'react'
import { BookOpen, Calculator, ChevronDown, ChevronRight } from 'lucide-react'
import { Line, Bar } from 'react-chartjs-2'
import { engineeringText } from '../data/engineeringText'

const columns = {
  '3.2.2': [
    { key: 'name', label: 'Story', fmt: v => v },
    { key: 'xcm', label: 'Xcm (m)', fmt: v => v?.toFixed(3) },
    { key: 'ycm', label: 'Ycm (m)', fmt: v => v?.toFixed(3) },
    { key: 'xcr', label: 'Xcr (m)', fmt: v => v?.toFixed(3) },
    { key: 'ycr', label: 'Ycr (m)', fmt: v => v?.toFixed(3) },
    { key: 'eox', label: 'eox (m)', fmt: v => v?.toFixed(3), highlight: true },
    { key: 'eoy', label: 'eoy (m)', fmt: v => v?.toFixed(3), highlight: true },
  ],
  '3.2.3': [
    { key: 'name', label: 'Story' },
    { key: 'ux_ul1', label: 'UX(UL1)', fmt: v => v?.toFixed(4) },
    { key: 'uy_ul2', label: 'UY(UL2)', fmt: v => v?.toFixed(4) },
    { key: 'rz_ul3', label: 'RZ(UL3)', fmt: v => v?.toFixed(5) },
    { key: 'kfx', label: 'KFX', fmt: v => v?.toFixed(6) },
    { key: 'kfy', label: 'KFY', fmt: v => v?.toFixed(6) },
    { key: 'kmt', label: 'KMT', fmt: v => v?.toFixed(4) },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3), highlight: true },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3), highlight: true },
  ],
  '3.2.4': [
    { key: 'name', label: 'Story' },
    { key: 'eox', label: 'eox (m)', fmt: v => v?.toFixed(3) },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_limit_x', label: '0.3·rx', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_eox_status', label: 'Status X', isStatus: true },
    { key: 'eoy', label: 'eoy (m)', fmt: v => v?.toFixed(3) },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_limit_y', label: '0.3·ry', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_eoy_status', label: 'Status Y', isStatus: true },
  ],
  '3.2.5': [
    { key: 'name', label: 'Story' },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3) },
    { key: 'ls', label: 'ls (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_5_rx_status', label: 'Status X', isStatus: true },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_5_ry_status', label: 'Status Y', isStatus: true },
  ],
  '3.2.6': [
    { key: 'name', label: 'Story' },
    { key: 'kx', label: 'Kx (kN/m)', fmt: v => v?.toFixed(2), highlight: true },
    { key: 'vx_eqx', label: 'VX_EQX', fmt: v => v?.toFixed(2) },
    { key: 'ux_eqx', label: 'UX_EQX', fmt: v => v?.toFixed(6) },
    { key: 'module_3_2_6_status', label: 'Status', isStatus: true },
  ],
  '3.2.7': [
    { key: 'name', label: 'Story' },
    { key: 'ky', label: 'Ky (kN/m)', fmt: v => v?.toFixed(2), highlight: true },
    { key: 'vy_eqy', label: 'VY_EQY', fmt: v => v?.toFixed(2) },
    { key: 'uy_eqy', label: 'UY_EQY', fmt: v => v?.toFixed(6) },
    { key: 'module_3_2_7_status', label: 'Status', isStatus: true },
  ],
  '3.2.8': [
    { key: 'name', label: 'Story' },
    { key: 'module_3_2_8_mass', label: 'Mass (×10³ kg)', fmt: v => v?.toFixed(1), highlight: true },
    { key: 'module_3_2_8_status_upper', label: 'Mi < 2·Mi+1', isStatus: true },
    { key: 'module_3_2_8_status_lower', label: 'Mi < 2·Mi-1', isStatus: true },
  ],
}

function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, key) => acc?.[key], obj)
}

/* ── Engineering Text Block ──────────────────────────────────────────── */
function EngineeringBlock({ moduleKey }) {
  const et = engineeringText['3.2']?.subsections?.[moduleKey]
  if (!et) return null
  const [expanded, setExpanded] = useState(false)

  return (
    <div style={{
      background: 'var(--bg-secondary)', borderRadius: 8, padding: '14px 18px',
      marginBottom: 16, border: '1px solid var(--border)',
    }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, userSelect: 'none' }}
      >
        <BookOpen size={14} style={{ color: 'var(--accent)' }} />
        <span style={{ fontWeight: 600, fontSize: 12, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Engineering Background — {moduleKey}
        </span>
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)' }}>
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
      </div>
      {expanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ marginTop: 10, fontSize: 12, lineHeight: 1.7, color: 'var(--text)' }}
        >
          {et.criteria && (
            <div style={{ marginBottom: 8 }}>
              {et.criteria.split('\n').map((p, i) => (
                <p key={i} style={{ margin: '0 0 4px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
              ))}
            </div>
          )}
          {et.formula && (
            <div style={{
              background: 'var(--bg-primary)', borderRadius: 6, padding: '8px 12px',
              fontFamily: 'monospace', fontSize: 11, whiteSpace: 'pre-wrap',
              borderLeft: '3px solid var(--accent)',
            }}>
              <Calculator size={11} style={{ display: 'inline', verticalAlign: -2 }} /> {et.formula}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}

/* ── Chart for 3.2 modules ──────────────────────────────────────────── */
const chartColors = {
  cyan: 'rgba(0, 210, 255, 1)',
  cyanFill: 'rgba(0, 210, 255, 0.15)',
  orange: 'rgba(255, 165, 0, 1)',
  orangeFill: 'rgba(255, 165, 0, 0.15)',
}

const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: 'var(--text)', font: { size: 11 } } } },
  scales: {
    x: { ticks: { color: 'var(--text-muted)', font: { size: 9 }, maxRotation: 45 }, grid: { color: 'var(--border)' } },
    y: { ticks: { color: 'var(--text-muted)', font: { size: 10 } }, grid: { color: 'var(--border)' } },
  },
}

function ModuleChart({ moduleKey, storeys }) {
  const names = storeys.map(s => s.name)

  if (moduleKey === '3.2.2') {
    return (
      <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 16, marginBottom: 16, border: '1px solid var(--border)' }}>
        <h4 style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Structural Eccentricity Along Height</h4>
        <div style={{ height: 280 }}>
          <Line data={{
            labels: names,
            datasets: [
              { label: 'eox (m)', data: storeys.map(s => s.eox), borderColor: chartColors.cyan, backgroundColor: chartColors.cyanFill, fill: false, tension: 0.3 },
              { label: 'eoy (m)', data: storeys.map(s => s.eoy), borderColor: chartColors.orange, backgroundColor: chartColors.orangeFill, fill: false, tension: 0.3 },
            ],
          }} options={chartOpts} />
        </div>
      </div>
    )
  }

  if (moduleKey === '3.2.3') {
    return (
      <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 16, marginBottom: 16, border: '1px solid var(--border)' }}>
        <h4 style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Torsional Radii Along Height</h4>
        <div style={{ height: 280 }}>
          <Line data={{
            labels: names,
            datasets: [
              { label: 'rx (m)', data: storeys.map(s => s.rx), borderColor: chartColors.cyan, fill: false, tension: 0.3 },
              { label: 'ry (m)', data: storeys.map(s => s.ry), borderColor: chartColors.orange, fill: false, tension: 0.3 },
            ],
          }} options={chartOpts} />
        </div>
      </div>
    )
  }

  if (moduleKey === '3.2.6') {
    return (
      <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 16, marginBottom: 16, border: '1px solid var(--border)' }}>
        <h4 style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Stiffness Distribution — X Direction</h4>
        <div style={{ height: 280 }}>
          <Bar data={{
            labels: names,
            datasets: [{
              label: 'Kx (kN/m)',
              data: storeys.map(s => s.kx),
              backgroundColor: storeys.map(s => s.module_3_2_6_status === 'NOT OK' ? 'rgba(255, 99, 132, 0.7)' : chartColors.cyan),
              borderRadius: 3,
            }],
          }} options={{ ...chartOpts, indexAxis: 'y' }} />
        </div>
      </div>
    )
  }

  if (moduleKey === '3.2.7') {
    return (
      <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 16, marginBottom: 16, border: '1px solid var(--border)' }}>
        <h4 style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Stiffness Distribution — Y Direction</h4>
        <div style={{ height: 280 }}>
          <Bar data={{
            labels: names,
            datasets: [{
              label: 'Ky (kN/m)',
              data: storeys.map(s => s.ky),
              backgroundColor: storeys.map(s => s.module_3_2_7_status === 'NOT OK' ? 'rgba(255, 99, 132, 0.7)' : chartColors.orange),
              borderRadius: 3,
            }],
          }} options={{ ...chartOpts, indexAxis: 'y' }} />
        </div>
      </div>
    )
  }

  if (moduleKey === '3.2.8') {
    return (
      <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 16, marginBottom: 16, border: '1px solid var(--border)' }}>
        <h4 style={{ fontSize: 12, color: 'var(--accent)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>Mass Distribution Along Height</h4>
        <div style={{ height: 280 }}>
          <Bar data={{
            labels: names,
            datasets: [{
              label: 'Mass (×10³ kg)',
              data: storeys.map(s => s.module_3_2_8_mass),
              backgroundColor: storeys.map(s => {
                if (s.module_3_2_8_status_upper === 'NOT OK' || s.module_3_2_8_status_lower === 'NOT OK') return 'rgba(255, 99, 132, 0.7)'
                return 'rgba(75, 192, 192, 0.7)'
              }),
              borderRadius: 3,
            }],
          }} options={{ ...chartOpts, indexAxis: 'y' }} />
        </div>
      </div>
    )
  }

  return null
}

export default function CalculationTable({ storeys, module: activeModule, onSelectStorey }) {
  const cols = columns[activeModule] || columns['3.2.2']

  return (
    <motion.div
      className="calc-table-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      {/* Engineering background text */}
      <EngineeringBlock moduleKey={activeModule} />

      <div className="calc-table-header">
        <h3>Table {activeModule} — All Storeys</h3>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          {storeys.length} storeys
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="calc-table">
          <thead>
            <tr>
              {cols.map(col => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {storeys.map((storey, idx) => (
              <motion.tr
                key={storey.id}
                onClick={() => onSelectStorey(storey)}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.02 }}
              >
                {cols.map(col => {
                  const val = getNestedValue(storey, col.key)
                  const display = col.fmt ? col.fmt(val) : val

                  if (col.isStatus) {
                    const s = val || '—'
                    const cls = s === 'OK' ? 'pass' : s === 'NOT OK' ? 'fail' : 'na'
                    return (
                      <td key={col.key} className={`status-cell ${cls}`}>
                        {display}
                      </td>
                    )
                  }

                  return (
                    <td
                      key={col.key}
                      style={col.highlight ? { color: 'var(--cyan)', fontWeight: 600 } : {}}
                    >
                      {display ?? '—'}
                    </td>
                  )
                })}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Chart below table */}
      <ModuleChart moduleKey={activeModule} storeys={storeys} />
    </motion.div>
  )
}
