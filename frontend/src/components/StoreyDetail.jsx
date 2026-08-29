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
  if (status === 'OK' || status === 'pass') return <CheckCircle2 size={14} style={{ color: 'var(--pass)' }} />
  if (status === 'NOT OK' || status === 'fail') return <XCircle size={14} style={{ color: 'var(--fail)' }} />
  return <Minus size={14} style={{ color: 'var(--text-tertiary)' }} />
}

function DataRow({ label, value, unit = 'm', accent = false }) {
  const displayValue = value !== null && value !== undefined
    ? (typeof value === 'number' ? value.toFixed(3) : value)
    : '—'

  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '5px 0', borderBottom: '1px solid var(--border-subtle)',
    }}>
      <span style={{ fontSize: 11, color: 'var(--text-tertiary)', fontWeight: 500 }}>{label}</span>
      <span style={{
        fontSize: 12, fontFamily: "'JetBrains Mono', monospace",
        fontWeight: accent ? 600 : 500,
        color: accent ? 'var(--accent)' : 'var(--text-primary)',
      }}>
        {displayValue}
        {value !== null && value !== undefined && (
          <span style={{ fontSize: 10, color: 'var(--text-tertiary)', marginLeft: 2 }}>{unit}</span>
        )}
      </span>
    </div>
  )
}

export default function StoreyDetail({ storey, module: activeModule }) {
  const config = moduleConfig[activeModule]
  const sd = {
    xcm: storey.xcm, ycm: storey.ycm, xcr: storey.xcr, ycr: storey.ycr,
    mass: storey.mass, elevation: storey.elevation,
    ux_ul1: storey.ux_ul1, uy_ul2: storey.uy_ul2, rz_ul3: storey.rz_ul3,
    vx_eqx: storey.vx_eqx, vy_eqy: storey.vy_eqy,
    ux_eqx: storey.ux_eqx, uy_eqy: storey.uy_eqy,
  }
  const c = {
    eox: storey.eox, eoy: storey.eoy, rx: storey.rx, ry: storey.ry,
    kfx: storey.kfx, kfy: storey.kfy, kmt: storey.kmt,
    kx: storey.kx, ky: storey.ky, ls: storey.ls,
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

  return (
    <motion.div key={`${storey.id}-${activeModule}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>
      {/* Header */}
      <div className="detail-header">
        <div>
          <h2>{storey.name}</h2>
          <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 1 }}>
            Module {activeModule}
          </div>
        </div>
        <span className={`status-badge ${storey.overall_classification === 'PASS' ? 'pass' : 'fail'}`}>
          {storey.overall_classification === 'PASS' ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
          {storey.overall_classification}
        </span>
      </div>

      {/* Source Data */}
      <div className="detail-section">
        <div className="detail-section-title">Source Data</div>
        <DataRow label="Xcm" value={sd.xcm} />
        <DataRow label="Ycm" value={sd.ycm} />
        <DataRow label="Xcr" value={sd.xcr} />
        <DataRow label="Ycr" value={sd.ycr} />
        <DataRow label="Mass" value={sd.mass} unit="×10³ kg" />
        <DataRow label="Elevation" value={sd.elevation} />
      </div>

      {/* Calculated Values */}
      <div className="detail-section">
        <div className="detail-section-title">Calculated Values</div>
        {activeModule === '3.2.2' && (
          <>
            <DataRow label="eox" value={c.eox} accent />
            <DataRow label="eoy" value={c.eoy} accent />
          </>
        )}
        {activeModule === '3.2.3' && (
          <>
            <DataRow label="KFX" value={c.kfx} unit="kN/m" />
            <DataRow label="KFY" value={c.kfy} unit="kN/m" />
            <DataRow label="KMT" value={c.kmt} unit="kN/m" />
            <DataRow label="rx" value={c.rx} accent />
            <DataRow label="ry" value={c.ry} accent />
          </>
        )}
        {activeModule === '3.2.4' && (
          <>
            <DataRow label="eox" value={c.eox} accent />
            <DataRow label="eoy" value={c.eoy} accent />
            <DataRow label="0.3·rx" value={c.module_3_2_4_limit_x} />
            <DataRow label="0.3·ry" value={c.module_3_2_4_limit_y} />
          </>
        )}
        {activeModule === '3.2.5' && (
          <>
            <DataRow label="rx" value={c.rx} accent />
            <DataRow label="ry" value={c.ry} accent />
            <DataRow label="ls" value={c.ls} />
          </>
        )}
        {activeModule === '3.2.6' && (
          <>
            <DataRow label="Kx" value={c.kx} unit="kN/m" accent />
            <DataRow label="VX (EQX)" value={sd.vx_eqx} unit="kN" />
            <DataRow label="UX (EQX)" value={sd.ux_eqx} unit="m" />
          </>
        )}
        {activeModule === '3.2.7' && (
          <>
            <DataRow label="Ky" value={c.ky} unit="kN/m" accent />
            <DataRow label="VY (EQY)" value={sd.vy_eqy} unit="kN" />
            <DataRow label="UY (EQY)" value={sd.uy_eqy} unit="m" />
          </>
        )}
        {activeModule === '3.2.8' && (
          <DataRow label="Mass" value={c.module_3_2_8_mass} unit="×10³ kg" accent />
        )}
      </div>

      {/* Classification Status */}
      <div className="detail-section">
        <div className="detail-section-title">Classification</div>
        <div style={{
          background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)', padding: 10,
        }}>
          {activeModule === '3.2.4' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_4_eox_status} />
                <span style={{ fontSize: 12 }}>X: {c.module_3_2_4_eox_status || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_4_eoy_status} />
                <span style={{ fontSize: 12 }}>Y: {c.module_3_2_4_eoy_status || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.5' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_5_rx_status} />
                <span style={{ fontSize: 12 }}>X: {c.module_3_2_5_rx_status || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_5_ry_status} />
                <span style={{ fontSize: 12 }}>Y: {c.module_3_2_5_ry_status || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.6' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
              <StatusIcon status={c.module_3_2_6_status} />
              <span style={{ fontSize: 12 }}>Stiffness X: {c.module_3_2_6_status || '—'}</span>
            </div>
          )}
          {activeModule === '3.2.7' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
              <StatusIcon status={c.module_3_2_7_status} />
              <span style={{ fontSize: 12 }}>Stiffness Y: {c.module_3_2_7_status || '—'}</span>
            </div>
          )}
          {activeModule === '3.2.8' && (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_8_status_upper} />
                <span style={{ fontSize: 12 }}>&lt; 2·Mi+1: {c.module_3_2_8_status_upper || '—'}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <StatusIcon status={c.module_3_2_8_status_lower} />
                <span style={{ fontSize: 12 }}>&lt; 2·Mi-1: {c.module_3_2_8_status_lower || '—'}</span>
              </div>
            </>
          )}
          {activeModule === '3.2.1' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
              <StatusIcon status={c.module_3_2_1_status} />
              <span style={{ fontSize: 12 }}>λ = {c.module_3_2_1_lambda?.toFixed(3) || '—'}</span>
            </div>
          )}
        </div>
      </div>

      {/* Formula */}
      <div className="detail-section">
        <div className="detail-section-title">Formula</div>
        <div style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
          color: 'var(--accent)', background: 'var(--accent-subtle)',
          padding: '8px 10px', borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--accent-muted)',
        }}>
          {config.formula}
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4 }}>
          Criterion: {config.criterion}
        </div>
      </div>

      {/* Failure Reasons */}
      {storey.failure_reasons && storey.failure_reasons.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title" style={{ color: 'var(--fail)' }}>Failures</div>
          <div style={{
            background: 'var(--fail-bg)', border: '1px solid var(--fail-border)',
            borderRadius: 'var(--radius-sm)', padding: 10,
          }}>
            {storey.failure_reasons.map((reason, i) => (
              <div key={i} style={{ fontSize: 11, color: 'var(--fail)', padding: '2px 0' }}>
                • {reason}
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
