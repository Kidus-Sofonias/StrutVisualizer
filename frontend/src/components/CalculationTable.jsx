import { useState } from 'react'
import { BookOpen, Calculator, ChevronDown, ChevronRight, Pencil } from 'lucide-react'
import { Line, Bar } from 'react-chartjs-2'
import { engineeringText } from '../data/engineeringText'
import {
  stiffnessXLineChart, stiffnessYLineChart,
  displacementXBarChart, displacementYBarChart,
} from '../config/chartConfig'

const columns = {
  '3.2.1': [
    { key: 'name', label: 'Story' },
    { key: 'lmax', label: 'Lmax (m)', fmt: v => v?.toFixed(1) },
    { key: 'lmin', label: 'Lmin (m)', fmt: v => v?.toFixed(1) },
    { key: 'module_3_2_1_lambda', label: '\u03BB = Lmax/Lmin', fmt: v => v?.toFixed(4), highlight: true },
    { key: 'module_3_2_1_status', label: 'Status (\u03BB < 4)', isStatus: true },
  ],
  '3.2.2': [
    { key: 'name', label: 'Story' },
    { key: 'xcm', label: 'Xcm (m)', fmt: v => v?.toFixed(3) },
    { key: 'ycm', label: 'Ycm (m)', fmt: v => v?.toFixed(3) },
    { key: 'xcr', label: 'Xcr (m)', fmt: v => v?.toFixed(3) },
    { key: 'ycr', label: 'Ycr (m)', fmt: v => v?.toFixed(3) },
    { key: 'eox', label: 'eox (m)', fmt: v => v?.toFixed(3), highlight: true },
    { key: 'eoy', label: 'eoy (m)', fmt: v => v?.toFixed(3), highlight: true },
  ],
  '3.2.3': [
    { key: 'name', label: 'Story' },
    { key: 'ux_ul1', label: 'UX(UL1) (m)', fmt: v => v?.toFixed(4) },
    { key: 'uy_ul2', label: 'UY(UL2) (m)', fmt: v => v?.toFixed(4) },
    { key: 'rz_ul3', label: 'RZ(UL3) (rad)', fmt: v => v?.toFixed(5) },
    { key: 'kfx', label: 'KFX (kN/m)', fmt: v => v?.toFixed(6) },
    { key: 'kfy', label: 'KFY (kN/m)', fmt: v => v?.toFixed(6) },
    { key: 'kmt', label: 'KMT (kN/m)', fmt: v => v?.toFixed(4) },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3), highlight: true },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3), highlight: true },
  ],
  '3.2.4': [
    { key: 'name', label: 'Story' },
    { key: 'eox', label: 'eox (m)', fmt: v => v?.toFixed(3) },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_limit_x', label: '0.3\u00B7rx', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_eox_status', label: 'Status X', isStatus: true },
    { key: 'eoy', label: 'eoy (m)', fmt: v => v?.toFixed(3) },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_limit_y', label: '0.3\u00B7ry', fmt: v => v?.toFixed(3) },
    { key: 'module_3_2_4_eoy_status', label: 'Status Y', isStatus: true },
  ],
  '3.2.5': [
    { key: 'name', label: 'Story' },
    { key: 'rx', label: 'rx (m)', fmt: v => v?.toFixed(3) },
    { key: 'ls', label: 'ls (m)', fmt: v => v?.toFixed(3), highlight: true },
    { key: 'module_3_2_5_rx_status', label: 'Status X', isStatus: true },
    { key: 'ry', label: 'ry (m)', fmt: v => v?.toFixed(3) },
    { key: 'ls', label: 'ls (m)', fmt: v => v?.toFixed(3), highlight: true, id: 'ls_y' },
    { key: 'module_3_2_5_ry_status', label: 'Status Y', isStatus: true },
  ],
  '3.2.6': [
    { key: 'name', label: 'Story' },
    { key: 'kx', label: 'Stiffness X axis (kN/m)', fmt: v => v?.toFixed(2), highlight: true },
    { key: 'module_3_2_6_status', label: 'K >0.7*Ki-1 X axis', isStatus: true },
  ],
  '3.2.7': [
    { key: 'name', label: 'Story' },
    { key: 'ky', label: 'Stiffness Y axis (kN/m)', fmt: v => v?.toFixed(2), highlight: true },
    { key: 'module_3_2_7_status', label: 'Ki >0.7*Ki+1 Y axis', isStatus: true },
  ],
  '3.2.8': [
    { key: 'name', label: 'Story' },
    { key: 'module_3_2_8_mass', label: 'Mass (1000 x Kg)', fmt: v => v?.toFixed(4), highlight: true },
    { key: 'module_3_2_8_status_upper', label: 'Mi < 2Mi+1', isStatus: true },
    { key: 'module_3_2_8_status_lower', label: 'Mi < 2Mi-1', isStatus: true },
  ],
}

const tableCaptions = {
  '3.2.1': 'Table 3.2.1: Slenderness of the Building',
  '3.2.2': 'Table 3.2.2: Structural Eccentricity of the Building',
  '3.2.3': 'Table 3.2.3: Torsional Radius of the Building',
  '3.2.4': 'Table 3.2.4: Structural Eccentricity and Radius of Gyration Comparison for the Building',
  '3.2.5': 'Table 3.2.5: Torsional Radius and Radius of Gyration Comparison for the Building',
  '3.2.6': 'Table 3.2.6: Storey Stiffness along X Direction of the Building',
  '3.2.7': 'Table 3.2.7: Storey Stiffness along Y Direction of the Building',
  '3.2.8': 'Table 3.2.8: Mass Distribution along height of the Building',
}

function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, key) => acc?.[key], obj)
}

/* ── Editable Formula Block ──────────────────────────────────────────── */
function FormulaBlock({ moduleKey }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [customFormula, setCustomFormula] = useState('')
  const et = engineeringText['3.2']?.subsections?.[moduleKey]
  if (!et) return null

  const handleSave = () => {
    const stored = JSON.parse(localStorage.getItem('custom_formulas') || '{}')
    stored[`3.2.${moduleKey}`] = customFormula
    localStorage.setItem('custom_formulas', JSON.stringify(stored))
    setEditing(false)
  }

  const storedFormulas = JSON.parse(localStorage.getItem('custom_formulas') || '{}')
  const displayFormula = storedFormulas[`3.2.${moduleKey}`] || et.formula

  return (
    <>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
          userSelect: 'none', padding: '8px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-primary)',
          background: 'var(--bg-subtle)', marginBottom: 8,
        }}
      >
        <Calculator size={13} style={{ color: 'var(--accent)', flexShrink: 0 }} />
        <span style={{
          fontWeight: 600, fontSize: 11, color: 'var(--accent)',
          textTransform: 'uppercase', letterSpacing: '0.04em', flex: 1,
        }}>Formula</span>
        <button
          onClick={(e) => { e.stopPropagation(); setEditing(!editing); setCustomFormula(displayFormula) }}
          style={{
            background: 'none', border: '1px solid var(--border-primary)',
            borderRadius: 4, padding: '2px 6px', cursor: 'pointer',
            color: 'var(--text-tertiary)', fontSize: 10,
            display: 'flex', alignItems: 'center', gap: 3,
          }}
          title="Edit formula"
        ><Pencil size={10} /> Edit</button>
        <span style={{ color: 'var(--text-tertiary)' }}>
          {expanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        </span>
      </div>
      {expanded && (
        <div style={{
          padding: '8px 12px', marginBottom: 14,
          fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
          whiteSpace: 'pre-wrap', borderLeft: '3px solid var(--accent)',
          color: 'var(--text-primary)', lineHeight: 1.8,
          background: 'var(--bg-surface)', borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
        }}>{displayFormula}</div>
      )}
      {editing && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 9999,
        }} onClick={() => setEditing(false)}>
          <div style={{
            background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)',
            padding: 24, width: 500, maxHeight: '80vh',
            boxShadow: 'var(--shadow-lg)', border: '1px solid var(--border-primary)',
          }} onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Edit Formula — Table {moduleKey}</h3>
            <p style={{ fontSize: 12, color: 'var(--text-tertiary)', marginBottom: 12 }}>
              Enter the formula using mathematical notation or Excel-style format.
            </p>
            <textarea value={customFormula} onChange={e => setCustomFormula(e.target.value)}
              style={{
                width: '100%', minHeight: 120, padding: 12,
                fontFamily: "'JetBrains Mono', monospace", fontSize: 12,
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-sm)', background: 'var(--bg-subtle)',
                color: 'var(--text-primary)', resize: 'vertical', lineHeight: 1.8,
              }}
            />
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 12 }}>
              <button onClick={() => setEditing(false)} style={{
                padding: '6px 16px', borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-primary)', background: 'var(--bg-subtle)',
                cursor: 'pointer', fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)',
              }}>Cancel</button>
              <button onClick={handleSave} style={{
                padding: '6px 16px', borderRadius: 'var(--radius-sm)',
                border: 'none', background: 'var(--accent)', color: 'white',
                cursor: 'pointer', fontSize: 12, fontWeight: 500,
              }}>Save Formula</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ── Engineering Text Block ──────────────────────────────────────────── */
function EngineeringBlock({ moduleKey }) {
  const [expanded, setExpanded] = useState(false)
  const et = engineeringText['3.2']?.subsections?.[moduleKey]
  if (!et) return null

  return (
    <div style={{ marginBottom: 12 }}>
      <div onClick={() => setExpanded(!expanded)}
        style={{
          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
          userSelect: 'none', padding: '10px 14px',
        }}>
        <BookOpen size={14} style={{ color: 'var(--accent)', flexShrink: 0 }} />
        <span style={{
          fontWeight: 600, fontSize: 11, color: 'var(--accent)',
          textTransform: 'uppercase', letterSpacing: '0.04em', flex: 1,
        }}>Engineering Background — {et.title || moduleKey}</span>
        <span style={{ color: 'var(--text-tertiary)' }}>
          {expanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        </span>
      </div>
      {expanded && (
        <div style={{ padding: '0 14px 12px', fontSize: 12.5, lineHeight: 1.8, color: 'var(--text-secondary)' }}>
          {et.criteria && et.criteria.split('\n').map((p, i) => (
            <p key={i} style={{ margin: '0 0 4px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── Charts: Only for Excel-matching tables ──────────────────────────── */
function ModuleChart({ moduleKey, storeys }) {
  const chartHeight = 320

  if (moduleKey === '3.2.6') {
    return (
      <div className="excel-chart" style={{ marginTop: 16 }}>
        <div style={{ height: chartHeight }}>
          <Line {...stiffnessXLineChart(storeys)} />
        </div>
      </div>
    )
  }

  if (moduleKey === '3.2.7') {
    return (
      <div className="excel-chart" style={{ marginTop: 16 }}>
        <div style={{ height: chartHeight }}>
          <Line {...stiffnessYLineChart(storeys)} />
        </div>
      </div>
    )
  }

  return null
}

/* ── Displacement Comparison Charts ──────────────────────────────────── */
function DisplacementCharts({ storeys }) {
  const [showX, setShowX] = useState(true)
  const chartHeight = 350

  return (
    <div style={{ marginTop: 24 }}>
      <div style={{
        padding: '12px 16px', background: 'var(--bg-subtle)',
        borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)',
        marginBottom: 16,
      }}>
        <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: 'var(--text-primary)' }}>
          Elastic Spectrum Deflection versus Design Spectrum Deflection
        </h4>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setShowX(true)}
            style={{
              padding: '4px 14px', borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-primary)',
              background: showX ? 'var(--accent)' : 'var(--bg-surface)',
              color: showX ? 'white' : 'var(--text-secondary)',
              cursor: 'pointer', fontSize: 12, fontWeight: 500,
            }}>X-Direction</button>
          <button onClick={() => setShowX(false)}
            style={{
              padding: '4px 14px', borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-primary)',
              background: !showX ? 'var(--accent)' : 'var(--bg-surface)',
              color: !showX ? 'white' : 'var(--text-secondary)',
              cursor: 'pointer', fontSize: 12, fontWeight: 500,
            }}>Y-Direction</button>
        </div>
      </div>

      <div className="excel-chart">
        <div style={{ height: chartHeight }}>
          {showX
            ? <Bar {...displacementXBarChart(storeys)} />
            : <Bar {...displacementYBarChart(storeys)} />
          }
        </div>
      </div>

      <p style={{
        fontSize: 12, color: 'var(--text-tertiary)', marginTop: 8,
        fontStyle: 'italic', lineHeight: 1.6,
      }}>
        Based on analysis data, the Elastic Analysis will be taken for Analysis for Damage Limitation and Stability Analysis.
      </p>
    </div>
  )
}

/* ── Main Component ──────────────────────────────────────────────────── */
export default function CalculationTable({ storeys, module: activeModule, onSelectStorey, selectedStorey }) {
  const cols = columns[activeModule] || columns['3.2.2']
  const caption = tableCaptions[activeModule] || ''

  return (
    <div>
      <FormulaBlock moduleKey={activeModule} />
      <EngineeringBlock moduleKey={activeModule} />

      {/* Table */}
      <div className="excel-table-wrap">
        <div className="excel-table-header">
          <h4>Table {activeModule}</h4>
          <span className="count">{storeys.length} storeys</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="excel-table">
            <thead>
              <tr>{cols.map((col, i) => <th key={col.id || col.key || i}>{col.label}</th>)}</tr>
            </thead>
            <tbody>
              {storeys.map((storey) => {
                const isSelected = selectedStorey?.id === storey.id
                return (
                  <tr key={storey.id} className={isSelected ? 'selected' : ''}
                    onClick={() => onSelectStorey(storey)} style={{ cursor: 'pointer' }}>
                    {cols.map((col, ci) => {
                      // Special handling for duplicate keys (like ls in 3.2.5)
                      let val
                      if (col.id === 'ls_y') {
                        val = storey.ls  // same ls used for both X and Y
                      } else {
                        val = getNestedValue(storey, col.key)
                      }
                      const display = col.fmt ? col.fmt(val) : val
                      if (col.isStatus) {
                        const s = val || '—'
                        const cls = s === 'OK' ? 'pass' : s === 'NOT OK' ? 'fail' : 'na'
                        return <td key={col.id || col.key || ci} className={`status-cell ${cls}`}>{display}</td>
                      }
                      return <td key={col.id || col.key || ci} style={col.highlight ? { color: 'var(--accent)', fontWeight: 600 } : {}}>{display ?? '—'}</td>
                    })}
                  </tr>
                )
              })}
            </tbody>
            {caption && <caption>{caption}</caption>}
          </table>
        </div>
      </div>

      {/* Chart below table — only for 3.2.6 and 3.2.7 */}
      <ModuleChart moduleKey={activeModule} storeys={storeys} />

      {/* Displacement comparison charts — shown after table 3.2.8 */}
      {activeModule === '3.2.8' && (
        <DisplacementCharts storeys={storeys} />
      )}
    </div>
  )
}
