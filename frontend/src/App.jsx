import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Building2, Upload, BarChart3, FileText, GitCompare, ChevronRight, AlertTriangle, CheckCircle2, XCircle, Home, Sun, Moon, Layers } from 'lucide-react'
import BuildingVisualization from './components/BuildingVisualization'
import StoreyDetail from './components/StoreyDetail'
import CalculationTable from './components/CalculationTable'
import ProjectUpload from './components/ProjectUpload'
import CompareView from './components/CompareView'
import ExportPanel from './components/ExportPanel'
import SectionView from './components/SectionView'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'

function App() {
  const [projects, setProjects] = useState([])
  const [activeProject, setActiveProject] = useState(null)
  const [selectedStorey, setSelectedStorey] = useState(null)
  const [activeModule, setActiveModule] = useState('3.2.2')
  const [activeSection, setActiveSection] = useState('3.2')
  const [activeView, setActiveView] = useState('dashboard')
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved !== null ? JSON.parse(saved) : true
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light')
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const loadProjects = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/projects`)
      const data = await res.json()
      setProjects(data.projects)
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

  const handleExport = async (format) => {
    if (!activeProject) return
    try {
      const res = await fetch(`${API}/api/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: activeProject.project_id, format }),
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report_${activeProject.project_name}.${format === 'excel' ? 'xlsx' : 'pdf'}`
        a.click()
        URL.revokeObjectURL(url)
        showNotification(`Exported ${format.toUpperCase()} report`)
      }
    } catch (e) {
      showNotification('Export failed', 'error')
    }
  }

  useEffect(() => { loadProjects() }, [loadProjects])

  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'upload', icon: Upload, label: 'Import' },
    { id: 'analysis', icon: BarChart3, label: 'Analysis' },
    { id: 'compare', icon: GitCompare, label: 'Compare' },
    { id: 'export', icon: FileText, label: 'Export' },
  ]

  const sections = [
    { id: '3.2', label: '3.2', name: 'Regularity' },
    { id: '3.3', label: '3.3', name: 'Classification' },
    { id: '3.4', label: '3.4', name: 'Behavior Factor' },
    { id: '4.1', label: '4.1', name: 'Base Shear' },
    { id: '4.2', label: '4.2', name: 'Modal' },
    { id: '4.3', label: '4.3', name: 'Imperfection' },
    { id: '4.4', label: '4.4', name: 'Stability' },
    { id: '4.5', label: '4.5', name: 'Drift' },
    { id: '4.6', label: '4.6', name: 'Overturning' },
  ]

  const modules_3_2 = ['3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.2.5', '3.2.6', '3.2.7', '3.2.8']

  return (
    <div className="app" data-theme={darkMode ? 'dark' : 'light'}>
      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            className={`notification ${notification.type}`}
            initial={{ y: -60, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -60, opacity: 0 }}
          >
            {notification.type === 'success' ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
            {notification.msg}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-logo">
          <Building2 size={28} />
          <span>StructAnalyst</span>
        </div>
        <div className="nav-items">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-btn ${activeView === item.id ? 'active' : ''}`}
              onClick={() => setActiveView(item.id)}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
        <div className="sidebar-projects">
          <div className="sidebar-section-title">Projects</div>
          {projects.map(p => (
            <button
              key={p.id}
              className={`project-btn ${activeProject?.project_id === p.id ? 'active' : ''}`}
              onClick={() => loadProject(p.id)}
            >
              <span className="project-name">{p.name}</span>
              <span className="project-count">{p.storeys} storeys</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="content-header">
          <div className="header-left">
            <h1>
              {activeView === 'dashboard' && 'Project Dashboard'}
              {activeView === 'upload' && 'Import Database'}
              {activeView === 'analysis' && 'Structural Analysis'}
              {activeView === 'compare' && 'Compare Projects'}
              {activeView === 'export' && 'Export Report'}
            </h1>
            {activeProject && (
              <div className="header-breadcrumb">
                <span>{activeProject.project_name}</span>
                {selectedStorey && activeSection === '3.2' && (
                  <>
                    <ChevronRight size={14} />
                    <span>{selectedStorey.name}</span>
                  </>
                )}
              </div>
            )}
          </div>
          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        {/* Views */}
        <div className="content-body">
          {loading && (
            <div className="loading-overlay">
              <div className="spinner" />
              <span>Processing...</span>
            </div>
          )}

          {activeView === 'dashboard' && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="dashboard">
              {projects.length === 0 ? (
                <div className="empty-state">
                  <Building2 size={64} strokeWidth={1} />
                  <h2>No Projects Loaded</h2>
                  <p>Import an Access database (.mdb) to begin structural analysis</p>
                  <button className="primary-btn" onClick={() => setActiveView('upload')}>
                    <Upload size={18} /> Import Database
                  </button>
                </div>
              ) : (
                <div className="dashboard-grid">
                  {projects.map(p => (
                    <motion.div key={p.id} className="dash-card" whileHover={{ scale: 1.02 }} onClick={() => loadProject(p.id)}>
                      <Building2 size={32} className="dash-icon" />
                      <h3>{p.name}</h3>
                      <div className="dash-stats">
                        <div className="stat">
                          <span className="stat-value">{p.storeys}</span>
                          <span className="stat-label">Storeys</span>
                        </div>
                        <div className="stat">
                          <span className="stat-value">{p.client || '—'}</span>
                          <span className="stat-label">Client</span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeView === 'upload' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <ProjectUpload onUpload={handleUpload} loading={loading} />
            </motion.div>
          )}

          {activeView === 'analysis' && activeProject && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="analysis-layout">
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

              {/* Section Content */}
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
                <SectionView
                  section={activeSection}
                  project={activeProject}
                />
              )}
            </motion.div>
          )}

          {activeView === 'analysis' && !activeProject && (
            <div className="empty-state">
              <BarChart3 size={64} strokeWidth={1} />
              <h2>No Project Selected</h2>
              <p>Select a project from the sidebar or import a new database</p>
            </div>
          )}

          {activeView === 'compare' && <CompareView projects={projects} api={API} />}

          {activeView === 'export' && activeProject && <ExportPanel project={activeProject} onExport={handleExport} />}

          {activeView === 'export' && !activeProject && (
            <div className="empty-state">
              <FileText size={64} strokeWidth={1} />
              <h2>No Project Selected</h2>
              <p>Select a project to export its report</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
