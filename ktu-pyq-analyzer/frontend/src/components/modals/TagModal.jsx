import React, { useState } from 'react'
import Modal from '../ui/Modal'
import Select from '../ui/Select'
import Input from '../ui/Input'
import Button from '../ui/Button'
import { saveQuestion } from '../../services/api'
import toast from 'react-hot-toast'

const MODULE_OPTS = [1,2,3,4,5].map(n => ({ value: n, label: `Module ${n}` }))
const TYPE_OPTS = [
  { value: 'short', label: 'Short Answer' },
  { value: 'long', label: 'Long Answer' },
]

export default function TagModal({ open, onClose, onSaved, croppedB64, cropCoords, paperId, pageNumber }) {
  const [module_, setModule] = useState(1)
  const [type, setType] = useState('short')
  const [qNum, setQNum] = useState('')
  const [tags, setTags] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    if (!croppedB64) return
    setSaving(true)
    try {
      await saveQuestion({
        metadata: {
          paper_id: paperId,
          module: Number(module_),
          type,
          question_number: qNum || null,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean),
          page_number: pageNumber,
          crop_coords: cropCoords,
          notes: notes || null,
        },
        image_b64: croppedB64,
      })
      toast.success('Question saved!')
      onSaved?.()
      onClose()
    } catch (e) {
      toast.error(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Tag Question" size="md">
      <div className="space-y-4">
        {croppedB64 && (
          <div className="rounded-xl overflow-hidden border border-white/10 bg-surface-2">
            <img src={`data:image/png;base64,${croppedB64}`} alt="Crop preview"
              className="w-full max-h-52 object-contain" />
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <Select label="Module" value={module_} onChange={setModule} options={MODULE_OPTS} />
          <Select label="Question Type" value={type} onChange={setType} options={TYPE_OPTS} />
        </div>

        <Input label="Question Number (optional)" value={qNum}
          onChange={e => setQNum(e.target.value)} placeholder="e.g. 3a, 7b" />

        <Input label="Tags (comma-separated)" value={tags}
          onChange={e => setTags(e.target.value)} placeholder="e.g. recursion, sorting" />

        <div>
          <label className="block text-sm text-slate-400 mb-1.5 font-medium">Notes</label>
          <textarea
            value={notes} onChange={e => setNotes(e.target.value)}
            placeholder="Optional notes…"
            rows={2}
            className="w-full bg-surface-3 border border-white/10 rounded-xl px-3 py-2.5 text-slate-200
              focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30
              transition-colors text-sm resize-none"
          />
        </div>

        <div className="flex gap-3 pt-1">
          <Button variant="secondary" className="flex-1" onClick={onClose}>Cancel</Button>
          <Button className="flex-1" loading={saving} onClick={handleSave}>Save Question</Button>
        </div>
      </div>
    </Modal>
  )
}
