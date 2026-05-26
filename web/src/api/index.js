import axios from 'axios'

const api = axios.create({
  baseURL: '/',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const healthCheck = () => api.get('/health')

// Data management
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

// Prediction
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

export default api
