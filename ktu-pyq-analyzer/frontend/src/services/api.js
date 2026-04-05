import axios from 'axios'

const BASE = '/api/v1'

const client = axios.create({ baseURL: BASE, timeout: 60000 })

client.interceptors.response.use(
  r => r,
  err => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(msg))
  }
)

// Subjects
export const getSubjects = () => client.get('/subjects').then(r => r.data)
export const createSubject = (data) => client.post('/subjects', data).then(r => r.data)

// Papers
export const uploadPaper = (formData, onProgress) =>
  client.post('/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: e => onProgress?.(Math.round((e.loaded * 100) / e.total)),
  }).then(r => r.data)

export const getPapers = (params) => client.get('/papers', { params }).then(r => r.data)
export const getPaper = (id) => client.get(`/papers/${id}`).then(r => r.data)
export const deletePaper = (id) => client.delete(`/papers/${id}`)

// Questions
export const saveQuestion = (payload) => client.post('/questions', payload).then(r => r.data)
export const getQuestions = (params) => client.get('/questions', { params }).then(r => r.data)
export const updateQuestion = (id, payload) => client.put(`/questions/${id}`, payload).then(r => r.data)
export const deleteQuestion = (id) => client.delete(`/questions/${id}`)
export const processPaper = (id) => client.post(`/papers/${id}/process`).then(r => r.data)

// Analytics
export const getAnalytics = (params) => client.get('/analytics/frequency', { params }).then(r => r.data)
export const getOverview = () => client.get('/analytics/overview').then(r => r.data)
