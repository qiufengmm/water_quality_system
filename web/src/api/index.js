import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Auth Interceptor ────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear and redirect to login
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      localStorage.removeItem('display_name')
      // Don't redirect if already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Health ──────────────────────────────────────────────
export const healthCheck = () => api.get('/health')

// ── Data Management ─────────────────────────────────────
export const uploadCsv = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/api/data/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const simulateData = (stationId, hours, interval) =>
  api.post('/api/data/upload/simulate', null, {
    params: { station_id: stationId, hours, interval },
  })

export const getRawData = (page = 1, pageSize = 10) =>
  api.get('/api/data/raw', { params: { page, page_size: pageSize } })

export const cleanData = (config = {}) =>
  api.post('/api/data/clean', config)

export const getCleanedData = (page = 1, pageSize = 10) =>
  api.get('/api/data/cleaned', { params: { page, page_size: pageSize } })

export const getDataSummary = () =>
  api.get('/api/data/summary')

export const getDataInfo = () =>
  api.get('/api/data/info')

export const getStations = () =>
  api.get('/api/data/stations')

export const deleteRawData = () =>
  api.delete('/api/data/raw')

export const deleteCleanedData = () =>
  api.delete('/api/data/cleaned')

// ── Prediction ──────────────────────────────────────────
export const trainModel = () =>
  api.post('/api/predict/train/from-data')

export const predictBatch = (stationId, days) =>
  api.post('/api/predict/batch', null, {
    params: { station_id: stationId, days },
  })

export const getModelInfo = () =>
  api.get('/api/predict/model-info')

export const getPredictionHistory = () =>
  api.get('/api/predict/history')

// ── Alerting (Week 3) ──────────────────────────────────
export const getAlertRules = () =>
  api.get('/api/alert/rules')

export const updateAlertRules = (rules) =>
  api.put('/api/alert/rules', rules)

export const checkAlerts = () =>
  api.post('/api/alert/check')

export const getAlertHistory = (page = 1, pageSize = 20) =>
  api.get('/api/alert/history', { params: { page, page_size: pageSize } })

export const clearAlertHistory = () =>
  api.delete('/api/alert/history')

// ── Export (Week 3) ─────────────────────────────────────
export const exportRawExcel = () =>
  api.get('/api/export/raw/excel', { responseType: 'blob' })

export const exportCleanedExcel = () =>
  api.get('/api/export/cleaned/excel', { responseType: 'blob' })

export const exportFullReport = () =>
  api.get('/api/export/report', { responseType: 'blob' })

// ── Admin / Auth (Week 3) ───────────────────────────────
export const login = (username, password) =>
  api.post('/api/admin/login', { username, password })

export const registerUser = (username, password, role, displayName) =>
  api.post('/api/admin/register', { username, password, role, display_name: displayName })

export const listUsers = () =>
  api.get('/api/admin/users')

export const getCurrentUser = () =>
  api.get('/api/admin/me')

export const createStation = (data) =>
  api.post('/api/admin/stations', data)

export const updateStation = (stationId, data) =>
  api.put(`/api/admin/stations/${stationId}`, data)

export const deleteStation = (stationId) =>
  api.delete(`/api/admin/stations/${stationId}`)

export default api
