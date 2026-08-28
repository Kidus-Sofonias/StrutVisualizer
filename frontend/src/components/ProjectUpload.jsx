import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Database, FileCheck, AlertTriangle, HardDrive, Link2, Loader2, CheckCircle2, XCircle } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export default function ProjectUpload({ onUpload, onLoadLocal, loading }) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [localFiles, setLocalFiles] = useState([])
  const [etabsStatus, setEtabsStatus] = useState(null)
  const [etabsConnecting, setEtabsConnecting] = useState(false)
  const [etabsModelPath, setEtabsModelPath] = useState('')
  const [importMode, setImportMode] = useState('database') // 'database' or 'etabs'
  const fileRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/api/status`)
      .then(r => r.json())
      .then(data => setLocalFiles(data.local_files || []))
      .catch(() => {})

    // Check ETABS availability
    fetch(`${API}/api/etabs/status`)
      .then(r => r.json())
      .then(data => setEtabsStatus(data))
      .catch(() => setEtabsStatus({ available: false, message: 'Could not check ETABS status' }))
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

  const handleEtabsConnect = async () => {
    setEtabsConnecting(true)
    try {
      const res = await fetch(`${API}/api/etabs/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_path: etabsModelPath,
          launch_etabs: false,
        }),
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
        // Reload projects list
        window.location.reload()
      } else {
        alert(data.detail || data.message || 'ETABS connection failed')
      }
    } catch (err) {
      alert('Failed to connect to ETABS: ' + err.message)
    } finally {
      setEtabsConnecting(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: 650, margin: '0 auto' }}
    >
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Database size={48} style={{ color: 'var(--accent)', marginBottom: 16 }} />
        <h2 style={{ fontSize: 24, marginBottom: 8 }}>Import Structural Data</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          Import your ETABS model data to begin structural analysis
        </p>
      </div>

      {/* Import Mode Toggle */}
      <div style={{
        display: 'flex', gap: 8, marginBottom: 24,
        background: 'var(--bg-tertiary)', borderRadius: 'var(--radius)',
        padding: 4, border: '1px solid var(--border)',
      }}>
        <button
          onClick={() => setImportMode('database')}
          style={{
            flex: 1, padding: '10px 16px', borderRadius: 'var(--radius-sm)',
            border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
            background: importMode === 'database' ? 'var(--accent)' : 'transparent',
            color: importMode === 'database' ? 'white' : 'var(--text-muted)',
            transition: 'all 0.2s',
          }}
        >
          <Database size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
          Access Database (.mdb)
        </button>
        <button
          onClick={() => setImportMode('etabs')}
          style={{
            flex: 1, padding: '10px 16px', borderRadius: 'var(--radius-sm)',
            border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
            background: importMode === 'etabs' ? 'var(--accent)' : 'transparent',
            color: importMode === 'etabs' ? 'white' : 'var(--text-muted)',
            transition: 'all 0.2s',
          }}
        >
          <Link2 size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
          ETABS Direct API
        </button>
      </div>

      <AnimatePresence mode="wait">
        {importMode === 'database' ? (
          <motion.div key="database" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
            {/* Local files */}
            {localFiles.length > 0 && (
              <div style={{
                marginBottom: 24, padding: 20,
                background: 'var(--bg-card)', borderRadius: 'var(--radius)',
                border: '1px solid var(--border)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <HardDrive size={16} style={{ color: 'var(--pass)' }} />
                  <span style={{ fontSize: 13, fontWeight: 600 }}>Files on Server</span>
                </div>
                {localFiles.map(f => (
                  <div key={f} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '10px 14px', background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-sm)', marginBottom: 8,
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
          </motion.div>
        ) : (
          <motion.div key="etabs" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            {/* ETABS Direct API Connection */}
            <div style={{
              padding: 24, background: 'var(--bg-card)', borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}>
              {/* Status */}
              <div style={{
                display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20,
                padding: '12px 16px', borderRadius: 'var(--radius-sm)',
                background: etabsStatus?.available ? 'rgba(21, 128, 61, 0.1)' : 'rgba(185, 28, 28, 0.1)',
                border: `1px solid ${etabsStatus?.available ? 'rgba(21, 128, 61, 0.3)' : 'rgba(185, 28, 28, 0.3)'}`,
              }}>
                {etabsStatus?.available ? (
                  <CheckCircle2 size={18} style={{ color: 'var(--pass)' }} />
                ) : (
                  <XCircle size={18} style={{ color: 'var(--fail)' }} />
                )}
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>
                    {etabsStatus?.available ? 'ETABS API Available' : 'ETABS API Not Available'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {etabsStatus?.message || 'Checking...'}
                  </div>
                </div>
              </div>

              {/* Requirements */}
              <div style={{ marginBottom: 20, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.8 }}>
                <strong style={{ color: 'var(--text)' }}>Requirements:</strong>
                <ul style={{ paddingLeft: 16, marginTop: 4 }}>
                  <li>Windows OS (COM is Windows-native)</li>
                  <li>ETABS installed and licensed on this machine</li>
                  <li>Python comtypes package ({etabsStatus?.comtypes_installed ? '✓ installed' : '✗ not installed'})</li>
                </ul>
              </div>

              {/* Model Path Input */}
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>
                  ETABS Model Path (.edb) — optional, leave empty to use current model
                </label>
                <input
                  type="text"
                  value={etabsModelPath}
                  onChange={(e) => setEtabsModelPath(e.target.value)}
                  placeholder="C:\Projects\Building Model.edb"
                  style={{
                    width: '100%', padding: '10px 14px', fontSize: 13,
                    background: 'var(--bg-tertiary)', border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)', color: 'var(--text)',
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                />
              </div>

              {/* Connect Button */}
              <button
                className="primary-btn"
                onClick={handleEtabsConnect}
                disabled={etabsConnecting || !etabsStatus?.available}
                style={{
                  width: '100%', padding: '12px 24px', fontSize: 14,
                  opacity: etabsStatus?.available ? 1 : 0.5,
                }}
              >
                {etabsConnecting ? (
                  <>
                    <Loader2 size={16} style={{ animation: 'spin 1s linear infinite', marginRight: 8 }} />
                    Connecting to ETABS...
                  </>
                ) : (
                  <>
                    <Link2 size={16} style={{ marginRight: 8 }} />
                    Connect to ETABS & Extract Data
                  </>
                )}
              </button>

              <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 12, textAlign: 'center' }}>
                This connects directly to a running ETABS instance via COM API.
                Make sure ETABS is open with your model loaded.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Database contents info */}
      {importMode === 'database' && (
        <div style={{
          marginTop: 32, padding: 20,
          background: 'var(--bg-card)', borderRadius: 'var(--radius)',
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
      )}
    </motion.div>
  )
}
