import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, BarChart3, FileText, GitCompare, CheckCircle2, XCircle, Home, Sun, Moon, Layers, Settings } from 'lucide-react'
import BuildingVisualization from './components/BuildingVisualization'
import StoreyDetail from './components/StoreyDetail'
import CalculationTable from './components/CalculationTable'
import ProjectUpload from './components/ProjectUpload'
import CompareView from './components/CompareView'
import ExportPanel from './components/ExportPanel'
import SectionView from './components/SectionView'
import SettingsPage from './components/SettingsPage'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8007'

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

const IMPORT_STAGES = [
  { id: 'uploading',    duration: 3 },
  { id: 'reading',      duration: 5 },
  { id: 'tables',       duration: 8 },
  { id: 'calculating',  duration: 10 },
  { id: 'extended',     duration: 6 },
  { id: 'wrapping',     duration: 3 },
]

function App() {
  const [projects, setProjects] = useState([])
  const [activeProject, setActiveProject] = useState(null)
  const [selectedStorey, setSelectedStorey] = useState(null)
  const [activeModule, setActiveModule] = useState('3.2.2')
  const [activeSection, setActiveSection] = useState('3.2')
  const [activeView, setActiveView] = useState('dashboard')
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(false)
  const [uploadStage, setUploadStage] = useState(IMPORT_STAGES[0].id)
  const [uploadElapsed, setUploadElapsed] = useState(0)
  const stageTimerRef = useRef(null)
  const elapsedRef = useRef(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const sidebarCloseTimer = useRef(null)
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('app_settings')
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS
    } catch {
      return DEFAULT_SETTINGS
    }
  })

  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
    }
  }, [settings.theme])

  useEffect(() => {
    const sizes = { small: '13px', medium: '14px', large: '16px' }
    document.documentElement.style.fontSize = sizes[settings.fontSize] || '14px'
  }, [settings.fontSize])

  const updateSettings = (newSettings) => {
    setSettings(newSettings)
    localStorage.setItem('app_settings', JSON.stringify(newSettings))
  }

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const loadProjects = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/projects`)
      const data = await res.json()
      setProjects(data.projects || [])
    } catch (e) {
      console.error('Failed to load projects:', e)
    }
  }, [])

  const loadProject = useCallback(async (id) => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/projects/${id}`)
      const data = await res.json()
      setActiveProject(data)
      setSelectedStorey(data.storeys[0] || null)
      setActiveView('analysis')
      setActiveSection('3.2')
    } catch {
      showNotification('Failed to load project', 'error')
    }
    setLoading(false)
  }, [])

  const startProgressTimer = useCallback(() => {
    setUploadProgress(true)
    setUploadStage(IMPORT_STAGES[0].id)
    setUploadElapsed(0)

    const startTime = Date.now()
    elapsedRef.current = setInterval(() => {
      setUploadElapsed(Math.floor((Date.now() - startTime) / 1000))
    }, 500)

    let stageIdx = 0
    let accumulated = 0
    stageTimerRef.current = setInterval(() => {
      accumulated += 0.5
      setUploadElapsed(Math.floor((Date.now() - startTime) / 1000))
      while (stageIdx < IMPORT_STAGES.length - 1 && accumulated >= IMPORT_STAGES[stageIdx].duration) {
        stageIdx++
        setUploadStage(IMPORT_STAGES[stageIdx].id)
      }
    }, 500)
  }, [stageTimerRef, elapsedRef])

  const stopProgressTimer = useCallback(() => {
    if (stageTimerRef.current) clearInterval(stageTimerRef.current)
    if (elapsedRef.current) clearInterval(elapsedRef.current)
    stageTimerRef.current = null
    elapsedRef.current = null
  }, [stageTimerRef, elapsedRef])

  const handleUpload = async (file) => {
    setLoading(true)
    startProgressTimer()
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API}/api/upload`, { method: 'POST', body: formData })
      const data = await res.json()
      if (data.status === 'success') {
        setUploadStage('wrapping')
        showNotification(`Imported ${data.storeys_imported} storeys from ${data.project_name}`)
        await loadProjects()
        await loadProject(data.project_id)
      } else {
        showNotification(data.message || 'Upload failed', 'error')
      }
    } catch (e) {
      showNotification('Upload failed: ' + e.message, 'error')
    }
    stopProgressTimer()
    setUploadProgress(false)
    setLoading(false)
  }

  const handleLoadLocal = async (filename) => {
    setLoading(true)
    startProgressTimer()
    try {
      const res = await fetch(`${API}/api/load-local`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename }),
      })
      const data = await res.json()
      if (data.status === 'success') {
        setUploadStage('wrapping')
        showNotification(`Loaded ${data.storeys_imported} storeys from ${data.project_name}`)
        await loadProjects()
        await loadProject(data.project_id)
      } else {
        showNotification(data.detail || 'Load failed', 'error')
      }
    } catch (e) {
      showNotification('Load failed: ' + e.message, 'error')
    }
    stopProgressTimer()
    setUploadProgress(false)
    setLoading(false)
  }

  const handleExport = async (format) => {
    if (!activeProject) return
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: activeProject.project_id, format }),
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report_${activeProject.project_name}.${format === 'excel' ? 'xlsx' : 'pdf'}`
        a.click()
        window.URL.revokeObjectURL(url)
        showNotification(`Exported ${format.toUpperCase()} report`)
      } else {
        showNotification('Export failed', 'error')
      }
    } catch (e) {
      showNotification('Export failed: ' + e.message, 'error')
    }
    setLoading(false)
  }

  useEffect(() => { loadProjects() }, [loadProjects])

  const sections = [
    { id: '3.2', label: '3.2', name: 'Regularity' },
    { id: '3.3', label: '3.3', name: 'Classification' },
    { id: '3.4', label: '3.4', name: 'q-Factor' },
    { id: '4.1', label: '4.1', name: 'Base Shear' },
    { id: '4.2', label: '4.2', name: 'Modal' },
    { id: '4.3', label: '4.3', name: 'Imperfection' },
    { id: '4.4', label: '4.4', name: 'Stability' },
    { id: '4.5', label: '4.5', name: 'Drift' },
    { id: '4.6', label: '4.6', name: 'Overturning' },
  ]

  const modules_3_2 = ['3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.2.5', '3.2.6', '3.2.7', '3.2.8']

  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'upload', icon: Upload, label: 'Import' },
    { id: 'analysis', icon: BarChart3, label: 'Analysis' },
    { id: 'compare', icon: GitCompare, label: 'Compare' },
    { id: 'export', icon: FileText, label: 'Export' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ]

  const handleSidebarEnter = useCallback(() => {
    if (sidebarCloseTimer.current) clearTimeout(sidebarCloseTimer.current)
    setSidebarOpen(true)
  }, [])

  const handleSidebarLeave = useCallback(() => {
    sidebarCloseTimer.current = setTimeout(() => setSidebarOpen(false), 250)
  }, [])

  return (
    <div className="app">
      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            className={`notification ${notification.type}`}
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
          >
            {notification.type === 'success' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
            {notification.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Base Icon Rail (always visible) ── */}
      <div
        className="sidebar"
        onMouseEnter={handleSidebarEnter}
        onMouseLeave={handleSidebarLeave}
      >
        <div className="sidebar-logo" onClick={() => setActiveView('dashboard')}>
          <Layers size={18} style={{ color: 'var(--accent)' }} />
        </div>

        <div className="sidebar-nav-rail">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-item-rail ${activeView === item.id ? 'active' : ''}`}
              onClick={() => setActiveView(item.id)}
              title={item.label}
            >
              <item.icon size={18} />
            </button>
          ))}
        </div>

        <div className="sidebar-project-rail">
          {projects.map((p, i) => (
            <button
              key={p.id}
              className={`project-dot-rail ${activeProject?.project_id === p.id ? 'active' : ''}`}
              onClick={() => loadProject(p.id)}
              title={p.name}
            >
              {i + 1}
            </button>
          ))}
        </div>

        <div className="sidebar-bottom-rail">
          <button
            className="nav-item-rail"
            onClick={() => updateSettings({ ...settings, theme: settings.theme === 'dark' ? 'light' : 'dark' })}
            title={settings.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          >
            {settings.theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>

      {/* ── YouTube-style Floating Overlay ── */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onMouseEnter={handleSidebarEnter}
        onMouseLeave={handleSidebarLeave}
      >
        <div className="sidebar-overlay-logo" onClick={() => { setActiveView('dashboard'); setSidebarOpen(false) }}>
          <Layers size={18} style={{ color: 'var(--accent)' }} />
        </div>

        <div className="sidebar-overlay-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`sidebar-overlay-item ${activeView === item.id ? 'active' : ''}`}
              onClick={() => { setActiveView(item.id); setSidebarOpen(false) }}
            >
              <span className="sidebar-overlay-item-icon">
                <item.icon size={20} />
              </span>
              {item.label}
            </button>
          ))}
        </div>

        <div className="sidebar-overlay-divider" />

        <div className="sidebar-overlay-section-label">Projects</div>

        <div className="sidebar-overlay-projects">
          {projects.map((p, i) => (
            <button
              key={p.id}
              className={`sidebar-overlay-project ${activeProject?.project_id === p.id ? 'active' : ''}`}
              onClick={() => { loadProject(p.id); setSidebarOpen(false) }}
            >
              <span className="sidebar-overlay-project-num">{i + 1}</span>
              {p.name}
            </button>
          ))}
        </div>

        <div className="sidebar-overlay-bottom">
          <button
            className="sidebar-overlay-item"
            onClick={() => { updateSettings({ ...settings, theme: settings.theme === 'dark' ? 'light' : 'dark' }); setSidebarOpen(false) }}
          >
            <span className="sidebar-overlay-item-icon">
              {settings.theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </span>
            {settings.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </div>

      {/* ── Main Content ── */}
      <div className="main-content">
        <div className="main-header">
          <h2>
            {activeView === 'analysis' && activeProject
              ? `${activeProject.project_name}`
              : activeView === 'dashboard' ? 'Dashboard'
              : activeView === 'upload' ? 'Import Data'
              : activeView === 'compare' ? 'Compare Projects'
              : activeView === 'export' ? 'Export Report'
              : activeView === 'settings' ? 'Settings'
              : 'StrutVisualizer'
            }
          </h2>
          <div className="header-actions">
            {loading && <div className="spinner" />}
            {activeProject && activeView === 'analysis' && (
              <span style={{ fontSize: 11, color: 'var(--text-tertiary)', fontFamily: "'JetBrains Mono', monospace" }}>
                {activeProject.storeys?.length || 0} storeys
              </span>
            )}
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* ── Dashboard ── */}
          {activeView === 'dashboard' && (
            <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="main-scroll">
              <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center', paddingTop: 80 }}>
                <div style={{
                  width: 64, height: 64, borderRadius: 'var(--radius-xl)',
                  background: 'var(--accent-subtle)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 20px', border: '1px solid var(--accent-muted)',
                }}>
                  <Layers size={28} style={{ color: 'var(--accent)' }} />
                </div>
                <h2 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8, letterSpacing: '-0.02em' }}>
                  Structural Analysis Platform
                </h2>
                <p style={{ color: 'var(--text-tertiary)', fontSize: 14, maxWidth: 440, margin: '0 auto 32px', lineHeight: 1.6 }}>
                  Import ETABS model data and perform storey-by-storey
                  structural regularity analysis per Eurocode 8.
                </p>
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                  <button className="primary-btn" onClick={() => setActiveView('upload')} style={{ padding: '11px 24px', fontSize: 13 }}>
                    <Upload size={16} /> Import Data
                  </button>
                  {projects.length > 0 && (
                    <button className="secondary-btn" onClick={() => loadProject(projects[0].id)} style={{ padding: '11px 24px', fontSize: 13 }}>
                      <BarChart3 size={16} /> View Latest
                    </button>
                  )}
                </div>
                {projects.length > 0 && (
                  <div style={{ marginTop: 44, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, textAlign: 'left' }}>
                    <div className="data-card">
                      <div className="label">Projects</div>
                      <div className="value">{projects.length}</div>
                    </div>
                    <div className="data-card">
                      <div className="label">Storeys</div>
                      <div className="value">{projects.reduce((s, p) => s + (p.storeys || 0), 0)}</div>
                    </div>
                    <div className="data-card">
                      <div className="label">Sections</div>
                      <div className="value">9</div>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* ── Upload ── */}
          {activeView === 'upload' && (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="main-scroll">
              <ProjectUpload onUpload={handleUpload} onLoadLocal={handleLoadLocal} loading={loading} uploadProgress={uploadProgress} uploadStage={uploadStage} uploadElapsed={uploadElapsed} />
            </motion.div>
          )}

          {/* ── Analysis (Three-Column Layout) ── */}
          {activeView === 'analysis' && activeProject && (
            <motion.div key="analysis" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="analysis-layout">
              {/* Section Tabs */}
              <div className="section-tabs">
                {sections.map(s => (
                  <button
                    key={s.id}
                    className={`section-tab ${activeSection === s.id ? 'active' : ''}`}
                    onClick={() => setActiveSection(s.id)}
                  >
                    <span className="section-label">{s.label}</span>
                    <span className="section-name">{s.name}</span>
                  </button>
                ))}
              </div>

              {/* Module Tabs */}
              {activeSection === '3.2' && (
                <div className="module-tabs">
                  {modules_3_2.map(m => (
                    <button
                      key={m}
                      className={`module-tab ${activeModule === m ? 'active' : ''}`}
                      onClick={() => setActiveModule(m)}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              )}

              {/* Three-Column Content */}
              {activeSection === '3.2' ? (
                <div className="analysis-three-col">
                  {/* Left: Storey List */}
                  <div className="storey-panel">
                    <div className="storey-panel-header">
                      <h3>Building Storeys</h3>
                      <div className="subtitle">{activeProject.storeys.length} levels</div>
                    </div>
                    <BuildingVisualization
                      storeys={activeProject.storeys}
                      selectedStorey={selectedStorey}
                      onSelectStorey={setSelectedStorey}
                      activeModule={activeModule}
                    />
                  </div>

                  {/* Center: Tables + Charts */}
                  <div className="center-panel">
                    <CalculationTable
                      storeys={activeProject.storeys}
                      module={activeModule}
                      onSelectStorey={setSelectedStorey}
                      selectedStorey={selectedStorey}
                    />
                  </div>

                  {/* Right: Floor Detail */}
                  <div className="detail-panel">
                    {selectedStorey && (
                      <StoreyDetail
                        storey={selectedStorey}
                        module={activeModule}
                      />
                    )}
                  </div>
                </div>
              ) : (
                <div className="main-scroll">
                  <SectionView section={activeSection} project={activeProject} />
                </div>
              )}
            </motion.div>
          )}

          {/* ── Empty States ── */}
          {activeView === 'analysis' && !activeProject && (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="empty-state" style={{ height: '100%' }}>
              <BarChart3 size={48} strokeWidth={1.2} />
              <h2>No Project Selected</h2>
              <p>Select a project from the sidebar or import a new database</p>
            </motion.div>
          )}

          {activeView === 'compare' && (
            <motion.div key="compare" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="main-scroll">
              <CompareView projects={projects} api={API} />
            </motion.div>
          )}

          {activeView === 'export' && activeProject && (
            <motion.div key="export" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="main-scroll">
              <ExportPanel project={activeProject} onExport={handleExport} settings={settings} />
            </motion.div>
          )}

          {activeView === 'export' && !activeProject && (
            <motion.div key="export-empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="empty-state" style={{ height: '100%' }}>
              <FileText size={48} strokeWidth={1.2} />
              <h2>No Project Selected</h2>
              <p>Select a project from the sidebar to export its report</p>
            </motion.div>
          )}

          {activeView === 'settings' && (
            <motion.div key="settings" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="main-scroll">
              <SettingsPage settings={settings} onUpdate={updateSettings} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default App
