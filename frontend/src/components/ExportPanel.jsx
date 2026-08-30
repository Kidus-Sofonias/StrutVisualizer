import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileSpreadsheet, FileText, Download, Loader2 } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ExportPanel({ project, onExport }) {
  const [docxLoading, setDocxLoading] = useState(false)

  const handleDocxExport = async () => {
    setDocxLoading(true)
    try {
      const res = await fetch(`${API}/api/export-docx`, { method: 'POST' })
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${project.project_name}_Structural_Design_Report.docx`
        a.click()
        window.URL.revokeObjectURL(url)
      } else {
        const err = await res.json()
        alert(err.detail || 'DOCX export failed')
      }
    } catch (e) {
      alert('DOCX export failed: ' + e.message)
    }
    setDocxLoading(false)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: 700 }}
    >
      <div style={{ marginBottom: 36 }}>
        <h2 style={{
          fontSize: 22, fontWeight: 700, marginBottom: 6,
          letterSpacing: '-0.02em',
        }}>
          Export Report
        </h2>
        <p style={{ color: 'var(--text-tertiary)', fontSize: 14, lineHeight: 1.6 }}>
          Generate a comprehensive analysis report for{' '}
          <strong style={{ color: 'var(--text-primary)' }}>{project.project_name}</strong>
        </p>
      </div>

      <div className="export-options" style={{ marginBottom: 32 }}>
        <motion.div
          className="export-card"
          whileHover={{ y: -3 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onExport('excel')}
        >
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'var(--pass-bg)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 4px',
          }}>
            <FileSpreadsheet size={28} style={{ color: 'var(--pass)' }} />
          </div>
          <h3>Excel Report</h3>
          <p>Full workbook with all calculation tables, formulas, and formatting</p>
          <div style={{ marginTop: 18 }}>
            <button className="primary-btn" style={{ width: '100%' }}>
              <Download size={16} />
              Export .xlsx
            </button>
          </div>
        </motion.div>

        <motion.div
          className="export-card"
          whileHover={{ y: -3 }}
          whileTap={{ scale: 0.98 }}
        >
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'var(--accent-subtle)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 4px',
          }}>
            <FileText size={28} style={{ color: 'var(--accent)' }} />
          </div>
          <h3>Word Report (DOCX)</h3>
          <p>Professional engineering report with sections 2.4–4.6, tables, and conclusions</p>
          <div style={{ marginTop: 18 }}>
            <button
              className="primary-btn"
              style={{ width: '100%' }}
              onClick={handleDocxExport}
              disabled={docxLoading}
            >
              {docxLoading ? <><Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> Generating...</> : <><Download size={16} /> Export .docx</>}
            </button>
          </div>
        </motion.div>

        <motion.div
          className="export-card"
          whileHover={{ y: -3 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onExport('pdf')}
        >
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'var(--bg-subtle)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 4px',
          }}>
            <FileText size={28} style={{ color: 'var(--text-tertiary)' }} />
          </div>
          <h3>PDF Report</h3>
          <p>Professional engineering report with tables and building summary</p>
          <div style={{ marginTop: 18 }}>
            <button className="secondary-btn" style={{ width: '100%' }}>
              <Download size={16} />
              Export .pdf
            </button>
          </div>
        </motion.div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Report Contents</h3>
        </div>
        <div className="card-body">
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)',
            gap: 8, fontSize: 13, color: 'var(--text-secondary)',
          }}>
            {[
              'Project information & building summary',
              'Table 3.2.1 — Plan Regularity (Slenderness)',
              'Table 3.2.2 — Structural Eccentricity',
              'Table 3.2.3 — Torsional Radius',
              'Table 3.2.4 — Eccentricity vs Gyration',
              'Table 3.2.5 — Torsional vs Gyration',
              'Table 3.2.6 — Storey Stiffness X',
              'Table 3.2.7 — Storey Stiffness Y',
              'Table 3.2.8 — Mass Distribution',
              'Building-level classification',
              'Section 2.4 — Loading Schedule',
              'Section 2.5 — Concrete Cover Check',
              'Section 3.3 — Lateral Force Classification',
              'Section 3.4 — Behavioral Factor (q)',
              'Section 4.1 — Base Shear',
              'Section 4.2 — Modal Participation (50 modes)',
              'Section 4.3 — Geometric Imperfection',
              'Section 4.4 — Stability Analysis',
              'Section 4.5 — Storey Drift Control',
              'Section 4.6 — Overturning Check',
              'Engineering Conclusion',
            ].map((item, i) => (
              <div key={i} style={{
                padding: '8px 12px', background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)', fontSize: 12,
              }}>
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
