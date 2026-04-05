import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, ArrowLeft, Tag } from 'lucide-react'
import CropTool from '../components/crop/CropTool'
import TagModal from '../components/modals/TagModal'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { getPaper } from '../services/api'
import toast from 'react-hot-toast'

export default function Viewer() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [cropData, setCropData] = useState(null)
  const [tagOpen, setTagOpen] = useState(false)

  useEffect(() => {
    getPaper(id).then(setPaper).catch(e => toast.error(e.message))
  }, [id])

  const getPageUrl = (page) => {
    if (!paper) return ''
    if (paper.file_type === 'image') return `/static/${paper.file_path}`
    // For PDF: backend serves a rendered page image
    return `/api/v1/papers/${id}/page/${page}`
  }

  const handleCrop = (b64, coords, page) => {
    setCropData({ b64, coords, page })
    setTagOpen(true)
  }

  if (!paper) return (
    <div className="flex items-center justify-center h-64">
      <div className="skeleton w-64 h-8" />
    </div>
  )

  return (
    <div className="space-y-4 fade-up">
      <div className="flex items-center gap-3">
        <Link to="/browse" className="p-2 rounded-xl hover:bg-surface-3 text-slate-400 transition-colors">
          <ArrowLeft size={18} />
        </Link>
        <div className="flex-1">
          <h1 className="font-display font-bold text-white text-xl">{paper.original_filename}</h1>
          <div className="flex items-center gap-2 mt-1">
            <Badge color="blue">{paper.year}</Badge>
            {paper.exam_type && <Badge color="gray">{paper.exam_type}</Badge>}
            <Badge color="teal">{paper.page_count} pages</Badge>
          </div>
        </div>
        <Link to="/browse">
          <Button variant="secondary" size="sm">
            <Tag size={13} /> View Questions
          </Button>
        </Link>
      </div>

      {/* Page navigator */}
      {paper.page_count > 1 && (
        <div className="flex items-center gap-3 justify-center">
          <Button variant="secondary" size="sm"
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}>
            <ChevronLeft size={14} />
          </Button>
          <span className="text-sm text-slate-400 font-mono">
            Page {currentPage} / {paper.page_count}
          </span>
          <Button variant="secondary" size="sm"
            onClick={() => setCurrentPage(p => Math.min(paper.page_count, p + 1))}
            disabled={currentPage === paper.page_count}>
            <ChevronRight size={14} />
          </Button>
        </div>
      )}

      <div className="glass rounded-2xl p-4">
        <CropTool
          imageUrl={getPageUrl(currentPage)}
          onCrop={handleCrop}
          pageNumber={currentPage}
        />
      </div>

      <TagModal
        open={tagOpen}
        onClose={() => setTagOpen(false)}
        croppedB64={cropData?.b64}
        cropCoords={cropData?.coords}
        paperId={Number(id)}
        pageNumber={cropData?.page}
        onSaved={() => setCropData(null)}
      />
    </div>
  )
}
