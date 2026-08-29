import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload, Database, FileCheck, AlertTriangle, HardDrive, Link2,
  Loader2, CheckCircle2, XCircle, Cpu, HardDriveIcon, Activity,
  FileSearch, Calculator, DatabaseIcon, Save, Zap, Clock,
} from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8005'

// Import processing stages — shown during the upload progress
const IMPORT_STAGES = [
  { id: 'uploading',    icon: Upload,           label: 'Uploading file',            desc: 'Sending database to server...',         duration: 3 },
  { id: 'reading',      icon: FileSearch,       label: 'Reading database',          desc: 'Connecting to Access parser...',         duration: 5 },
  { id: 'tables',       icon: DatabaseIcon,      label: 'Parsing tables',            desc: 'Extracting Story Data, Mass, Shears...', duration: 8 },
  { id: 'calculating',  icon: Calculator,        label: 'Running calculations',      desc: 'Computing stiffness, regularity...',     duration: 10 },
  { id: 'extended',     icon: Database,          label: 'Importing extended data',   desc: 'Loading Column Forces, Displacements...',duration: 6 },
  { id: 'wrapping',     icon: Save,              label: 'Wrapping up',              desc: 'Finalizing project data...',             duration: 3 },
]

// Animated system resource monitor
function SystemStats({ visible }) {
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    if (!visible) return
    const poll = async () => {
      try {
        const res = await fetch(`${API}/api/system-stats`)
        const data = await res.json()
        if (!data.error) {
          setStats(data)
          setHistory(prev => [...prev.slice(-29), data.cpu_percent])
        }
      } catch {}
    }
    poll()
    const interval = setInterval(poll, 1200)
    return () => clearInterval(interval)
  }, [visible])

  if (!visible || !stats) return null

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      style={styles.statsContainer}
    >
      <div style={styles.statsLabel}>
        <Activity size={12} />
        <span>System Resources</span>
      </div>

      <div style={styles.statsGrid}>
        {/* CPU */}
        <div style={styles.statItem}>
          <div style={styles.statHeader}>
            <Cpu size={11} />
            <span>CPU</span>
            <span style={styles.statValue}>{stats.cpu_percent}%</span>
          </div>
          <div style={styles.progressTrack}>
            <motion.div
              style={{
                ...styles.progressBar,
                background: stats.cpu_percent > 80 ? 'var(--fail)' :
                            stats.cpu_percent > 50 ? 'var(--warn)' : 'var(--accent)',
              }}
              animate={{ width: `${Math.min(stats.cpu_percent, 100)}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>

        {/* RAM */}
        <div style={styles.statItem}>
          <div style={styles.statHeader}>
            <HardDriveIcon size={11} />
            <span>RAM</span>
            <span style={styles.statValue}>
              {stats.ram_percent}% <span style={styles.statSub}>({stats.ram_used_mb} MB)</span>
            </span>
          </div>
          <div style={styles.progressTrack}>
            <motion.div
              style={{
                ...styles.progressBar,
                background: stats.ram_percent > 80 ? 'var(--fail)' :
                            stats.ram_percent > 60 ? 'var(--warn)' : 'var(--pass)',
              }}
              animate={{ width: `${Math.min(stats.ram_percent, 100)}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>

        {/* Mini sparkline for CPU */}
        {history.length > 3 && (
          <div style={styles.sparkline}>
            <svg width="100%" height="28" viewBox={`0 0 ${history.length * 6} 28`} preserveAspectRatio="none">
              <polyline
                fill="none"
                stroke="var(--accent)"
                strokeWidth="1.5"
                strokeLinecap="round"
                points={history.map((v, i) => `${i * 6},${28 - (v / 100) * 28}`).join(' ')}
              />
            </svg>
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Animated stage progress indicator
function ImportProgress({ currentStage, stages, elapsed, isComplete }) {
  const currentIdx = stages.findIndex(s => s.id === currentStage)
  const overallProgress = isComplete
    ? 100
    : Math.min(((currentIdx + 0.5) / stages.length) * 100, 95)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={styles.progressContainer}
    >
      {/* Overall progress bar */}
      <div style={styles.overallBar}>
        <div style={styles.overallBarTrack}>
          <motion.div
            style={styles.overallBarFill}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
          {isComplete && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 500, damping: 25, delay: 0.2 }}
              style={styles.completeCheckmark}
            >
              <CheckCircle2 size={14} />
            </motion.div>
          )}
        </div>
        <div style={styles.overallLabel}>
          <span style={styles.overallPercent}>{Math.round(overallProgress)}%</span>
          <span style={styles.overallTime}>
            <Clock size={10} style={{ marginRight: 3 }} />
            {formatTime(elapsed)}
          </span>
        </div>
      </div>

      {/* Stage list */}
      <div style={styles.stagesList}>
        {stages.map((stage, idx) => {
          const isDone = isComplete || idx < currentIdx
          const isActive = idx === currentIdx && !isComplete
          const StageIcon = stage.icon

          return (
            <motion.div
              key={stage.id}
              style={{
                ...styles.stageItem,
                opacity: idx <= currentIdx || isComplete ? 1 : 0.3,
              }}
              initial={false}
              animate={{
                x: isActive ? 0 : 0,
                scale: isActive ? 1 : 0.98,
              }}
              transition={{ duration: 0.2 }}
            >
              {/* Icon */}
              <div style={{
                ...styles.stageIcon,
                background: isDone ? 'var(--pass)' : isActive ? 'var(--accent)' : 'var(--bg-muted)',
                color: isDone || isActive ? 'white' : 'var(--text-tertiary)',
              }}>
                {isDone ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 25 }}
                  >
                    <CheckCircle2 size={14} />
                  </motion.div>
                ) : isActive ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                  >
                    <Loader2 size={14} />
                  </motion.div>
                ) : (
                  <StageIcon size={14} />
                )}
              </div>

              {/* Text */}
              <div style={styles.stageText}>
                <div style={{
                  ...styles.stageLabel,
                  color: isDone ? 'var(--pass)' : isActive ? 'var(--text-primary)' : 'var(--text-tertiary)',
                  fontWeight: isActive ? 600 : 500,
                }}>
                  {stage.label}
                </div>
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={styles.stageDesc}
                  >
                    {stage.desc}
                  </motion.div>
                )}
                {isDone && (
                  <div style={{ ...styles.stageDesc, color: 'var(--pass)' }}>Done</div>
                )}
              </div>

              {/* Pulse indicator for active stage */}
              {isActive && (
                <motion.div
                  style={styles.pulseIndicator}
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                />
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Elapsed time footer */}
      {!isComplete && (
        <motion.div
          style={styles.elapsedFooter}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Zap size={12} />
          <span>Processing in background — this may take a few minutes for large databases</span>
        </motion.div>
      )}
    </motion.div>
  )
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return m > 0 ? `${m}m ${s}s` : `${s}s`
}

export default function ProjectUpload({ onUpload, onLoadLocal, loading, uploadProgress, uploadStage, uploadElapsed }) {
  const [dragOver, setDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [localFiles, setLocalFiles] = useState([])
  const [etabsStatus, setEtabsStatus] = useState(null)
  const [etabsConnecting, setEtabsConnecting] = useState(false)
  const [etabsModelPath, setEtabsModelPath] = useState('')
  const [importMode, setImportMode] = useState('database')
  const [showStats, setShowStats] = useState(false)
  const fileRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/api/status`)
      .then(r => r.json())
      .then(data => setLocalFiles(data.local_files || []))
      .catch(() => {})

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
      setShowStats(true)
      onUpload(selectedFile)
    }
  }

  const handleEtabsConnect = async () => {
    setEtabsConnecting(true)
    try {
      const res = await fetch(`${API}/api/etabs/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_path: etabsModelPath, launch_etabs: false }),
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
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

  const isImporting = loading && uploadProgress

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: 720, margin: '0 auto' }}
    >
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 36 }}>
        <div style={{
          width: 64, height: 64, borderRadius: 'var(--radius-xl)',
          background: 'var(--accent-subtle)', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 20px', border: '1px solid var(--accent-muted)',
        }}>
          <Database size={28} style={{ color: 'var(--accent)' }} />
        </div>
        <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 6, letterSpacing: '-0.02em' }}>
          Import Structural Data
        </h2>
        <p style={{ color: 'var(--text-tertiary)', fontSize: 14 }}>
          Import your ETABS model data to begin structural analysis
        </p>
      </div>

      {/* Show progress when importing */}
      <AnimatePresence mode="wait">
        {isImporting ? (
          <motion.div key="progress" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }}>
            {/* File info */}
            <div style={styles.fileInfoBar}>
              <FileCheck size={16} style={{ color: 'var(--pass)' }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>{selectedFile?.name || 'Loading...'}</span>
              {selectedFile && (
                <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginLeft: 'auto' }}>
                  {(selectedFile.size / 1024 / 1024).toFixed(1)} MB
                </span>
              )}
            </div>

            {/* Import progress stages */}
            <ImportProgress
              currentStage={uploadStage}
              stages={IMPORT_STAGES}
              elapsed={uploadElapsed}
              isComplete={!loading}
            />

            {/* System stats */}
            <SystemStats visible={showStats} />
          </motion.div>
        ) : (
          <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {/* Import Mode Toggle */}
            <div style={{
              display: 'flex', gap: 4, marginBottom: 28,
              background: 'var(--bg-subtle)', borderRadius: 'var(--radius-lg)',
              padding: 4, border: '1px solid var(--border-primary)',
            }}>
              <button
                onClick={() => setImportMode('database')}
                style={{
                  flex: 1, padding: '10px 16px', borderRadius: 'var(--radius-md)',
                  border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
                  background: importMode === 'database' ? 'var(--bg-surface)' : 'transparent',
                  color: importMode === 'database' ? 'var(--text-primary)' : 'var(--text-tertiary)',
                  transition: 'all 0.15s ease',
                  boxShadow: importMode === 'database' ? 'var(--shadow-sm)' : 'none',
                }}
              >
                <Database size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
                Access Database (.mdb)
              </button>
              <button
                onClick={() => setImportMode('etabs')}
                style={{
                  flex: 1, padding: '10px 16px', borderRadius: 'var(--radius-md)',
                  border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
                  background: importMode === 'etabs' ? 'var(--bg-surface)' : 'transparent',
                  color: importMode === 'etabs' ? 'var(--text-primary)' : 'var(--text-tertiary)',
                  transition: 'all 0.15s ease',
                  boxShadow: importMode === 'etabs' ? 'var(--shadow-sm)' : 'none',
                }}
              >
                <Link2 size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
                ETABS Direct API
              </button>
            </div>

            <AnimatePresence mode="wait">
              {importMode === 'database' ? (
                <motion.div key="database" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 16 }}>
                  {/* Local files */}
                  {localFiles.length > 0 && (
                    <div className="card" style={{ marginBottom: 24 }}>
                      <div className="card-header">
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <HardDrive size={15} style={{ color: 'var(--pass)' }} />
                          <h3 style={{ fontSize: 13 }}>Files on Server</h3>
                        </div>
                      </div>
                      <div className="card-body">
                        {localFiles.map(f => (
                          <div key={f} style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                            padding: '10px 14px', background: 'var(--bg-subtle)',
                            borderRadius: 'var(--radius-sm)', marginBottom: 8,
                            border: '1px solid var(--border-subtle)',
                          }}>
                            <span style={{
                              fontSize: 13, fontFamily: "'JetBrains Mono', monospace",
                              color: 'var(--text-secondary)',
                            }}>
                              {f}
                            </span>
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
                        <p style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4 }}>
                          Loading from server uses cache — takes under 1 second
                        </p>
                      </div>
                    </div>
                  )}

                  <div style={{
                    textAlign: 'center', color: 'var(--text-tertiary)', fontSize: 12,
                    margin: '20px 0', display: 'flex', alignItems: 'center', gap: 12,
                  }}>
                    <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
                    <span style={{ fontWeight: 500 }}>or upload a new file</span>
                    <div style={{ flex: 1, height: 1, background: 'var(--border-subtle)' }} />
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
                        <Upload size={48} style={{ color: 'var(--text-tertiary)' }} />
                        <h3>Drop .mdb file here</h3>
                        <p>or click to browse • Supports .mdb and .accdb files</p>
                      </>
                    )}
                  </div>

                  {selectedFile && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      style={{ marginTop: 20, textAlign: 'center' }}
                    >
                      <button
                        className="primary-btn"
                        onClick={handleUpload}
                        disabled={loading}
                        style={{ padding: '12px 36px', fontSize: 14 }}
                      >
                        <Upload size={18} />
                        Import & Calculate
                      </button>
                    </motion.div>
                  )}
                </motion.div>
              ) : (
                <motion.div key="etabs" initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -16 }}>
                  <div className="card">
                    <div className="card-body">
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24,
                        padding: '14px 18px', borderRadius: 'var(--radius-md)',
                        background: etabsStatus?.available ? 'var(--pass-bg)' : 'var(--fail-bg)',
                        border: `1px solid ${etabsStatus?.available ? 'var(--pass-border)' : 'var(--fail-border)'}`,
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
                          <div style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
                            {etabsStatus?.message || 'Checking...'}
                          </div>
                        </div>
                      </div>

                      <div style={{ marginBottom: 20, fontSize: 12, color: 'var(--text-tertiary)', lineHeight: 1.8 }}>
                        <strong style={{ color: 'var(--text-secondary)' }}>Requirements:</strong>
                        <ul style={{ paddingLeft: 16, marginTop: 6 }}>
                          <li>Windows OS (COM is Windows-native)</li>
                          <li>ETABS installed and licensed on this machine</li>
                          <li>Python comtypes package ({etabsStatus?.comtypes_installed ? '✓ installed' : '✗ not installed'})</li>
                        </ul>
                      </div>

                      <div style={{ marginBottom: 20 }}>
                        <label style={{
                          fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6,
                          color: 'var(--text-secondary)',
                        }}>
                          ETABS Model Path (.edb) — optional
                        </label>
                        <input
                          type="text"
                          value={etabsModelPath}
                          onChange={(e) => setEtabsModelPath(e.target.value)}
                          placeholder="C:\Projects\Building Model.edb"
                          style={{
                            width: '100%', padding: '10px 14px', fontSize: 13,
                            fontFamily: "'JetBrains Mono', monospace",
                          }}
                        />
                      </div>

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

                      <p style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 14, textAlign: 'center' }}>
                        Connects directly to a running ETABS instance via COM API.
                        Make sure ETABS is open with your model loaded.
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Database contents info */}
            {importMode === 'database' && (
              <div className="card" style={{ marginTop: 28 }}>
                <div className="card-body">
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                    <AlertTriangle size={18} style={{ color: 'var(--warn)', marginTop: 2, flexShrink: 0 }} />
                    <div>
                      <h4 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Expected Database Contents</h4>
                      <ul style={{ fontSize: 12, color: 'var(--text-tertiary)', lineHeight: 2, paddingLeft: 16 }}>
                        <li><strong style={{ color: 'var(--text-secondary)' }}>Center Mass Rigidity</strong> — XCM, YCM, XCR, YCR, Mass per storey</li>
                        <li><strong style={{ color: 'var(--text-secondary)' }}>Story Data</strong> — Storey heights and elevations</li>
                        <li><strong style={{ color: 'var(--text-secondary)' }}>Story Shears</strong> — VX, VY for unit load cases (UL1, UL2, UL3)</li>
                        <li><strong style={{ color: 'var(--text-secondary)' }}>Displacement data</strong> — UX, UY, RZ for unit load cases</li>
                        <li><strong style={{ color: 'var(--text-secondary)' }}>Diaphragm Mass Data</strong> — Mass distribution per storey</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// ─── Styles ────────────────────────────────────────────────────────────────
const styles = {
  fileInfoBar: {
    display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px',
    background: 'var(--bg-surface)', border: '1px solid var(--border-primary)',
    borderRadius: 'var(--radius-md)', marginBottom: 20,
    fontFamily: "'JetBrains Mono', monospace",
  },
  progressContainer: {
    background: 'var(--bg-surface)', border: '1px solid var(--border-primary)',
    borderRadius: 'var(--radius-lg)', overflow: 'hidden', marginBottom: 16,
  },
  overallBar: { padding: '16px 20px 0' },
  overallBarTrack: {
    height: 6, background: 'var(--bg-subtle)', borderRadius: 3,
    overflow: 'hidden', position: 'relative',
  },
  overallBarFill: {
    height: '100%', background: 'linear-gradient(90deg, var(--accent), #60A5FA)',
    borderRadius: 3, transition: 'width 0.6s ease',
  },
  completeCheckmark: {
    position: 'absolute', right: -2, top: '50%', transform: 'translateY(-50%)',
    color: 'var(--pass)', background: 'white', borderRadius: '50%',
  },
  overallLabel: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    marginTop: 8, paddingBottom: 0,
  },
  overallPercent: {
    fontSize: 13, fontWeight: 700, color: 'var(--text-primary)',
    fontFamily: "'JetBrains Mono', monospace",
  },
  overallTime: {
    fontSize: 11, color: 'var(--text-tertiary)', display: 'flex', alignItems: 'center',
    fontFamily: "'JetBrains Mono', monospace",
  },
  stagesList: { padding: '12px 20px 16px' },
  stageItem: {
    display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0',
    position: 'relative', transition: 'opacity 0.3s ease',
  },
  stageIcon: {
    width: 32, height: 32, borderRadius: 'var(--radius-sm)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0, transition: 'all 0.3s ease',
  },
  stageText: { flex: 1, minWidth: 0 },
  stageLabel: {
    fontSize: 13, transition: 'all 0.3s ease',
  },
  stageDesc: {
    fontSize: 11, color: 'var(--text-tertiary)', marginTop: 1,
    fontFamily: "'JetBrains Mono', monospace",
  },
  pulseIndicator: {
    width: 6, height: 6, borderRadius: '50%',
    background: 'var(--accent)', flexShrink: 0,
  },
  elapsedFooter: {
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
    padding: '12px 16px', borderTop: '1px solid var(--border-subtle)',
    fontSize: 11, color: 'var(--text-tertiary)', fontWeight: 500,
  },
  statsContainer: {
    background: 'var(--bg-surface)', border: '1px solid var(--border-primary)',
    borderRadius: 'var(--radius-lg)', overflow: 'hidden', marginBottom: 16,
  },
  statsLabel: {
    display: 'flex', alignItems: 'center', gap: 6, padding: '12px 16px',
    fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)',
    textTransform: 'uppercase', letterSpacing: '0.05em',
    borderBottom: '1px solid var(--border-subtle)',
  },
  statsGrid: { padding: '14px 16px', display: 'grid', gridTemplateColumns: '1fr 1fr 80px', gap: 12, alignItems: 'center' },
  statItem: { minWidth: 0 },
  statHeader: {
    display: 'flex', alignItems: 'center', gap: 5, marginBottom: 6,
    fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)',
  },
  statValue: {
    marginLeft: 'auto', fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11, fontWeight: 700, color: 'var(--text-primary)',
  },
  statSub: { fontWeight: 400, color: 'var(--text-tertiary)' },
  progressTrack: {
    height: 4, background: 'var(--bg-subtle)', borderRadius: 2, overflow: 'hidden',
  },
  progressBar: {
    height: '100%', borderRadius: 2,
  },
  sparkline: {
    borderLeft: '1px solid var(--border-subtle)', paddingLeft: 10,
  },
}
