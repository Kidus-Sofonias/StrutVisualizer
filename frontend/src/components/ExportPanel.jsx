import { motion } from 'framer-motion'
import { FileSpreadsheet, FileText, Download } from 'lucide-react'

export default function ExportPanel({ project, onExport }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: 600 }}
    >
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, marginBottom: 8 }}>Export Report</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          Generate a report for <strong>{project.project_name}</strong>
        </p>
      </div>

      <div className="export-options">
        <motion.div
          className="export-card"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onExport('excel')}
        >
          <FileSpreadsheet size={48} style={{ color: 'var(--pass)' }} />
          <h3>Excel Report</h3>
          <p>Full workbook with all calculation tables, formulas, and formatting</p>
          <div style={{ marginTop: 16 }}>
            <button className="primary-btn" style={{ width: '100%' }}>
              <Download size={16} />
              Export .xlsx
            </button>
          </div>
        </motion.div>

        <motion.div
          className="export-card"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onExport('pdf')}
        >
          <FileText size={48} style={{ color: 'var(--accent)' }} />
          <h3>PDF Report</h3>
          <p>Professional engineering report with tables and building summary</p>
          <div style={{ marginTop: 16 }}>
            <button className="primary-btn" style={{ width: '100%' }}>
              <Download size={16} />
              Export .pdf
            </button>
          </div>
        </motion.div>
      </div>

      <div style={{
        marginTop: 32,
        padding: 20,
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
      }}>
        <h4 style={{ fontSize: 14, marginBottom: 12 }}>Report Contents</h4>
        <ul style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 2, paddingLeft: 16 }}>
          <li>Project information and building summary</li>
          <li>Table 3.2.1 — Plan Regularity (Slenderness)</li>
          <li>Table 3.2.2 — Structural Eccentricity</li>
          <li>Table 3.2.3 — Torsional Radius</li>
          <li>Table 3.2.4 — Eccentricity vs Gyration Comparison</li>
          <li>Table 3.2.5 — Torsional vs Gyration Comparison</li>
          <li>Table 3.2.6 — Storey Stiffness X Direction</li>
          <li>Table 3.2.7 — Storey Stiffness Y Direction</li>
          <li>Table 3.2.8 — Mass Distribution</li>
          <li>Building-level classification and critical storeys</li>
        </ul>
      </div>
    </motion.div>
  )
}
