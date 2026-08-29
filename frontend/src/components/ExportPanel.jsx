import { motion } from 'framer-motion'
import { FileSpreadsheet, FileText, Download } from 'lucide-react'

export default function ExportPanel({ project, onExport }) {
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
          onClick={() => onExport('pdf')}
        >
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'var(--accent-subtle)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 4px',
          }}>
            <FileText size={28} style={{ color: 'var(--accent)' }} />
          </div>
          <h3>PDF Report</h3>
          <p>Professional engineering report with tables and building summary</p>
          <div style={{ marginTop: 18 }}>
            <button className="primary-btn" style={{ width: '100%' }}>
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
