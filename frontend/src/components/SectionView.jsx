import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, AlertTriangle, BookOpen, Calculator, ChevronDown, ChevronRight, Pencil } from 'lucide-react'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { useState, useEffect } from 'react'
import { engineeringText } from '../data/engineeringText'
import { displacementXBarChart, displacementYBarChart } from '../config/chartConfig'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

/* ── Section metadata ─────────────────────────────────────────────────── */
const sectionMeta = {
  '2.4': {
    title: '2.4 — Loading Schedule',
    subtitle: 'Worksheet 2.4 Loading Groups',
    description: 'Permanent, imposed and seismic actions per floor group with dead load components, live load category, and seismic combination.',
  },
  '2.5': {
    title: '2.5 — Concrete Cover Check',
    subtitle: 'Worksheet 2.5 Bond-Cover Logic',
    description: 'Member-by-member concrete cover verification against Eurocode 2 bond and durability requirements.',
  },
  '3.3': {
    title: '3.3 — Building System Classification',
    subtitle: 'Lateral Force Participation Ratio',
    description: 'Classifies the building structural system based on the proportion of lateral force resisted by frame vs. wall elements.',
  },
  '3.4': {
    title: '3.4 — Behavioral Factor (q)',
    subtitle: 'Seismic Behavior Reduction Factor',
    description: 'Determines the q-factor used to reduce the elastic response spectrum based on structural system type and regularity.',
  },
  '4.1': {
    title: '4.1 — Base Shear',
    subtitle: 'Seismic Base Shear Force (Fb)',
    description: 'Calculates the design seismic base shear from the response spectrum, building weight, and modal periods.',
  },
  '4.2': {
    title: '4.2 — Modal Participation',
    subtitle: 'Fundamental Periods & Mass Participation',
    description: 'Reads ETABS modal analysis results: natural periods and mass participation ratios for the first 50 modes.',
  },
  '4.3': {
    title: '4.3 — Geometric Imperfection',
    subtitle: 'P-Delta Imperfection Forces',
    description: 'Calculates equivalent horizontal imperfection forces from cumulative vertical loads and imperfection ratio θi.',
  },
  '4.4': {
    title: '4.4 — Stability Analysis (P-Delta)',
    subtitle: 'Inter-Story Drift Sensitivity Coefficient',
    description: 'Evaluates second-order effects: θ = ΣPu·Δu / (Hu·hs). θ ≥ 0.1 indicates sway sensitivity.',
  },
  '4.5': {
    title: '4.5 — Storey Drift Control',
    subtitle: 'Damage Limitation Check',
    description: 'Verifies that inter-story drift satisfies ν·dr/h ≤ limit for damage limitation under design earthquake.',
  },
  '4.6': {
    title: '4.6 — Overturning Check',
    subtitle: 'Safety Factor Against Overturning',
    description: 'Checks that the ratio of resisting moment to overturning moment exceeds 1.5.',
  },
}

/* ── Helper components ────────────────────────────────────────────────── */
function SectionHeader({ meta }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h2 style={{
        fontSize: 20, fontWeight: 700, marginBottom: 4,
        letterSpacing: '-0.02em', color: 'var(--text-primary)',
      }}>
        {meta.title}
      </h2>
      <p style={{ color: 'var(--text-tertiary)', fontSize: 13 }}>{meta.description}</p>
    </div>
  )
}

function InfoCard({ label, value, unit = '' }) {
  return (
    <div className="data-card">
      <div className="label">{label}</div>
      <div className="value">
        {value !== null && value !== undefined && value !== '' ? value : '—'}
        {value !== null && value !== undefined && unit && <span className="unit">{unit}</span>}
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const s = String(status || '').toUpperCase()
  if (s === 'OK' || s === 'PASS' || s === 'NO SWAY') {
    return <span className="status-badge pass" style={{ display: 'inline-flex' }}><CheckCircle2 size={13} /> {status}</span>
  }
  if (s === 'NOT OK' || s === 'FAIL' || s === 'SWAY') {
    return <span className="status-badge fail" style={{ display: 'inline-flex' }}><XCircle size={13} /> {status}</span>
  }
  return <span style={{ color: 'var(--text-tertiary)', fontWeight: 500 }}>{status || '—'}</span>
}

/* ── Editable Formula Block (used in all sections) ────────────────────── */
function FormulaBlock({ sectionKey }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [customFormula, setCustomFormula] = useState('')
  const et = engineeringText[sectionKey]
  if (!et || !et.formula) return null

  const handleSave = () => {
    const stored = JSON.parse(localStorage.getItem('custom_formulas') || '{}')
    stored[sectionKey] = customFormula
    localStorage.setItem('custom_formulas', JSON.stringify(stored))
    setEditing(false)
  }

  const storedFormulas = JSON.parse(localStorage.getItem('custom_formulas') || '{}')
  const displayFormula = storedFormulas[sectionKey] || et.formula

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
        }}>
          Formula
        </span>
        <button
          onClick={(e) => {
            e.stopPropagation()
            setEditing(!editing)
            setCustomFormula(displayFormula)
          }}
          style={{
            background: 'none', border: '1px solid var(--border-primary)',
            borderRadius: 4, padding: '2px 6px', cursor: 'pointer',
            color: 'var(--text-tertiary)', fontSize: 10,
            display: 'flex', alignItems: 'center', gap: 3,
          }}
          title="Edit formula"
        >
          <Pencil size={10} /> Edit
        </button>
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
        }}>
          {displayFormula}
        </div>
      )}
      {editing && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 9999,
        }} onClick={() => setEditing(false)}>
          <div
            style={{
              background: 'var(--bg-surface)', borderRadius: 'var(--radius-lg)',
              padding: 24, width: 500, maxHeight: '80vh',
              boxShadow: 'var(--shadow-lg)', border: '1px solid var(--border-primary)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>
              Edit Formula
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-tertiary)', marginBottom: 12 }}>
              Enter the formula using mathematical notation or Excel-style format.
            </p>
            <textarea
              value={customFormula}
              onChange={(e) => setCustomFormula(e.target.value)}
              style={{
                width: '100%', minHeight: 120, padding: 12,
                fontFamily: "'JetBrains Mono', monospace", fontSize: 12,
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-sm)', background: 'var(--bg-subtle)',
                color: 'var(--text-primary)', resize: 'vertical',
                lineHeight: 1.8,
              }}
            />
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 12 }}>
              <button
                onClick={() => setEditing(false)}
                style={{
                  padding: '6px 16px', borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-primary)', background: 'var(--bg-subtle)',
                  cursor: 'pointer', fontSize: 12, fontWeight: 500,
                  color: 'var(--text-secondary)',
                }}
              >Cancel</button>
              <button
                onClick={handleSave}
                style={{
                  padding: '6px 16px', borderRadius: 'var(--radius-sm)',
                  border: 'none', background: 'var(--accent)', color: 'white',
                  cursor: 'pointer', fontSize: 12, fontWeight: 500,
                }}
              >Save Formula</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/* ── Engineering Text (expandable dropdown) ───────────────────────────── */
function EngineeringText({ sectionKey }) {
  const [expanded, setExpanded] = useState(false)
  const data = engineeringText[sectionKey]
  if (!data) return null

  return (
    <div style={{ marginBottom: 20 }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
          userSelect: 'none', padding: '12px 16px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-primary)',
          background: 'var(--bg-subtle)',
        }}
      >
        <BookOpen size={14} style={{ color: 'var(--accent)', flexShrink: 0 }} />
        <span style={{
          fontWeight: 600, fontSize: 11, color: 'var(--accent)',
          textTransform: 'uppercase', letterSpacing: '0.04em', flex: 1,
        }}>
          Engineering Background & Criteria
        </span>
        <span style={{ color: 'var(--text-tertiary)' }}>
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </span>
      </div>
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{ padding: '12px 16px', fontSize: 13, lineHeight: 1.8, color: 'var(--text-secondary)' }}
        >
          {data.background && (
            <div style={{ marginBottom: 12 }}>
              {data.background.split('\n').map((p, i) => (
                <p key={i} style={{ margin: '0 0 6px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
              ))}
            </div>
          )}
          {data.criteria && (
            <div style={{ marginTop: 8, fontSize: 12.5 }}>
              {data.criteria.split('\n').map((p, i) => (
                <p key={i} style={{ margin: '0 0 4px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}

function DataTable({ headers, rows }) {
  return (
    <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)' }}>
      <table className="calc-table">
        <thead>
          <tr>
            {headers.map((h, i) => <th key={i}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              {row.map((cell, ci) => {
                if (typeof cell === 'object' && cell !== null && !Array.isArray(cell)) {
                  const style = cell.highlight ? { color: 'var(--accent)', fontWeight: 600 } : {}
                  if (cell.status) {
                    return <td key={ci} style={style}><StatusBadge status={cell.text} /></td>
                  }
                  return <td key={ci} style={style}>{cell.text ?? '—'}</td>
                }
                return <td key={ci}>{cell ?? '—'}</td>
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ── Section 2.4 ──────────────────────────────────────────────────────── */
function Section24({ data }) {
  if (!data) return <EmptySection />
  const schedule = data.schedule || []
  return (
    <div>
      <SectionHeader meta={sectionMeta['2.4']} />
      <FormulaBlock sectionKey="2.4" />
      <EngineeringText sectionKey="2.4" />
      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Code Reference" value={data.code_reference} />
      </div>
      <DataTable
        headers={['Floor Group', 'Occupancy', 'Dead (kN/m²)', 'Live (kN/m²)', 'ψE', 'Factored Live', 'Seismic Total']}
        rows={schedule.map(s => [
          s.floor_group,
          s.occupancy,
          s.total_dead_knm2?.toFixed(2),
          s.live_knm2?.toFixed(2),
          s.psi_e?.toFixed(2),
          s.factored_live_knm2?.toFixed(2),
          { text: s.seismic_total_knm2?.toFixed(4), highlight: true },
        ])}
      />
    </div>
  )
}

/* ── Section 2.5 ──────────────────────────────────────────────────────── */
function Section25({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['2.5']} />
      <FormulaBlock sectionKey="2.5" />
      <EngineeringText sectionKey="2.5" />
      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Aggregate Size" value={data.aggregate_size} />
        <InfoCard label="Structural Class" value={data.structural_class} />
        <InfoCard label="Code Reference" value={data.code_reference} />
      </div>
      <div className="formula-box" style={{ marginBottom: 16 }}>
        <div className="formula">Cmin = max(Cmin,bond, Cmin,dur, 10mm); Cnom = Cmin + Cdev</div>
        <div className="description">{data.description}</div>
      </div>
      <DataTable
        headers={['Group', 'Member', 'Cmin,bond', 'Cmin,dur', 'Cmin', 'Cdev', 'Cnom', 'Selected', 'Status']}
        rows={(data.rows || []).map(r => [
          r.group,
          r.member,
          r.cmin_bond?.toFixed(0),
          r.cmin_dur?.toFixed(0),
          { text: r.cmin?.toFixed(0), highlight: true },
          r.cdev?.toFixed(0),
          r.cnom_calculated?.toFixed(0),
          r.selected_cover?.toFixed(0),
          { text: r.status, status: true },
        ])}
      />
    </div>
  )
}

/* ── Section 3.3 ──────────────────────────────────────────────────────── */
function Section33({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['3.3']} />
      <FormulaBlock sectionKey="3.3" />
      <EngineeringText sectionKey="3.3" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Building Classification" value={data.building_classification} />
        <InfoCard label="X Col %" value={data.x_direction?.column_pct ? (data.x_direction.column_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="X Wall %" value={data.x_direction?.wall_pct ? (data.x_direction.wall_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="Y Col %" value={data.y_direction?.column_pct ? (data.y_direction.column_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="Y Wall %" value={data.y_direction?.wall_pct ? (data.y_direction.wall_pct * 100).toFixed(1) + '%' : '—'} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div>
          <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            X-Direction (UL1)
          </h4>
          <DataTable
            headers={['Story', 'Lateral (kN)', 'Column', 'Wall', 'Col %', 'Wall %']}
            rows={(data.x_direction?.storeys || []).map(s => [
              s.name,
              s.lateral?.toFixed(0),
              s.column_force?.toFixed(0),
              s.wall_force?.toFixed(0),
              (s.column_pct * 100).toFixed(1) + '%',
              (s.wall_pct * 100).toFixed(1) + '%',
            ])}
          />
        </div>
        <div>
          <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            Y-Direction (UL2)
          </h4>
          <DataTable
            headers={['Story', 'Lateral (kN)', 'Column', 'Wall', 'Col %', 'Wall %']}
            rows={(data.y_direction?.storeys || []).map(s => [
              s.name,
              s.lateral?.toFixed(0),
              s.column_force?.toFixed(0),
              s.wall_force?.toFixed(0),
              (s.column_pct * 100).toFixed(1) + '%',
              (s.wall_pct * 100).toFixed(1) + '%',
            ])}
          />
        </div>
      </div>
    </div>
  )
}

/* ── Section 3.4 ──────────────────────────────────────────────────────── */
function Section34({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['3.4']} />
      <FormulaBlock sectionKey="3.4" />
      <EngineeringText sectionKey="3.4" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Building Type" value={data.building_type} />
        <InfoCard label="q₀" value={data.qo} />
        <InfoCard label="kw" value={data.kw} />
        <InfoCard label="αu/α1" value={data.alpha_ratio} />
        <InfoCard label="q (X)" value={data.qx} />
        <InfoCard label="q (Y)" value={data.qy} />
        <InfoCard label="q (design)" value={data.q} />
        <InfoCard label="Plan Regularity" value={data.regularity_plan} />
        <InfoCard label="Elevation Regularity" value={data.regularity_elevation} />
      </div>

      <div className="formula-box">
        <div className="formula">q = q₀ × kw × (αu/α1)</div>
        <div className="description">{data.description}</div>
      </div>
    </div>
  )
}

/* ── Section 4.1 ──────────────────────────────────────────────────────── */
function Section41({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.1']} />
      <FormulaBlock sectionKey="4.1" />
      <EngineeringText sectionKey="4.1" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="ag" value={data.ag} unit="g" />
        <InfoCard label="Ground Type" value={data.ground_type} />
        <InfoCard label="S" value={data.S} />
        <InfoCard label="TB" value={data.TB} unit="s" />
        <InfoCard label="TC" value={data.TC} unit="s" />
        <InfoCard label="TD" value={data.TD} unit="s" />
        <InfoCard label="β" value={data.beta} />
        <InfoCard label="q" value={data.q} />
      </div>

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="T1x" value={data.T1x?.toFixed(3)} unit="s" />
        <InfoCard label="T1y" value={data.T1y?.toFixed(3)} unit="s" />
        <InfoCard label="Sd(T)x" value={data.Sd_x_pct?.toFixed(1)} unit="%" />
        <InfoCard label="Sd(T)y" value={data.Sd_y_pct?.toFixed(1)} unit="%" />
        <InfoCard label="Total Weight" value={data.total_weight_kN?.toFixed(0)} unit="kN" />
        <InfoCard label="λ" value={data.lambda} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--cyan)' }}>X-Direction</div>
          <div className="description">
            Modal participation: {(data.modal_ratio_x * 100)?.toFixed(1)}%<br />
            Fb = {data.Fb_x?.toFixed(2)} kN<br />
            Lower bound check: {data.lower_bound_x?.toFixed(2)} kN
          </div>
        </div>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--orange)' }}>Y-Direction</div>
          <div className="description">
            Modal participation: {(data.modal_ratio_y * 100)?.toFixed(1)}%<br />
            Fb = {data.Fb_y?.toFixed(2)} kN<br />
            Lower bound check: {data.lower_bound_y?.toFixed(2)} kN
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Section 4.2 ──────────────────────────────────────────────────────── */
function Section42({ data }) {
  if (!data) return <EmptySection />
  const modes = data.modes || []
  const top10 = modes.slice(0, 10)

  return (
    <div>
      <SectionHeader meta={sectionMeta['4.2']} />
      <FormulaBlock sectionKey="4.2" />
      <EngineeringText sectionKey="4.2" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Total Modes" value={data.total_modes} />
        <InfoCard label="T1x" value={data.T1x?.toFixed(3)} unit="s" />
        <InfoCard label="T1y" value={data.T1y?.toFixed(3)} unit="s" />
        <InfoCard label="Mass X (Mode 1)" value={data.mass_x?.toFixed(1)} unit="%" />
        <InfoCard label="Mass Y (Mode 1)" value={data.mass_y?.toFixed(1)} unit="%" />
      </div>

      <DataTable
        headers={['Mode', 'Period (s)', 'UX (%)', 'UY (%)', 'RZ (%)', 'ΣUX (%)', 'ΣUY (%)']}
        rows={top10.map(m => [
          m.mode,
          m.period?.toFixed(4),
          m.ux?.toFixed(4),
          m.uy?.toFixed(4),
          m.rz?.toFixed(4),
          m.sum_ux?.toFixed(2),
          m.sum_uy?.toFixed(2),
        ])}
      />
    </div>
  )
}

/* ── Section 4.3 ──────────────────────────────────────────────────────── */
function Section43({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.3']} />
      <FormulaBlock sectionKey="4.3" />
      <EngineeringText sectionKey="4.3" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="θ₀" value={data.theta0} />
        <InfoCard label="αh" value={data.alpha_h} />
        <InfoCard label="αm" value={data.alpha_m} />
        <InfoCard label="θi" value={data.theta_i} />
      </div>
      <div className="formula-box" style={{ marginBottom: 20 }}>
        <div className="formula">θi = θ₀ × αh × αm = {data.description || `${data.theta0} × ${data.alpha_h} × ${data.alpha_m} = ${data.theta_i}`}</div>
      </div>
      <DataTable
        headers={['Story', 'Ptot (kN)', 'θ₀', 'L(h)', 'm', 'αh', 'αm', 'θi', 'Hi (kN)']}
        rows={(data.storeys || []).map(s => [
          s.name,
          s.ptot?.toFixed(0),
          s.theta0,
          s.l_h?.toFixed(2),
          s.m,
          s.alpha_h,
          s.alpha_m,
          s.theta_i?.toFixed(6),
          { text: s.hi?.toFixed(2), highlight: true },
        ])}
      />
    </div>
  )
}

/* ── Section 4.4 ──────────────────────────────────────────────────────── */
function Section44({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.4']} />
      <FormulaBlock sectionKey="4.4" />
      <EngineeringText sectionKey="4.4" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Max θ (X)" value={data.max_theta_x?.toFixed(4)} />
        <InfoCard label="Max θ (Y)" value={data.max_theta_y?.toFixed(4)} />
        <InfoCard label="X Status" value="" />
        <InfoCard label="Y Status" value="" />
      </div>
      <div style={{ marginBottom: 20, display: 'flex', gap: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontWeight: 500 }}>X:</span> <StatusBadge status={data.max_classification_x} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontWeight: 500 }}>Y:</span> <StatusBadge status={data.max_classification_y} />
        </div>
      </div>
      <DataTable
        headers={['Story', 'Load Case', 'Dir', 'Ptot (kN)', 'Hu (kN)', 'Δu (m)', 'Height (m)', 'θ', 'Status']}
        rows={(data.storeys || []).map(s => [
          s.name,
          s.load_case,
          s.direction,
          s.ptot?.toFixed(0),
          s.hu?.toFixed(0),
          s.delta_u?.toFixed(6),
          s.height?.toFixed(2),
          s.theta?.toFixed(6),
          { text: s.classification, status: true },
        ])}
      />
    </div>
  )
}

/* ── Section 4.5 ──────────────────────────────────────────────────────── */
function Section45({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.5']} />
      <FormulaBlock sectionKey="4.5" />
      <EngineeringText sectionKey="4.5" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="ν" value={data.nu} />
        <InfoCard label="Limit" value={data.limit} />
        <InfoCard label="Max Ratio (X)" value={data.max_ratio_x?.toFixed(6)} />
        <InfoCard label="Max Ratio (Y)" value={data.max_ratio_y?.toFixed(6)} />
        <InfoCard label="X Status" value={data.max_status_x} />
        <InfoCard label="Y Status" value={data.max_status_y} />
      </div>
      <DataTable
        headers={['Story', 'Load Case', 'dr X (m)', 'dr Y (m)', 'ν·dr/h (X)', 'ν·dr/h (Y)', 'Limit', 'X Status', 'Y Status']}
        rows={(data.storeys || []).map(s => [
          s.name,
          s.load_case,
          s.dr_x?.toFixed(6),
          s.dr_y?.toFixed(6),
          s.nu_dr_h_x?.toFixed(6),
          s.nu_dr_h_y?.toFixed(6),
          s.limit,
          { text: s.status_x, status: true },
          { text: s.status_y, status: true },
        ])}
      />
    </div>
  )
}

/* ── Section 4.6 ──────────────────────────────────────────────────────── */
function Section46({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.6']} />
      <FormulaBlock sectionKey="4.6" />
      <EngineeringText sectionKey="4.6" />

      <div className="data-grid" style={{ marginBottom: 20 }}>
        <InfoCard label="Total Weight" value={data.total_weight_kN?.toFixed(0)} unit="kN" />
        <InfoCard label="Ground Xcm" value={data.ground_xcm?.toFixed(3)} unit="m" />
        <InfoCard label="Ground Ycm" value={data.ground_ycm?.toFixed(3)} unit="m" />
        <InfoCard label="Required SF" value={data.required_sf} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--cyan)' }}>X-Direction</div>
          <div className="description">
            Overturning: {data.x_direction?.total_ot_moment?.toFixed(0)} kN·m<br />
            Resisting: {data.x_direction?.resisting_moment?.toFixed(0)} kN·m<br />
            <strong style={{ color: 'var(--text-primary)' }}>Safety Factor: {data.x_direction?.safety_factor?.toFixed(2)}</strong>
          </div>
          <div style={{ marginTop: 8 }}><StatusBadge status={data.x_direction?.passes ? 'PASS' : 'FAIL'} /></div>
        </div>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--orange)' }}>Y-Direction</div>
          <div className="description">
            Overturning: {data.y_direction?.total_ot_moment?.toFixed(0)} kN·m<br />
            Resisting: {data.y_direction?.resisting_moment?.toFixed(0)} kN·m<br />
            <strong style={{ color: 'var(--text-primary)' }}>Safety Factor: {data.y_direction?.safety_factor?.toFixed(2)}</strong>
          </div>
          <div style={{ marginTop: 8 }}><StatusBadge status={data.y_direction?.passes ? 'PASS' : 'FAIL'} /></div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div>
          <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            X-Direction Storeys
          </h4>
          <DataTable
            headers={['Story', 'Elevation (m)', 'Shear (kN)', 'OT Moment (kN·m)']}
            rows={(data.x_direction?.storeys || []).map(s => [
              s.name,
              s.elevation?.toFixed(2),
              s.shear?.toFixed(0),
              { text: s.ot_moment?.toFixed(0), highlight: true },
            ])}
          />
        </div>
        <div>
          <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            Y-Direction Storeys
          </h4>
          <DataTable
            headers={['Story', 'Elevation (m)', 'Shear (kN)', 'OT Moment (kN·m)']}
            rows={(data.y_direction?.storeys || []).map(s => [
              s.name,
              s.elevation?.toFixed(2),
              s.shear?.toFixed(0),
              { text: s.ot_moment?.toFixed(0), highlight: true },
            ])}
          />
        </div>
      </div>
    </div>
  )
}

/* ── Empty state ──────────────────────────────────────────────────────── */
function EmptySection() {
  return (
    <div className="empty-state" style={{ height: '40vh' }}>
      <AlertTriangle size={48} strokeWidth={1.2} />
      <h2>No Data Available</h2>
      <p>This section requires extended data import. Make sure the Access database contains the necessary tables.</p>
    </div>
  )
}

/* ── Main SectionView ─────────────────────────────────────────────────── */
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function useStandaloneData(section) {
  const [data, setData] = useState(null)
  useEffect(() => {
    if (section === '2.4') {
      fetch(`${API}/api/loading-schedule`).then(r => r.json()).then(setData).catch(() => {})
    } else if (section === '2.5') {
      fetch(`${API}/api/concrete-cover`).then(r => r.json()).then(setData).catch(() => {})
    }
  }, [section])
  return data
}

export default function SectionView({ section, project }) {
  const standaloneData = useStandaloneData(section)
  const data = section === '2.4' || section === '2.5' ? standaloneData : project?.sections?.[section]

  const fade = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 } }

  return (
    <motion.div {...fade} key={section}>
      {section === '2.4' && <Section24 data={data} />}
      {section === '2.5' && <Section25 data={data} />}
      {section === '3.3' && <Section33 data={data} />}
      {section === '3.4' && <Section34 data={data} />}
      {section === '4.1' && <Section41 data={data} />}
      {section === '4.2' && <Section42 data={data} />}
      {section === '4.3' && <Section43 data={data} />}
      {section === '4.4' && <Section44 data={data} />}
      {section === '4.5' && <Section45 data={data} />}
      {section === '4.6' && <Section46 data={data} />}
    </motion.div>
  )
}
