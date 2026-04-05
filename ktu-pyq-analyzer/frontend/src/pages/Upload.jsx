import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, FileText, X, CheckCircle } from 'lucide-react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { uploadPaper } from '../services/api'
import toast from 'react-hot-toast'

export default function UploadPage() {
  const navigate = useNavigate()
  const fileRef = useRef()
  const [file, setFile] = useState(null)
  const [subjectName, setSubjectName] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [examType, setExamType] = useState('Regular')
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [drag, setDrag] = useState(false)

  const handleFile = (f) => {
    const allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']
    if (!allowed.includes(f.type)) { toast.error('Only PDF, JPG, PNG, WEBP files allowed'); return }
    if (f.size > 50 * 1024 * 1024) { toast.error('File must be under 50MB'); return }
    setFile(f)
  }

  const onDrop = (e) => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleSubmit = async () => {
    if (!file || !subjectName.trim() || !year) { toast.error('Fill all required fields'); return }
    setUploading(true); setProgress(0)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('subject_name', subjectName.trim())
    fd.append('year', year)
    fd.append('exam_type', examType)
    try {
      const paper = await uploadPaper(fd, setProgress)
      toast.success('Paper uploaded successfully!')
      navigate(`/processing/${paper.id}`)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 fade-up">
      <div>
        <h1 className="text-3xl font-display font-bold text-white">Upload Paper</h1>
        <p className="text-slate-500 mt-1">Upload a KTU question paper to start tagging questions</p>
      </div>

      <Card>
        {/* Drop Zone */}
        <div
          className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200
            ${drag ? 'border-primary-500 bg-primary-500/5' : 'border-white/15 hover:border-primary-500/50'}
            ${file ? 'border-accent-teal/50 bg-accent-teal/5' : ''}`}
          onDragOver={e => { e.preventDefault(); setDrag(true) }}
          onDragLeave={() => setDrag(false)}
          onDrop={onDrop}
          onClick={() => !file && fileRef.current.click()}
        >
          <input ref={fileRef} type="file" accept=".pdf,.jpg,.jpeg,.png,.webp"
            className="hidden" onChange={e => e.target.files[0] && handleFile(e.target.files[0])} />

          {file ? (
            <div className="space-y-2">
              <CheckCircle size={36} className="mx-auto text-accent-teal" />
              <p className="font-medium text-slate-200">{file.name}</p>
              <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              <Button variant="ghost" size="sm" onClick={e => { e.stopPropagation(); setFile(null) }}>
                <X size={13} /> Remove
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              <UploadIcon size={36} className="mx-auto text-slate-600" />
              <p className="text-slate-300 font-medium">Drop file here or click to browse</p>
              <p className="text-sm text-slate-500">PDF, JPG, PNG, WEBP · Max 50MB</p>
            </div>
          )}
        </div>
      </Card>

      <Card>
        <h2 className="font-display font-semibold text-white mb-4">Paper Details</h2>
        <div className="space-y-4">
          <Input label="Subject Name *" value={subjectName}
            onChange={e => setSubjectName(e.target.value)} placeholder="e.g. Data Structures (CS201)" />

          <div className="grid grid-cols-2 gap-4">
            <Input label="Year *" type="number" value={year}
              onChange={e => setYear(Number(e.target.value))} min="2000" max="2099" />
            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Exam Type</label>
              <select value={examType} onChange={e => setExamType(e.target.value)}
                className="w-full bg-surface-3 border border-white/10 rounded-xl px-3 py-2.5 text-slate-200
                  focus:outline-none focus:border-primary-500 text-sm">
                {['Regular', 'Supplementary', 'Model', 'Internal'].map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </Card>

      {uploading && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Uploading…</span><span>{progress}%</span>
          </div>
          <div className="h-2 bg-surface-3 rounded-full overflow-hidden">
            <div className="h-full bg-primary-500 rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      <Button className="w-full" size="lg" loading={uploading}
        onClick={handleSubmit} disabled={!file || !subjectName}>
        <UploadIcon size={18} /> Upload & Open Viewer
      </Button>
    </div>
  )
}
