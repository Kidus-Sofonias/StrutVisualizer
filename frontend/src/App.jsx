import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Building2, Upload, BarChart3, FileText, GitCompare, ChevronRight, AlertTriangle, CheckCircle2, XCircle, Home, Sun, Moon, Layers, Settings } from 'lucide-react'
import BuildingVisualization from './components/BuildingVisualization'
import StoreyDetail from './components/StoreyDetail'
import CalculationTable from './components/CalculationTable'
import ProjectUpload from './components/ProjectUpload'
import CompareView from './components/CompareView'
import ExportPanel from './components/ExportPanel'
import SectionView from './components/SectionView'
import SettingsPage from './components/SettingsPage'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'

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

function App() {
  const [projects, setProjects] = useState([])
  const [activeProject, setActiveProject] = useState(null)
  const [selectedStorey, setSelectedStorey] = useState(null)
  const [activeModule, setActiveModule] = useState('3.2.2')
  const [activeSection, setActiveSection] = useState('3.2')
  const [activeView, setActiveView] = useState('dashboard')
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)
  const [settings, setSettings] = useState(() => {
    try {
      const saved = localStorage.getItem('app_settings')
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS
    } catch {
      return DEFAULT_SETTINGS
    }
  })

  // Apply theme
  useEffect(() => {
    if (settings.theme === 'dark') {
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
    }
  }, [settings.theme])

  // Apply font size
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
    } catch (e) {
      showNotification('Failed to load project', 'error')
    }
    setLoading(false)
  }, [])

  const handleUpload = async (file) => {
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API}/api/upload`, { method: 'POST', body: formData })
      const data = await res.json()
      if (data.status === 'success') {
        showNotification(`Imported ${data.storeys_imported} storeys from ${data.project_name}`)
        await loadProjects()
        await loadProject(data.project_id)
      } else {
        showNotification(data.message || 'Upload failed', 'error')
      }
    } catch (e) {
      showNotification('Upload failed: ' + e.message, 'error')
    }
    setLoading(false)
  }

  const handleLoadLocal = async (filename) => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/load-local`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename }),
      })
      const data = await res.json()
      if (data.status === 'success') {
        showNotification(`Loaded ${data.storeys_imported} storeys from ${data.project_name}`)
        await loadProjects()
        await loadProject(data.project_id)
      } else {
        showNotification(data.detail || 'Load failed', 'error')
      }
    } catch (e) {
      showNotification('Load failed: ' + e.message, 'error')
    }
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

  const deleteProject = async (id) => {
    try {
      await fetch(`${API}/api/projects/${id}`, { method: 'DELETE' })
      if (activeProject?.project_id === id) {
        setActiveProject(null)
        setSelectedStorey(null)
        setActiveView('dashboard')
      }
      await loadProjects()
      showNotification('Project deleted')
    } catch (e) {
      showNotification('Delete failed', 'error')
    }
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

  const modules_3_2 = ['3.2.2', '3.2.3', '3.2.4', '3.2.5', '3.2.6', '3.2.7', '3.2.8']

  return (
    <div className="app">
      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            className={`notification ${notification.type}`}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {notification.type === 'success' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
            {notification.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <Layers size={20} style={{ color: 'var(--accent)' }} />
          <div>
            <h1>StrutVisualizer</h1>
            <p>Structural Analysis</p>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-label">Navigation</div>
        </div>
        {[
          { id: 'dashboard', icon: Home, label: 'Dashboard' },
          { id: 'upload', icon: Upload, label: 'Import Data' },
          { id: 'analysis', icon: BarChart3, label: 'Analysis' },
          { id: 'compare', icon: GitCompare, label: 'Compare' },
          { id: 'export', icon: FileText, label: 'Export' },
          { id: 'settings', icon: Settings, label: 'Settings' },
        ].map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => setActiveView(item.id)}
          >
            <item.icon size={16} />
            {item.label}
          </button>
        ))}

        {/* Projects */}
        <div className="nav-section">
          <div className="nav-label">Projects ({projects.length})</div>
        </div>
        <div className="project-list">
          {projects.map(p => (
            <div
              key={p.id}
              className={`project-item ${activeProject?.project_id === p.id ? 'active' : ''}`}
              onClick={() => loadProject(p.id)}
            >
              <Building2 size={14} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {p.name}
                </div>
                {p.created && (
                  <div className="time">{p.created.replace(/_/g, ' ').slice(0, 19)}</div>
                )}
              </div>
              <span className="storeys">{p.storeys}S</span>
            </div>
          ))}
          {projects.length === 0 && (
            <p style={{ fontSize: 11, color: 'var(--text-muted)', padding: '8px 12px' }}>
              No projects loaded
            </p>
          )}
        </div>

        {/* Theme Toggle */}
        <div style={{ padding: '12px 16px', marginTop: 'auto', borderTop: '1px solid var(--border)' }}>
          <button
            className="nav-item"
            onClick={() => updateSettings({ ...settings, theme: settings.theme === 'dark' ? 'light' : 'dark' })}
            style={{ justifyContent: 'center' }}
          >
            {settings.theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            {settings.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Views */}
        {activeView === 'dashboard' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-scroll">
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <Layers size={64} strokeWidth={1} style={{ color: 'var(--accent)', marginBottom: 16 }} />
              <h2 style={{ fontSize: 24, marginBottom: 8 }}>Structural Engineering Analysis</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: 14, maxWidth: 500, margin: '0 auto' }}>
                Import your ETABS model data via Access database (.mdb) or direct ETABS API connection.
                Perform storey-by-storey structural regularity analysis per Eurocode 8.
              </p>
              <div style={{ marginTop: 32, display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button className="primary-btn" onClick={() => setActiveView('upload')} style={{ padding: '12px 24px' }}>
                  <Upload size={18} /> Import Data
                </button>
                {projects.length > 0 && (
                  <button className="secondary-btn" onClick={() => loadProject(projects[0].id)} style={{ padding: '12px 24px' }}>
                    <BarChart3 size={18} /> View Latest
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {activeView === 'upload' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-scroll">
            <ProjectUpload onUpload={handleUpload} onLoadLocal={handleLoadLocal} loading={loading} />
          </motion.div>
        )}

        {activeView === 'analysis' && activeProject && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="analysis-layout">
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

            {activeSection === '3.2' && (
              <>
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
                <div className="analysis-content">
                  <div className="building-panel">
                    <BuildingVisualization
                      storeys={activeProject.storeys}
                      selectedStorey={selectedStorey}
                      onSelectStorey={setSelectedStorey}
                      activeModule={activeModule}
                    />
                  </div>
                  <div className="detail-panel">
                    {selectedStorey && (
                      <StoreyDetail
                        storey={selectedStorey}
                        module={activeModule}
                        projectName={activeProject.project_name}
                      />
                    )}
                  </div>
                </div>
                <CalculationTable
                  storeys={activeProject.storeys}
                  module={activeModule}
                  onSelectStorey={setSelectedStorey}
                />
              </>
            )}

            {activeSection !== '3.2' && (
              <div className="main-scroll">
                <SectionView
                  section={activeSection}
                  project={activeProject}
                />
              </div>
            )}
          </motion.div>
        )}

        {activeView === 'analysis' && !activeProject && (
          <div className="empty-state" style={{ height: '100%' }}>
            <BarChart3 size={64} strokeWidth={1} />
            <h2>No Project Selected</h2>
            <p>Select a project from the sidebar or import a new database</p>
          </div>
        )}

        {activeView === 'compare' && <CompareView projects={projects} api={API} />}

        {activeView === 'export' && activeProject && (
          <div className="main-scroll">
            <ExportPanel project={activeProject} onExport={handleExport} settings={settings} />
          </div>
        )}

        {activeView === 'export' && !activeProject && (
          <div className="empty-state" style={{ height: '100%' }}>
            <FileText size={64} strokeWidth={1} />
            <h2>No Project Selected</h2>
            <p>Select a project to export its report</p>
          </div>
        )}

        {activeView === 'settings' && (
          <div className="main-scroll">
            <SettingsPage settings={settings} onUpdate={updateSettings} />
          </div>
        )}
      </div>
    </div>
  )
}

export default App
