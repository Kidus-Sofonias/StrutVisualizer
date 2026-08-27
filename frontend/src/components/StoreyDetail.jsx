import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Minus } from 'lucide-react'

const moduleConfig = {
  '3.2.1': { title: 'Plan Regularity', formula: 'λ = Lmax / Lmin', criterion: 'λ < 4' },
  '3.2.2': { title: 'Structural Eccentricity', formula: 'eox = Xcm − Xcr, eoy = Ycm − Ycr', criterion: 'Informational' },
  '3.2.3': { title: 'Torsional Radius', formula: 'rx = √(KMT/KFY), ry = √(KMT/KFX)', criterion: 'Intermediate' },
  '3.2.4': { title: 'Eccentricity vs Gyration', formula: '|eox| ≤ 0.3·rx, |eoy| ≤ 0.3·ry', criterion: 'Both must be OK' },
  '3.2.5': { title: 'Torsional vs Gyration', formula: 'rx ≥ ls, ry ≥ ls', criterion: 'Both must be OK' },
  '3.2.6': { title: 'Storey Stiffness X', formula: 'Ki > 0.7 · Ki+1', criterion: 'Inter-storey comparison' },
  '3.2.7': { title: 'Storey Stiffness Y', formula: 'Ki > 0.7 · Ki+1', criterion: 'Inter-storey comparison' },
  '3.2.8': { title: 'Mass Distribution', formula: 'Mi < 2·Mi+1, Mi < 2·Mi-1', criterion: 'Both must be OK' },
}

function StatusIcon({ status }) {
  if (status === 'OK' || status === 'pass') return <CheckCircle2 size={16} style={{ color: 'var(--pass)' }} />
  if (status === 'NOT OK' || status === 'fail') return <XCircle size={16} style={{ color: 'var(--fail)' }} />
  return <Minus size={16} style={{ color: 'var(--text-muted)' }} />
}

function DataCard({ label, value, unit = 'm' }) {
  return (
    <div className="data-card">
      <div className="label">{label}</div>
      <div className="value">
        {value !== null && value !== undefined ? (
          typeof value === 'number' ? value.toFixed(3) : value
        ) : '—'}
        {value !== null && value !== undefined && <span className="unit">{unit}</span>}
      </div>
    </div>
  )
}

export default function StoreyDetail({ storey, module: activeModule, projectName }) {
  const config = moduleConfig[activeModule]
  // API returns flat properties, not nested source_data/calculations
  const sd = {
    xcm: storey.xcm,
    ycm: storey.ycm,
    xcr: storey.xcr,
    ycr: storey.ycr,
    mass: storey.mass,
    elevation: storey.elevation,
    ux_ul1: storey.ux_ul1,
    uy_ul2: storey.uy_ul2,
    rz_ul3: storey.rz_ul3,
    vx_ul1: storey.vx_ul1,
    vy_ul2: storey.vy_ul2,
    vx_eqx: storey.vx_eqx,
    vy_eqy: storey.vy_eqy,
    ux_eqx: storey.ux_eqx,
    uy_eqx: storey.uy_eqx,
    ux_eqy: storey.ux_eqy,
    uy_eqy: storey.uy_eqy,
  }
  const c = {
    eox: storey.eox,
    eoy: storey.eoy,
    rx: storey.rx,
    ry: storey.ry,
    kfx: storey.kfx,
    kfy: storey.kfy,
    kmt: storey.kmt,
    kx: storey.kx,
    ky: storey.ky,
    ls: storey.ls,
    module_3_2_1_status: storey.module_3_2_1_status,
    module_3_2_1_lambda: storey.module_3_2_1_lambda,
    module_3_2_4_eox_status: storey.module_3_2_4_eox_status,
    module_3_2_4_eoy_status: storey.module_3_2_4_eoy_status,
    module_3_2_4_limit_x: storey.module_3_2_4_limit_x,
    module_3_2_4_limit_y: storey.module_3_2_4_limit_y,
    module_3_2_5_rx_status: storey.module_3_2_5_rx_status,
    module_3_2_5_ry_status: storey.module_3_2_5_ry_status,
    module_3_2_6_status: storey.module_3_2_6_status,
    module_3_2_7_status: storey.module_3_2_7_status,
    module_3_2_8_mass: storey.module_3_2_8_mass,
    module_3_2_8_status_upper: storey.module_3_2_8_status_upper,
    module_3_2_8_status_lower: storey.module_3_2_8_status_lower,
  }

  const fade = {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  }

  return (
    <motion.div key={`${storey.id}-${activeModule}`} {...fade}>
      <div className="detail-header">
        <h2>{storey.name}</h2>
        <span className={`status-badge ${storey.overall_classification === 'PASS' ? 'pass' : 'fail'}`}>
          {storey.overall_classification === 'PASS' ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
          {storey.overall_classification}
        </span>
      </div>

      {/* Module Info */}
      <div className="detail-section">
        <div className="detail-section-title">Module {activeModule} — {config.title}</div>
        <div className="formula-box">
          <div className="formula">{config.formula}</div>
          <div className="description">Criterion: {config.criterion}</div>
        </div>
      </div>

      {/* Source Data */}
      <div className="detail-section">
        <div className="detail-section-title">Source Data (Access/ETABS)</div>
        <div className="data-grid">
          <DataCard label="Xcm" value={sd.xcm} />
          <DataCard label="Ycm" value={sd.ycm} />
          <DataCard label="Xcr" value={sd.xcr} />
          <DataCard label="Ycr" value={sd.ycr} />
          <DataCard label="Mass" value={sd.mass} unit="×10³ kg" />
          <DataCard label="Elevation" value={sd.elevation} />
        </div>
      </div>

      {/* Calculated Values */}
      <div className="detail-section">
        <div className="detail-section-title">Calculated Values</div>
        <div className="data-grid">
          {(activeModule === '3.2.2' || activeModule === '3.2.4') && (
            <>
              <DataCard label="eox" value={c.eox} />
              <DataCard label="eoy" value={c.eoy} />
            </>
          )}
          {activeModule === '3.2.3' && (
            <>
              <DataCard label="KFX" value={c.kfx} unit="kN/m" />
              <DataCard label="KFY" value={c.kfy} unit="kN/m" />
              <DataCard label="KMT" value={c.kmt} unit="kN/m" />
              <DataCard label="rx" value={c.rx} />
              <DataCard label="ry" value={c.ry} />
            </>
          )}
          {activeModule === '3.2.4' && (
            <>
              <DataCard label="0.3·rx" value={c.module_3_2_4_limit_x} />
              <DataCard label="0.3·ry" value={c.module_3_2_4_limit_y} />
            </>
          )}
          {activeModule === '3.2.5' && (
            <>
              <DataCard label="rx" value={c.rx} />
              <DataCard label="ls" value={c.ls} />
              <DataCard label="ry" value={c.ry} />
            </>
          )}
          {activeModule === '3.2.6' && (
            <>
              <DataCard label="Kx" value={c.kx} unit="kN/m" />
              <DataCard label="VX (EQX)" value={sd.vx_eqx} unit="kN" />
              <DataCard label="UX (EQX)" value={sd.ux_eqx} unit="m" />
            </>
          )}
          {activeModule === '3.2.7' && (
            <>
              <DataCard label="Ky" value={c.ky} unit="kN/m" />
              <DataCard label="VY (EQY)" value={sd.vy_eqy} unit="kN" />
              <DataCard label="UY (EQY)" value={sd.uy_eqy} unit="m" />
            </>
          )}
          {activeModule === '3.2.8' && (
            <DataCard label="Mass" value={c.module_3_2_8_mass} unit="×10³ kg" />
          )}
        </div>
      </div>

      {/* Status */}
      <div className="detail-section">
        <div className="detail-section-title">Classification</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {activeModule === '3.2.4' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_4_eox_status} />
                <span>X-direction: {c.module_3_2_4_eox_status || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_4_eoy_status} />
                <span>Y-direction: {c.module_3_2_4_eoy_status || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.5' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_5_rx_status} />
                <span>X-direction: {c.module_3_2_5_rx_status || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_5_ry_status} />
                <span>Y-direction: {c.module_3_2_5_ry_status || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.6' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <StatusIcon status={c.module_3_2_6_status} />
              <span>Stiffness X: {c.module_3_2_6_status || '—'}</span>
            </div>
          )}
          {activeModule === '3.2.7' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <StatusIcon status={c.module_3_2_7_status} />
              <span>Stiffness Y: {c.module_3_2_7_status || '—'}</span>
            </div>
          )}
          {activeModule === '3.2.8' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_8_status_upper} />
                <span>Mi &lt; 2·Mi+1: {c.module_3_2_8_status_upper || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusIcon status={c.module_3_2_8_status_lower} />
                <span>Mi &lt; 2·Mi-1: {c.module_3_2_8_status_lower || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.1' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <StatusIcon status={c.module_3_2_1_status} />
              <span>Slenderness: {c.module_3_2_1_status || '—'} (λ = {c.module_3_2_1_lambda?.toFixed(3) || '—'})</span>
            </div>
          )}
        </div>
      </div>

      {/* Failure Reasons */}
      {storey.failure_reasons && storey.failure_reasons.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title" style={{ color: 'var(--fail)' }}>Failure Reasons</div>
          {storey.failure_reasons.map((reason, i) => (
            <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', padding: '4px 0' }}>
              • {reason}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
