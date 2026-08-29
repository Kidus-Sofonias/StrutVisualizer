import { motion } from 'framer-motion'

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
  return (
    <div className="storey-panel-list">
      {storeys.map((storey, idx) => {
        const status = getStoreyStatus(storey, activeModule)
        const isSelected = selectedStorey?.id === storey.id
        return (
          <motion.div
            key={storey.id}
            className={`storey-panel-item ${isSelected ? 'selected' : ''}`}
            onClick={() => onSelectStorey(storey)}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.02 }}
          >
            <div className={`storey-panel-indicator ${status}`} />
            <span className="storey-panel-name">{storey.name}</span>
            {status !== 'na' && (
              <span className={`storey-panel-badge ${status}`}>
                {status === 'pass' ? 'OK' : 'FAIL'}
              </span>
            )}
          </motion.div>
        )
      })}
    </div>
  )
}
