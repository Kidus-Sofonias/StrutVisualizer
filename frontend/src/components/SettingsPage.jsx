import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings, Sun, Moon, FileText, Table, BarChart3, Download, RotateCcw } from 'lucide-react'

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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Settings size={20} /> Settings
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
            Customize the application appearance and export behavior
          </p>
        </div>
        <button className="secondary-btn" onClick={resetAll}>
          <RotateCcw size={14} /> Reset Defaults
        </button>
      </div>

      {/* Appearance */}
      <div className="settings-section">
        <h3><Sun size={16} style={{ verticalAlign: -2, marginRight: 6 }} /> Appearance</h3>
        <div className="settings-row">
          <div>
            <div className="label">Theme</div>
            <div className="hint">Choose between light and dark mode</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={local.theme === 'light' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('theme', 'light')}
              style={{ padding: '6px 14px', fontSize: 12 }}
            >
              <Sun size={14} /> Light
            </button>
            <button
              className={local.theme === 'dark' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('theme', 'dark')}
              style={{ padding: '6px 14px', fontSize: 12 }}
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
            style={{
              padding: '6px 12px', borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)', background: 'var(--bg-tertiary)',
              color: 'var(--text)', fontSize: 12,
            }}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>

      {/* Display */}
      <div className="settings-section">
        <h3><BarChart3 size={16} style={{ verticalAlign: -2, marginRight: 6 }} /> Display</h3>
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
            style={{
              padding: '6px 12px', borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)', background: 'var(--bg-tertiary)',
              color: 'var(--text)', fontSize: 12,
            }}
          >
            <option value="top-down">Top to Bottom</option>
            <option value="bottom-up">Bottom to Top</option>
          </select>
        </div>
      </div>

      {/* Charts */}
      <div className="settings-section">
        <h3><BarChart3 size={16} style={{ verticalAlign: -2, marginRight: 6 }} /> Charts</h3>
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
        <h3><Download size={16} style={{ verticalAlign: -2, marginRight: 6 }} /> Export</h3>
        <div className="settings-row">
          <div>
            <div className="label">Default Export Format</div>
            <div className="hint">Choose between Excel and PDF as the default</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              className={local.defaultExportFormat === 'excel' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('defaultExportFormat', 'excel')}
              style={{ padding: '6px 14px', fontSize: 12 }}
            >
              <Table size={14} /> Excel
            </button>
            <button
              className={local.defaultExportFormat === 'pdf' ? 'primary-btn' : 'secondary-btn'}
              onClick={() => update('defaultExportFormat', 'pdf')}
              style={{ padding: '6px 14px', fontSize: 12 }}
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
        <h3><Settings size={16} style={{ verticalAlign: -2, marginRight: 6 }} /> Data</h3>
        <div className="settings-row">
          <div>
            <div className="label">Auto-Recalculate on Import</div>
            <div className="hint">Automatically run all calculations after data import</div>
          </div>
          <Toggle value={local.autoRecalculate} onChange={(v) => update('autoRecalculate', v)} />
        </div>
      </div>
    </motion.div>
  )
}
