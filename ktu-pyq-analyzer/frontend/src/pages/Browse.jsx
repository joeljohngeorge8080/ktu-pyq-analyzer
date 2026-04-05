import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Eye, Trash2, Filter } from 'lucide-react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Select from '../components/ui/Select'
import { useApi } from '../hooks/useApi'
import { getQuestions, getSubjects, deleteQuestion } from '../services/api'
import toast from 'react-hot-toast'

const MODULE_OPTS = [{ value: '', label: 'All Modules' }, ...[1, 2, 3, 4, 5].map(n => ({ value: n, label: `Module ${n}` }))]
const TYPE_OPTS = [{ value: '', label: 'All Types' }, { value: 'short', label: 'Short' }, { value: 'long', label: 'Long' }]
const YEAR_OPTS = [{ value: '', label: 'All Years' }, ...[2024, 2023, 2022, 2021, 2020, 2019, 2018].map(y => ({ value: y, label: String(y) }))]

export default function Browse() {
  const [module_, setModule] = useState('')
  const [type, setType] = useState('')
  const [year, setYear] = useState('')
  const [subjectId, setSubjectId] = useState('')
  const [deleting, setDeleting] = useState(null)

  const { data: subjects } = useApi(getSubjects, [], { initial: [] })
  const subjectOpts = [{ value: '', label: 'All Subjects' }, ...(subjects?.map(s => ({ value: s.id, label: s.name })) ?? [])]

  const { data: questions, loading, reload } = useApi(
    () => getQuestions({ module: module_ || undefined, type: type || undefined, year: year || undefined, subject_id: subjectId || undefined }),
    [module_, type, year, subjectId],
    { initial: [] }
  )

  const handleDelete = async (id) => {
    setDeleting(id)
    try {
      await deleteQuestion(id)
      toast.success('Question deleted')
      reload()
    } catch (e) {
      toast.error(e.message)
    } finally {
      setDeleting(null)
    }
  }

  // Group by module → type
  const grouped = {}
  for (const q of (questions ?? [])) {
    const mk = `Module ${q.module}`
    const tk = q.type === 'short' ? 'Short Answer' : 'Long Answer'
    if (!grouped[mk]) grouped[mk] = {}
    if (!grouped[mk][tk]) grouped[mk][tk] = []
    grouped[mk][tk].push(q)
  }

  return (
    <div className="space-y-6 fade-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Browse Questions</h1>
          <p className="text-slate-500 mt-1">Organized by module and type</p>
        </div>

        {subjectId && (
          <a href={`/api/v1/download/subject?subject_id=${subjectId}`} download className="flex items-center gap-2 bg-primary-500/20 text-primary-400 px-4 py-2 rounded-xl text-sm font-medium hover:bg-primary-500/30 transition-colors">
            Download Subject Dataset
          </a>
        )}
      </div>

      {/* Filters */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <Filter size={14} className="text-primary-400" />
          <span className="text-sm font-medium text-slate-300">Filters</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Select value={subjectId} onChange={setSubjectId} options={subjectOpts} />
          <Select value={module_} onChange={setModule} options={MODULE_OPTS} />
          <Select value={type} onChange={setType} options={TYPE_OPTS} />
          <Select value={year} onChange={setYear} options={YEAR_OPTS} />
        </div>
      </Card>

      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <div key={i} className="skeleton h-32 rounded-2xl" />)}
        </div>
      )}

      {!loading && questions?.length === 0 && (
        <div className="text-center py-16 text-slate-600">
          <BookOpen size={48} className="mx-auto mb-3 opacity-30" />
          <p className="font-medium">No questions found</p>
          <p className="text-sm mt-1">Upload papers and tag questions to see them here</p>
        </div>
      )}

      {Object.entries(grouped).sort().map(([mod, types]) => (
        <div key={mod} className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-display font-bold text-white text-lg flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary-400" />{mod}
            </h2>
            {subjectId && (
              <a href={`/api/v1/download/module?subject_id=${subjectId}&module=${mod.replace('Module ', '')}`} download className="text-xs text-primary-400 bg-primary-500/10 hover:bg-primary-500/20 px-3 py-1.5 rounded-lg transition-colors">
                Download {mod}
              </a>
            )}
          </div>
          {Object.entries(types).map(([typ, qs]) => (
            <Card key={typ}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-slate-300 text-sm">{typ}</h3>
                <Badge color={typ.includes('Short') ? 'teal' : 'gold'}>{qs.length} questions</Badge>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                {qs.map(q => (
                  <div key={q.id} className="group relative rounded-xl overflow-hidden border border-white/10 bg-surface-2 hover:border-primary-500/40 transition-all">
                    <img src={`/static/${q.image_path}`} alt="Question"
                      className="w-full h-28 object-cover" />
                    <div className="p-2">
                      <div className="text-xs text-slate-400">
                        {q.question_number && <span className="font-mono">Q{q.question_number} · </span>}
                        <span className="text-slate-500">Pg {q.page_number}</span>
                      </div>
                      {q.tags?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {q.tags.slice(0, 2).map(t => (
                            <span key={t} className="text-xs bg-primary-500/10 text-primary-400 px-1.5 py-0.5 rounded">{t}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <button onClick={() => handleDelete(q.id)}
                      className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 p-1 bg-black/70 rounded-lg text-accent-rose hover:bg-accent-rose/20 transition-all">
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      ))}
    </div>
  )
}
