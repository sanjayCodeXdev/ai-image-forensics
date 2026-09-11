import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120_000, // 2 min — allow time for model inference
})

// ── Request interceptor ──────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => config,
  (error)  => Promise.reject(error),
)

// ── Response interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg =
      error.response?.data?.detail ||
      error.response?.data?.error  ||
      error.message                ||
      'An unexpected error occurred.'
    return Promise.reject(new Error(msg))
  },
)

// ── API methods ───────────────────────────────────────────────────────────────

export const healthCheck = () => api.get('/health').then(r => r.data)

/**
 * Upload an image file and run the full analysis pipeline.
 * @param {File} file
 * @param {(pct: number) => void} onProgress
 */
export const analyzeImage = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  }).then(r => r.data)
}

export const getAnalysis = (analysisId) =>
  api.get(`/analysis/${analysisId}`).then(r => r.data)

export const getReport = (analysisId) =>
  api.get(`/analysis/${analysisId}/report`).then(r => r.data)

export const getImageUrl = (analysisId) => `/api/analysis/${analysisId}/image`

export const getHistory = () =>
  api.get('/history').then(r => r.data)

export const deleteAnalysis = (analysisId) =>
  api.delete(`/history/${analysisId}`)

export default api
