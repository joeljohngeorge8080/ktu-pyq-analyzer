import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Edit2, Trash2, Check, X } from 'lucide-react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Input from '../components/ui/Input'
import { getPaper, getQuestions, updateQuestion, deleteQuestion } from '../services/api'
import toast from 'react-hot-toast'

function QuestionItem({ q, onUpdate, onDelete }) {
    const [editing, setEditing] = useState(false)
    const [mod, setMod] = useState(q.module)
    const [type, setType] = useState(q.type)
    const [qNum, setQNum] = useState(q.question_number || '')

    const handleSave = async () => {
        try {
            const updated = await updateQuestion(q.id, {
                module: Number(mod),
                type,
                question_number: qNum
            })
            onUpdate(updated)
            setEditing(false)
            toast.success('Updated')
        } catch (e) {
            toast.error('Failed to update')
        }
    }

    const handleDelete = async () => {
        try {
            await deleteQuestion(q.id)
            onDelete(q.id)
            toast.success('Deleted')
        } catch (e) {
            toast.error('Failed to delete')
        }
    }

    return (
        <Card className="flex flex-col md:flex-row gap-4 mb-4">
            <div className="flex-1 bg-surface-3 p-2 rounded-lg flex items-center justify-center min-h-[100px]">
                <img src={`/api/v1/static/${q.image_path}`} alt={`Q${q.question_number}`} className="max-w-full max-h-64 object-contain rounded" />
            </div>

            <div className="w-full md:w-64 flex flex-col justify-between">
                {editing ? (
                    <div className="space-y-3">
                        <Input label="Q Num" value={qNum} onChange={e => setQNum(e.target.value)} size="sm" />
                        <Input type="number" label="Module (1-5)" value={mod} onChange={e => setMod(e.target.value)} min={1} max={5} size="sm" />
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Type</label>
                            <select value={type} onChange={e => setType(e.target.value)}
                                className="w-full bg-surface-4 border border-white/10 rounded-lg px-2 py-1.5 text-slate-200 text-sm">
                                <option value="short">Short</option>
                                <option value="long">Long</option>
                            </select>
                        </div>
                        <div className="flex gap-2">
                            <Button size="sm" onClick={handleSave} className="flex-1"><Check size={14} /> Save</Button>
                            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}><X size={14} /> Cancel</Button>
                        </div>
                    </div>
                ) : (
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-lg font-bold text-white">Q{q.question_number}</span>
                            <Badge color={q.type === 'short' ? 'blue' : 'purple'}>{q.type}</Badge>
                            <Badge color="teal">Module {q.module}</Badge>
                        </div>

                        <div className="flex gap-2 mt-4">
                            <Button size="sm" variant="secondary" onClick={() => setEditing(true)}><Edit2 size={14} /> Edit</Button>
                            <Button size="sm" variant="ghost" className="text-red-400 hover:text-red-300 hover:bg-red-500/10" onClick={handleDelete}>
                                <Trash2 size={14} /> Delete
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    )
}

export default function Review() {
    const { id } = useParams()
    const [paper, setPaper] = useState(null)
    const [questions, setQuestions] = useState([])

    useEffect(() => {
        getPaper(id).then(setPaper).catch(e => toast.error(e.message))
        getQuestions({ paper_id: id }).then(setQuestions).catch(e => toast.error(e.message))
    }, [id])

    if (!paper) return <div className="text-center py-20">Loading...</div>

    return (
        <div className="max-w-4xl mx-auto space-y-6 fade-up">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Link to="/browse" className="p-2 rounded-xl hover:bg-surface-3 text-slate-400">
                        <ArrowLeft size={18} />
                    </Link>
                    <div>
                        <h1 className="font-display font-bold text-white text-xl">Review Extracted Questions</h1>
                        <p className="text-sm text-slate-400">{paper.original_filename} · {questions.length} auto-detected</p>
                    </div>
                </div>
                <Link to="/browse">
                    <Button>Finish Review</Button>
                </Link>
            </div>

            <div className="space-y-4">
                {questions.length === 0 ? (
                    <Card className="text-center py-8">
                        <p className="text-slate-400">No questions found. You can add them manually.</p>
                    </Card>
                ) : (
                    questions.map(q => (
                        <QuestionItem
                            key={q.id}
                            q={q}
                            onUpdate={(updated) => setQuestions(qs => qs.map(x => x.id === q.id ? updated : x))}
                            onDelete={(qid) => setQuestions(qs => qs.filter(x => x.id !== qid))}
                        />
                    ))
                )}
            </div>
        </div>
    )
}
