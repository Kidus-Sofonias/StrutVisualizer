import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, AlertTriangle, BookOpen, Calculator, ChevronDown, ChevronRight } from 'lucide-react'
import { Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { useState } from 'react'
import { engineeringText } from '../data/engineeringText'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

/* ── Section metadata ─────────────────────────────────────────────────── */
const sectionMeta = {
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
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>{meta.title}</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>{meta.description}</p>
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
    return <span style={{ color: 'var(--pass)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 4 }}><CheckCircle2 size={14} /> {status}</span>
  }
  if (s === 'NOT OK' || s === 'FAIL' || s === 'SWAY') {
    return <span style={{ color: 'var(--fail)', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 4 }}><XCircle size={14} /> {status}</span>
  }
  return <span style={{ color: 'var(--text-muted)' }}>{status || '—'}</span>
}

function EngineeringText({ sectionKey, subKey }) {
  const data = engineeringText[sectionKey]
  if (!data) return null
  const sub = subKey ? data.subsections?.[subKey] : data
  if (!sub) return null

  const [expanded, setExpanded] = useState(false)

  return (
    <div className="engineering-text" style={{
      background: 'var(--bg-secondary)', borderRadius: 8, padding: '16px 20px',
      marginBottom: 20, border: '1px solid var(--border)',
    }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, userSelect: 'none' }}
      >
        <BookOpen size={16} style={{ color: 'var(--accent)' }} />
        <span style={{ fontWeight: 600, fontSize: 13, color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Engineering Background & Criteria
        </span>
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)' }}>
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </span>
      </div>
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{ marginTop: 12, fontSize: 13, lineHeight: 1.7, color: 'var(--text)' }}
        >
          {sub.background && (
            <div style={{ marginBottom: 12 }}>
              {sub.background.split('\n').map((p, i) => (
                <p key={i} style={{ margin: '0 0 8px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
              ))}
            </div>
          )}
          {sub.formula && (
            <div style={{
              background: 'var(--bg-primary)', borderRadius: 6, padding: '10px 14px',
              fontFamily: 'monospace', fontSize: 12, marginBottom: 12,
              borderLeft: '3px solid var(--accent)', whiteSpace: 'pre-wrap',
            }}>
              <div style={{ fontSize: 11, color: 'var(--accent)', marginBottom: 4, fontFamily: 'sans-serif', fontWeight: 600 }}>
                <Calculator size={12} style={{ display: 'inline', verticalAlign: -2 }} /> Formula:
              </div>
              {sub.formula}
            </div>
          )}
          {sub.criteria && (
            <div style={{ fontSize: 13, lineHeight: 1.7 }}>
              {sub.criteria.split('\n').map((p, i) => (
                <p key={i} style={{ margin: '0 0 6px 0', whiteSpace: 'pre-wrap' }}>{p}</p>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}

function ChartCard({ title, children }) {
  return (
    <div style={{
      background: 'var(--bg-secondary)', borderRadius: 8, padding: 20,
      marginBottom: 20, border: '1px solid var(--border)',
    }}>
      <h4 style={{ fontSize: 13, color: 'var(--accent)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>{title}</h4>
      <div style={{ position: 'relative', height: 300 }}>
        {children}
      </div>
    </div>
  )
}

function DataTable({ headers, rows, onRowClick }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="calc-table">
        <thead>
          <tr>
            {headers.map((h, i) => <th key={i}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} onClick={onRowClick} style={onRowClick ? { cursor: 'pointer' } : {}}>
              {row.map((cell, ci) => {
                if (typeof cell === 'object' && cell !== null) {
                  const style = cell.highlight ? { color: 'var(--cyan)', fontWeight: 600 } : {}
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

/* ── Chart config helpers ─────────────────────────────────────────────── */
const chartColors = {
  cyan: 'rgba(0, 210, 255, 1)',
  cyanFill: 'rgba(0, 210, 255, 0.15)',
  orange: 'rgba(255, 165, 0, 1)',
  orangeFill: 'rgba(255, 165, 0, 0.15)',
  green: 'rgba(75, 192, 192, 1)',
  red: 'rgba(255, 99, 132, 1)',
  purple: 'rgba(153, 102, 255, 1)',
}

const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: 'var(--text)', font: { size: 11 } } },
  },
  scales: {
    x: { ticks: { color: 'var(--text-muted)', font: { size: 10 } }, grid: { color: 'var(--border)' } },
    y: { ticks: { color: 'var(--text-muted)', font: { size: 10 } }, grid: { color: 'var(--border)' } },
  },
}

/* ── Section 3.3 ──────────────────────────────────────────────────────── */
function Section33({ data }) {
  if (!data) return <EmptySection />
  const et = engineeringText['3.3']

  return (
    <div>
      <SectionHeader meta={sectionMeta['3.3']} />
      <EngineeringText sectionKey="3.3" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="Building Classification" value={data.building_classification} />
        <InfoCard label="X Col %" value={data.x_direction?.column_pct ? (data.x_direction.column_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="X Wall %" value={data.x_direction?.wall_pct ? (data.x_direction.wall_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="Y Col %" value={data.y_direction?.column_pct ? (data.y_direction.column_pct * 100).toFixed(1) + '%' : '—'} />
        <InfoCard label="Y Wall %" value={data.y_direction?.wall_pct ? (data.y_direction.wall_pct * 100).toFixed(1) + '%' : '—'} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <h4 style={{ fontSize: 13, color: 'var(--accent)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>X-Direction (UL1)</h4>
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
          <ChartCard title="X-Direction Force Distribution">
            <Bar data={{
              labels: (data.x_direction?.storeys || []).map(s => s.name),
              datasets: [
                { label: 'Column %', data: (data.x_direction?.storeys || []).map(s => s.column_pct * 100), backgroundColor: chartColors.cyan, borderRadius: 2 },
                { label: 'Wall %', data: (data.x_direction?.storeys || []).map(s => s.wall_pct * 100), backgroundColor: chartColors.orange, borderRadius: 2 },
              ],
            }} options={{ ...defaultChartOptions, indexAxis: 'y', scales: { ...defaultChartOptions.scales, x: { ...defaultChartOptions.scales.x, max: 100 } }, plugins: { ...defaultChartOptions.plugins, title: { display: true, text: 'Column vs Wall Participation (%)', color: 'var(--text)' } } }} />
          </ChartCard>
        </div>
        <div>
          <h4 style={{ fontSize: 13, color: 'var(--accent)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>Y-Direction (UL2)</h4>
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
          <ChartCard title="Y-Direction Force Distribution">
            <Bar data={{
              labels: (data.y_direction?.storeys || []).map(s => s.name),
              datasets: [
                { label: 'Column %', data: (data.y_direction?.storeys || []).map(s => s.column_pct * 100), backgroundColor: chartColors.cyan, borderRadius: 2 },
                { label: 'Wall %', data: (data.y_direction?.storeys || []).map(s => s.wall_pct * 100), backgroundColor: chartColors.orange, borderRadius: 2 },
              ],
            }} options={{ ...defaultChartOptions, indexAxis: 'y', scales: { ...defaultChartOptions.scales, x: { ...defaultChartOptions.scales.x, max: 100 } }, plugins: { ...defaultChartOptions.plugins, title: { display: true, text: 'Column vs Wall Participation (%)', color: 'var(--text)' } } }} />
          </ChartCard>
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
      <EngineeringText sectionKey="3.4" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
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
      <EngineeringText sectionKey="4.1" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="ag" value={data.ag} unit="g" />
        <InfoCard label="Ground Type" value={data.ground_type} />
        <InfoCard label="S" value={data.S} />
        <InfoCard label="TB" value={data.TB} unit="s" />
        <InfoCard label="TC" value={data.TC} unit="s" />
        <InfoCard label="TD" value={data.TD} unit="s" />
        <InfoCard label="β" value={data.beta} />
        <InfoCard label="q" value={data.q} />
      </div>

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="T1x" value={data.T1x?.toFixed(3)} unit="s" />
        <InfoCard label="T1y" value={data.T1y?.toFixed(3)} unit="s" />
        <InfoCard label="Sd(T)x" value={data.Sd_x_pct?.toFixed(1)} unit="%" />
        <InfoCard label="Sd(T)y" value={data.Sd_y_pct?.toFixed(1)} unit="%" />
        <InfoCard label="Total Weight" value={data.total_weight_kN?.toFixed(0)} unit="kN" />
        <InfoCard label="λ" value={data.lambda} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
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
      <EngineeringText sectionKey="4.2" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
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

      <ChartCard title="Modal Mass Participation (Cumulative)">
        <Line data={{
          labels: top10.map(m => `Mode ${m.mode}`),
          datasets: [
            { label: 'ΣUX (%)', data: top10.map(m => m.sum_ux), borderColor: chartColors.cyan, backgroundColor: chartColors.cyanFill, fill: true, tension: 0.3 },
            { label: 'ΣUY (%)', data: top10.map(m => m.sum_uy), borderColor: chartColors.orange, backgroundColor: chartColors.orangeFill, fill: true, tension: 0.3 },
          ],
        }} options={defaultChartOptions} />
      </ChartCard>
    </div>
  )
}

/* ── Section 4.3 ──────────────────────────────────────────────────────── */
function Section43({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.3']} />
      <EngineeringText sectionKey="4.3" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="θ₀" value={data.theta0} />
        <InfoCard label="αh" value={data.alpha_h} />
        <InfoCard label="αm" value={data.alpha_m} />
        <InfoCard label="θi" value={data.theta_i} />
      </div>
      <div className="formula-box" style={{ marginBottom: 24 }}>
        <div className="formula">θi = θ₀ × αh × αm = {data.description || `${data.theta0} × ${data.alpha_h} × ${data.alpha_m} = ${data.theta_i}`}</div>
      </div>
      <DataTable
        headers={['Story', 'Ptot (kN)', 'Height (m)', 'θi', 'Hi (kN)']}
        rows={(data.storeys || []).map(s => [
          s.name,
          s.ptot?.toFixed(0),
          s.height?.toFixed(2),
          s.theta_i?.toFixed(6),
          { text: s.hi?.toFixed(2), highlight: true },
        ])}
      />

      <ChartCard title="Geometric Imperfection Forces (Hi) Along Height">
        <Bar data={{
          labels: (data.storeys || []).map(s => s.name),
          datasets: [{
            label: 'Hi (kN)',
            data: (data.storeys || []).map(s => s.hi),
            backgroundColor: chartColors.cyan,
            borderRadius: 3,
          }],
        }} options={{ ...defaultChartOptions, indexAxis: 'y', plugins: { ...defaultChartOptions.plugins, title: { display: true, text: 'Transversal Imperfection Force per Storey', color: 'var(--text)' } } }} />
      </ChartCard>
    </div>
  )
}

/* ── Section 4.4 ──────────────────────────────────────────────────────── */
function Section44({ data }) {
  if (!data) return <EmptySection />
  return (
    <div>
      <SectionHeader meta={sectionMeta['4.4']} />
      <EngineeringText sectionKey="4.4" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="Max θ (X)" value={data.max_theta_x?.toFixed(4)} />
        <InfoCard label="Max θ (Y)" value={data.max_theta_y?.toFixed(4)} />
        <InfoCard label="X Status" value="" />
        <InfoCard label="Y Status" value="" />
      </div>
      <div style={{ marginBottom: 24, display: 'flex', gap: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span>X:</span> <StatusBadge status={data.max_classification_x} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span>Y:</span> <StatusBadge status={data.max_classification_y} />
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
      <EngineeringText sectionKey="4.5" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="ν" value={data.nu} />
        <InfoCard label="Limit" value={data.limit} />
        <InfoCard label="Max Ratio (X)" value={data.max_ratio_x?.toFixed(6)} />
        <InfoCard label="Max Ratio (Y)" value={data.max_ratio_y?.toFixed(6)} />
        <InfoCard label="X Status" value={data.max_status_x} />
        <InfoCard label="Y Status" value={data.max_status_y} />
      </div>
      <DataTable
        headers={['Story', 'Load Case', 'Dir', 'Height (m)', 'dr (m)', 'ν·dr/h', 'Limit', 'Status']}
        rows={(data.storeys || []).map(s => [
          s.name,
          s.load_case,
          s.direction,
          s.height?.toFixed(2),
          s.dr?.toFixed(6),
          s.nu_dr_h?.toFixed(6),
          s.limit,
          { text: s.status, status: true },
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
      <EngineeringText sectionKey="4.6" />

      <div className="data-grid" style={{ marginBottom: 24 }}>
        <InfoCard label="Total Weight" value={data.total_weight_kN?.toFixed(0)} unit="kN" />
        <InfoCard label="Ground Xcm" value={data.ground_xcm?.toFixed(3)} unit="m" />
        <InfoCard label="Ground Ycm" value={data.ground_ycm?.toFixed(3)} unit="m" />
        <InfoCard label="Required SF" value={data.required_sf} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--cyan)' }}>X-Direction</div>
          <div className="description">
            Overturning: {data.x_direction?.total_ot_moment?.toFixed(0)} kN·m<br />
            Resisting: {data.x_direction?.resisting_moment?.toFixed(0)} kN·m<br />
            <strong>Safety Factor: {data.x_direction?.safety_factor?.toFixed(2)}</strong>
          </div>
          <div style={{ marginTop: 8 }}><StatusBadge status={data.x_direction?.passes ? 'PASS' : 'FAIL'} /></div>
        </div>
        <div className="formula-box">
          <div className="formula" style={{ color: 'var(--orange)' }}>Y-Direction</div>
          <div className="description">
            Overturning: {data.y_direction?.total_ot_moment?.toFixed(0)} kN·m<br />
            Resisting: {data.y_direction?.resisting_moment?.toFixed(0)} kN·m<br />
            <strong>Safety Factor: {data.y_direction?.safety_factor?.toFixed(2)}</strong>
          </div>
          <div style={{ marginTop: 8 }}><StatusBadge status={data.y_direction?.passes ? 'PASS' : 'FAIL'} /></div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <h4 style={{ fontSize: 13, color: 'var(--accent)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>X-Direction Storeys</h4>
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
          <h4 style={{ fontSize: 13, color: 'var(--accent)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>Y-Direction Storeys</h4>
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

      <ChartCard title="Overturning vs Resisting Moment">
        <Bar data={{
          labels: ['X-Direction', 'Y-Direction'],
          datasets: [
            { label: 'Overturning Moment (kN·m)', data: [data.x_direction?.total_ot_moment, data.y_direction?.total_ot_moment], backgroundColor: chartColors.red, borderRadius: 4 },
            { label: 'Resisting Moment (kN·m)', data: [data.x_direction?.resisting_moment, data.y_direction?.resisting_moment], backgroundColor: chartColors.green, borderRadius: 4 },
          ],
        }} options={{ ...defaultChartOptions, plugins: { ...defaultChartOptions.plugins, title: { display: true, text: 'Safety Factor: X=' + data.x_direction?.safety_factor?.toFixed(2) + ', Y=' + data.y_direction?.safety_factor?.toFixed(2), color: 'var(--text)' } } }} />
      </ChartCard>
    </div>
  )
}

/* ── Empty state ──────────────────────────────────────────────────────── */
function EmptySection() {
  return (
    <div className="empty-state" style={{ height: '40vh' }}>
      <AlertTriangle size={48} strokeWidth={1} />
      <h2>No Data Available</h2>
      <p>This section requires extended data import. Make sure the Access database contains the necessary tables.</p>
    </div>
  )
}

/* ── Main SectionView ─────────────────────────────────────────────────── */
export default function SectionView({ section, project }) {
  const data = project?.sections?.[section]

  const fade = { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 } }

  return (
    <motion.div {...fade} key={section}>
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
