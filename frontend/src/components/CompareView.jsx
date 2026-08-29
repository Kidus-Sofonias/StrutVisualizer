import { useState } from 'react'
import { motion } from 'framer-motion'
import { GitCompare, Plus } from 'lucide-react'

export default function CompareView({ projects, api }) {
  const [selectedIds, setSelectedIds] = useState([])
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(false)

  const toggleProject = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const runComparison = async () => {
    if (selectedIds.length < 2) return
    setLoading(true)
    try {
      const res = await fetch(`${api}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_ids: selectedIds }),
      })
      const data = await res.json()
      setComparison(data.comparison)
    } catch (e) {
      console.error('Comparison failed:', e)
    }
    setLoading(false)
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4, letterSpacing: '-0.01em' }}>
          Compare Projects
        </h2>
        <p style={{ color: 'var(--text-tertiary)', fontSize: 14, marginBottom: 20 }}>
          Select two or more projects to compare their structural analysis results side by side.
        </p>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {projects.map(p => (
            <button
              key={p.id}
              onClick={() => toggleProject(p.id)}
              style={{
                padding: '10px 18px',
                borderRadius: 'var(--radius-md)',
                border: `1.5px solid ${selectedIds.includes(p.id) ? 'var(--accent)' : 'var(--border-primary)'}`,
                background: selectedIds.includes(p.id) ? 'var(--accent-subtle)' : 'var(--bg-surface)',
                color: selectedIds.includes(p.id) ? 'var(--accent)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontFamily: 'inherit', fontSize: 13, fontWeight: 500,
                transition: 'all 0.15s ease',
                display: 'flex', alignItems: 'center', gap: 6,
              }}
            >
              {selectedIds.includes(p.id) && <Plus size={14} />}
              {p.name}
              <span style={{
                fontSize: 11, color: 'var(--text-tertiary)',
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                ({p.storeys}S)
              </span>
            </button>
          ))}
        </div>

        {selectedIds.length >= 2 && (
          <button
            className="primary-btn"
            onClick={runComparison}
            disabled={loading}
            style={{ marginTop: 16 }}
          >
            {loading ? <div className="spinner" style={{ width: 16, height: 16 }} /> : <GitCompare size={16} />}
            Compare {selectedIds.length} Projects
          </button>
        )}
      </div>

      {comparison && (
        <div className="compare-grid">
          {comparison.map((proj, idx) => (
            <motion.div
              key={proj.project_id}
              className="compare-card"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <h3>{proj.project_name}</h3>
              <div style={{ overflowX: 'auto' }}>
                <table className="calc-table">
                  <thead>
                    <tr>
                      <th>Story</th>
                      <th>eox</th>
                      <th>eoy</th>
                      <th>rx</th>
                      <th>ry</th>
                      <th>Kx</th>
                      <th>Ky</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {proj.storeys.map(s => (
                      <tr key={s.name}>
                        <td>{s.name}</td>
                        <td>{s.eox?.toFixed(3) ?? '—'}</td>
                        <td>{s.eoy?.toFixed(3) ?? '—'}</td>
                        <td>{s.rx?.toFixed(3) ?? '—'}</td>
                        <td>{s.ry?.toFixed(3) ?? '—'}</td>
                        <td>{s.kx?.toFixed(0) ?? '—'}</td>
                        <td>{s.ky?.toFixed(0) ?? '—'}</td>
                        <td className={`status-cell ${s.classification === 'PASS' ? 'pass' : 'fail'}`}>
                          {s.classification}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
