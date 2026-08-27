import { useState } from 'react'
import { motion } from 'framer-motion'
import { Building2, Layers } from 'lucide-react'

const moduleStatusKey = {
  '3.2.1': null,
  '3.2.2': null,
  '3.2.3': null,
  '3.2.4_eox': 'module_3_2_4_eox_status',
  '3.2.4_eoy': 'module_3_2_4_eoy_status',
  '3.2.5_rx': 'module_3_2_5_rx_status',
  '3.2.5_ry': 'module_3_2_5_ry_status',
  '3.2.6': 'module_3_2_6_status',
  '3.2.7': 'module_3_2_7_status',
  '3.2.8': 'module_3_2_8_status_upper',
}

function getStoreyStatus(storey, activeModule) {
  if (activeModule === '3.2.2' || activeModule === '3.2.3') return 'na'
  const key = moduleStatusKey[activeModule]
  if (!key) return 'na'
  const val = storey[key]
  if (!val || val === 'N/A' || val === '-') return 'na'
  return val === 'OK' ? 'pass' : 'fail'
}

export default function BuildingVisualization({ storeys, selectedStorey, onSelectStorey, activeModule }) {
  const [viewMode, setViewMode] = useState('list')

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="building-title">Building Storeys</div>
        <div style={{ display: 'flex', gap: 4 }}>
          <button
            className="secondary-btn"
            style={{ padding: '4px 10px', fontSize: 11 }}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            <Layers size={14} />
          </button>
          <button
            className="secondary-btn"
            style={{ padding: '4px 10px', fontSize: 11 }}
            onClick={() => setViewMode('graphical')}
            title="Graphical view"
          >
            <Building2 size={14} />
          </button>
        </div>
      </div>

      {viewMode === 'list' ? (
        <div className="storey-list">
          {storeys.map((storey, idx) => {
            const status = getStoreyStatus(storey, activeModule)
            const isSelected = selectedStorey?.id === storey.id
            return (
              <motion.div
                key={storey.id}
                className={`storey-item ${isSelected ? 'selected' : ''} ${status}`}
                onClick={() => onSelectStorey(storey)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03 }}
              >
                <div className={`storey-indicator ${status}`} />
                <span className="storey-name">{storey.name}</span>
                {status !== 'na' && (
                  <span className={`storey-badge ${status}`}>
                    {status === 'pass' ? 'OK' : 'FAIL'}
                  </span>
                )}
              </motion.div>
            )
          })}
        </div>
      ) : (
        <GraphicalView
          storeys={storeys}
          selectedStorey={selectedStorey}
          onSelectStorey={onSelectStorey}
          activeModule={activeModule}
        />
      )}
    </div>
  )
}

function GraphicalView({ storeys, selectedStorey, onSelectStorey, activeModule }) {
  const maxHeight = 400
  const storeyHeight = maxHeight / Math.max(storeys.length, 1)

  return (
    <div style={{ position: 'relative', height: maxHeight + 40, display: 'flex', flexDirection: 'column-reverse', gap: 2 }}>
      {storeys.map((storey, idx) => {
        const status = getStoreyStatus(storey, activeModule)
        const isSelected = selectedStorey?.id === storey.id
        const bgColor = isSelected
          ? 'var(--accent)'
          : status === 'fail'
            ? 'rgba(239, 68, 68, 0.3)'
            : status === 'pass'
              ? 'rgba(16, 185, 129, 0.15)'
              : 'var(--bg-tertiary)'
        const borderColor = isSelected
          ? 'var(--accent)'
          : status === 'fail'
            ? 'var(--fail)'
            : 'var(--border)'

        return (
          <motion.div
            key={storey.id}
            onClick={() => onSelectStorey(storey)}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: idx * 0.04, type: 'spring', stiffness: 200 }}
            style={{
              height: Math.max(storeyHeight - 2, 24),
              background: bgColor,
              border: `1px solid ${borderColor}`,
              borderRadius: 4,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0 10px',
              fontSize: 10,
              fontWeight: 500,
              transition: 'all 0.2s',
              boxShadow: isSelected ? '0 0 12px var(--accent-glow)' : 'none',
              transformOrigin: 'left',
            }}
          >
            <span style={{ color: isSelected ? 'white' : 'var(--text-secondary)' }}>
              {storey.name}
            </span>
            {status === 'fail' && (
              <span style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: 'var(--fail)',
                boxShadow: '0 0 6px var(--fail)',
              }} />
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
