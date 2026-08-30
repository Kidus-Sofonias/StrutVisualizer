import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Settings, Sun, Moon, FileText, Table, BarChart3, Download, RotateCcw, Weight } from 'lucide-react'

const DEFAULT_SETTINGS = {
  theme: 'light',
  fontSize: 'medium',
  showFormulas: true,
  showEngineeringText: true,
  defaultExportFormat: 'excel',
  exportIncludeCharts: true,
  exportIncludeFormulas: true,
  exportIncludeBackground: true,
  exportGroupBySection: true,
  chartAnimations: true,
  chartTooltips: true,
  storeySortOrder: 'top-down',
  autoRecalculate: false,
}

function WeightOverrideSection() {
  const [override, setOverride] = useState('')
  const [activeWeight, setActiveWeight] = useState(null)
  const [calculatedWeight, setCalculatedWeight] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // Load current project info
  useEffect(() => {
    fetch(`${API}/api/projects`)
      .then(r => r.json())
      .then(data => {
        if (data.projects && data.projects.length > 0) {
          const pid = data.projects[0].id
          return fetch(`${API}/api/projects/${pid}`)
        }
      })
      .then(r => r ? r.json() : null)
      .then(proj => {
        if (proj) {
          if (proj.total_weight_override) {
            setOverride(String(proj.total_weight_override))
          }
          // Get calculated weight from section 4.1
          const w41 = proj.sections?.['4.1']?.total_weight_kN
          if (w41) setCalculatedWeight(w41)
        }
      })
      .catch(() => {})
  }, [])

  const handleSave = async () => {
    setLoading(true)
    setMessage('')
    try {
      const pid_res = await fetch(`${API}/api/projects`)
      const pid_data = await pid_res.json()
      if (!pid_data.projects || pid_data.projects.length === 0) {
        setMessage('No project loaded')
        setLoading(false)
        return
      }
      const pid = pid_data.projects[0].id
      const body = override && parseFloat(override) > 0
        ? { total_weight: parseFloat(override) }
        : { total_weight: null }
      const res = await fetch(`${API}/api/projects/${pid}/weight-override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      setActiveWeight(data.active_weight)
      setCalculatedWeight(data.calculated_weight)
      setMessage(body.total_weight
        ? `Weight set to ${body.total_weight} kN (recalculated)`
        : `Using calculated weight: ${data.calculated_weight?.toFixed(0) || '?'} kN`)
    } catch (e) {
      setMessage('Error: ' + e.message)
    }
    setLoading(false)
  }

  return (
    <div className="settings-section">
      <h3><Weight size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Engineering Parameters</h3>
      <div className="settings-row">
        <div>
          <div className="label">Total Building Weight (W) for Section 4.1</div>
          <div className="hint">
            Override the total weight used in base shear calculation.<br />
            MDB-calculated: ~100,925 kN (Column + Pier Forces)<br />
            Excel reference: 103,268 kN (Base Reactions)<br />
            Leave empty to use MDB-calculated value.
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end' }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              type="number"
              value={override}
              onChange={(e) => setOverride(e.target.value)}
              placeholder={calculatedWeight ? String(Math.round(calculatedWeight)) : '103268'}
              style={{
                width: 140, padding: '7px 12px', fontSize: 13,
                border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-subtle)', color: 'var(--text-primary)',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            />
            <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>kN</span>
          </div>
          <button
            className="primary-btn"
            onClick={handleSave}
            disabled={loading}
            style={{ padding: '6px 16px', fontSize: 12 }}
          >
            {loading ? 'Saving...' : 'Apply & Recalculate'}
          </button>
          {activeWeight && (
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
              Active: {activeWeight.toFixed(0)} kN
            </div>
          )}
          {message && (
            <div style={{ fontSize: 11, color: message.startsWith('Error') ? 'var(--red)' : 'var(--green)' }}>
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function SettingsPage({ settings, onUpdate }) {
  const [local, setLocal] = useState({ ...DEFAULT_SETTINGS, ...settings })

  useEffect(() => {
    setLocal({ ...DEFAULT_SETTINGS, ...settings })
  }, [settings])

  const update = (key, value) => {
    const next = { ...local, [key]: value }
    setLocal(next)
    onUpdate(next)
  }

  const resetAll = () => {
    setLocal(DEFAULT_SETTINGS)
    onUpdate(DEFAULT_SETTINGS)
  }

  const Toggle = ({ value, onChange }) => (
    <div
      className={`toggle ${value ? 'active' : ''}`}
      onClick={() => onChange(!value)}
    />
  )

  return (
    <motion.div
      className="settings-page"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 28,
      }}>
        <div>
          <h2 style={{
            fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10,
            letterSpacing: '-0.02em',
          }}>
            <Settings size={22} style={{ color: 'var(--accent)' }} /> Settings
          </h2>
          <p style={{ color: 'var(--text-tertiary)', fontSize: 14, marginTop: 4 }}>
            Customize the application appearance and export behavior
          </p>
        </div>
        <button className="secondary-btn" onClick={resetAll}>
          <RotateCcw size={14} /> Reset Defaults
        </button>
      </div>

      {/* Appearance */}
      <div className="settings-section">
        <h3><Sun size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Appearance</h3>
        <div className="settings-row">
          <div>
            <div className="label">Theme</div>
            <div className="hint">Choose between light and dark mode</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={local.theme === 'light' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('theme', 'light')}
              style={{ padding: '7px 16px', fontSize: 12 }}
            >
              <Sun size={14} /> Light
            </button>
            <button
              className={local.theme === 'dark' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('theme', 'dark')}
              style={{ padding: '7px 16px', fontSize: 12 }}
            >
              <Moon size={14} /> Dark
            </button>
          </div>
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Font Size</div>
            <div className="hint">Adjust text size throughout the app</div>
          </div>
          <select
            value={local.fontSize}
            onChange={(e) => update('fontSize', e.target.value)}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>

      {/* Display */}
      <div className="settings-section">
        <h3><BarChart3 size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Display</h3>
        <div className="settings-row">
          <div>
            <div className="label">Show Engineering Background Text</div>
            <div className="hint">Display expandable engineering descriptions below tables</div>
          </div>
          <Toggle value={local.showEngineeringText} onChange={(v) => update('showEngineeringText', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Show Formulas in Tables</div>
            <div className="hint">Display formula references alongside calculated values</div>
          </div>
          <Toggle value={local.showFormulas} onChange={(v) => update('showFormulas', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Storey Sort Order</div>
            <div className="hint">Display storeys from top-to-bottom or bottom-to-top</div>
          </div>
          <select
            value={local.storeySortOrder}
            onChange={(e) => update('storeySortOrder', e.target.value)}
          >
            <option value="top-down">Top to Bottom</option>
            <option value="bottom-up">Bottom to Top</option>
          </select>
        </div>
      </div>

      {/* Charts */}
      <div className="settings-section">
        <h3><BarChart3 size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Charts</h3>
        <div className="settings-row">
          <div>
            <div className="label">Chart Animations</div>
            <div className="hint">Enable smooth transitions on chart data</div>
          </div>
          <Toggle value={local.chartAnimations} onChange={(v) => update('chartAnimations', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Chart Tooltips</div>
            <div className="hint">Show detailed values when hovering over chart points</div>
          </div>
          <Toggle value={local.chartTooltips} onChange={(v) => update('chartTooltips', v)} />
        </div>
      </div>

      {/* Export */}
      <div className="settings-section">
        <h3><Download size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Export</h3>
        <div className="settings-row">
          <div>
            <div className="label">Default Export Format</div>
            <div className="hint">Choose between Excel and PDF as the default</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={local.defaultExportFormat === 'excel' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('defaultExportFormat', 'excel')}
              style={{ padding: '7px 16px', fontSize: 12 }}
            >
              <Table size={14} /> Excel
            </button>
            <button
              className={local.defaultExportFormat === 'pdf' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('defaultExportFormat', 'pdf')}
              style={{ padding: '7px 16px', fontSize: 12 }}
            >
              <FileText size={14} /> PDF
            </button>
          </div>
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Include Charts in Export</div>
            <div className="hint">Embed stiffness and displacement charts in the report</div>
          </div>
          <Toggle value={local.exportIncludeCharts} onChange={(v) => update('exportIncludeCharts', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Include Formulas in Export</div>
            <div className="hint">Show calculation formulas and engineering criteria</div>
          </div>
          <Toggle value={local.exportIncludeFormulas} onChange={(v) => update('exportIncludeFormulas', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Include Engineering Background</div>
            <div className="hint">Include explanatory text from Eurocode references</div>
          </div>
          <Toggle value={local.exportIncludeBackground} onChange={(v) => update('exportIncludeBackground', v)} />
        </div>
        <div className="settings-row">
          <div>
            <div className="label">Group by Section in Export</div>
            <div className="hint">Organize Excel sheets by section (3.2, 3.3, etc.)</div>
          </div>
          <Toggle value={local.exportGroupBySection} onChange={(v) => update('exportGroupBySection', v)} />
        </div>
      </div>

      {/* Data */}
      <div className="settings-section">
        <h3><Settings size={16} style={{ verticalAlign: -2, color: 'var(--accent)' }} /> Data</h3>
        <div className="settings-row">
          <div>
            <div className="label">Auto-Recalculate on Import</div>
            <div className="hint">Automatically run all calculations after data import</div>
          </div>
          <Toggle value={local.autoRecalculate} onChange={(v) => update('autoRecalculate', v)} />
        </div>
      </div>

      {/* Engineering Parameters */}
      <WeightOverrideSection />
    </motion.div>
  )
}
