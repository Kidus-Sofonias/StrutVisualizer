import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, Database, FileCheck, AlertTriangle, HardDrive } from 'lucide-react'

const API = 'http://localhost:8000'

export default function ProjectUpload({ onUpload, onLoadLocal, loading }) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [localFiles, setLocalFiles] = useState([])
  const fileRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/api/status`)
      .then(r => r.json())
      .then(data => setLocalFiles(data.local_files || []))
      .catch(() => {})
  }, [])

  const handleFile = (file) => {
    if (file && (file.name.endsWith('.mdb') || file.name.endsWith('.accdb'))) {
      setSelectedFile(file)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }



  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: 600, margin: '0 auto' }}
    >
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Database size={48} style={{ color: 'var(--accent)', marginBottom: 16 }} />
        <h2 style={{ fontSize: 24, marginBottom: 8 }}>Import Access Database</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          Upload your ETABS-exported .mdb file to begin structural analysis
        </p>
      </div>

      {/* Local files */}
      {localFiles.length > 0 && (
        <div style={{
          marginBottom: 24,
          padding: 20,
          background: 'var(--bg-card)',
          borderRadius: 'var(--radius)',
          border: '1px solid var(--border)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <HardDrive size={16} style={{ color: 'var(--pass)' }} />
            <span style={{ fontSize: 13, fontWeight: 600 }}>Files on Server</span>
          </div>
          {localFiles.map(f => (
            <div key={f} style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 14px',
              background: 'var(--bg-tertiary)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: 8,
            }}>
              <span style={{ fontSize: 13, fontFamily: "'JetBrains Mono', monospace" }}>{f}</span>
              <button
                className="primary-btn"
                onClick={() => onLoadLocal && onLoadLocal(f)}
                disabled={loading}
                style={{ padding: '6px 16px', fontSize: 12 }}
              >
                {loading ? 'Loading...' : 'Load'}
              </button>
            </div>
          ))}
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
            Loading from server uses cache — takes under 1 second
          </p>
        </div>
      )}

      <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 12, margin: '16px 0' }}>
        — or upload a new file —
      </div>

      <div
        className={`upload-zone ${dragOver ? 'dragover' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".mdb,.accdb"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {selectedFile ? (
          <>
            <FileCheck size={48} style={{ color: 'var(--pass)' }} />
            <h3>{selectedFile.name}</h3>
            <p>{(selectedFile.size / 1024 / 1024).toFixed(1)} MB — Ready to import</p>
          </>
        ) : (
          <>
            <Upload size={48} style={{ color: 'var(--text-muted)' }} />
            <h3>Drop .mdb file here</h3>
            <p>or click to browse • Supports .mdb and .accdb files</p>
          </>
        )}
      </div>

      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ marginTop: 20, textAlign: 'center' }}
        >
          <button
            className="primary-btn"
            onClick={handleUpload}
            disabled={loading}
            style={{ padding: '12px 32px', fontSize: 15 }}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                Importing...
              </>
            ) : (
              <>
                <Upload size={18} />
                Import & Calculate
              </>
            )}
          </button>
        </motion.div>
      )}

      <div style={{
        marginTop: 32,
        padding: 20,
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <AlertTriangle size={18} style={{ color: 'var(--warn)', marginTop: 2, flexShrink: 0 }} />
          <div>
            <h4 style={{ fontSize: 13, marginBottom: 6 }}>Expected Database Contents</h4>
            <ul style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.8, paddingLeft: 16 }}>
              <li><strong>Center Mass Rigidity</strong> — XCM, YCM, XCR, YCR, Mass per storey</li>
              <li><strong>Story Data</strong> — Storey heights and elevations</li>
              <li><strong>Story Shears</strong> — VX, VY for unit load cases (UL1, UL2, UL3)</li>
              <li><strong>Displacement data</strong> — UX, UY, RZ for unit load cases</li>
              <li><strong>Diaphragm Mass Data</strong> — Mass distribution per storey</li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
