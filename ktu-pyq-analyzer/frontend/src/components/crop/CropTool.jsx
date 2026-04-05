import React, { useRef, useState, useCallback, useEffect } from 'react'
import { Crop, RotateCcw } from 'lucide-react'
import Button from '../ui/Button'

export default function CropTool({ imageUrl, onCrop, pageNumber }) {
  const canvasRef = useRef(null)
  const imgRef = useRef(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPos, setStartPos] = useState(null)
  const [rect, setRect] = useState(null)
  const [imgLoaded, setImgLoaded] = useState(false)

  const getPos = (e, canvas) => {
    const r = canvas.getBoundingClientRect()
    const scaleX = canvas.width / r.width
    const scaleY = canvas.height / r.height
    const clientX = e.touches ? e.touches[0].clientX : e.clientX
    const clientY = e.touches ? e.touches[0].clientY : e.clientY
    return {
      x: (clientX - r.left) * scaleX,
      y: (clientY - r.top) * scaleY,
    }
  }

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current
    const img = imgRef.current
    if (!canvas || !img || !imgLoaded) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    if (rect) {
      ctx.fillStyle = 'rgba(0,0,0,0.45)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, rect.x, rect.y, rect.w, rect.h, rect.x, rect.y, rect.w, rect.h)
      ctx.strokeStyle = '#4c6ef5'
      ctx.lineWidth = 2
      ctx.strokeRect(rect.x, rect.y, rect.w, rect.h)
      // Corner handles
      const handles = [
        [rect.x, rect.y], [rect.x + rect.w, rect.y],
        [rect.x, rect.y + rect.h], [rect.x + rect.w, rect.y + rect.h],
      ]
      ctx.fillStyle = '#4c6ef5'
      handles.forEach(([hx, hy]) => {
        ctx.beginPath(); ctx.arc(hx, hy, 5, 0, Math.PI * 2); ctx.fill()
      })
    }
  }, [rect, imgLoaded])

  useEffect(() => { drawCanvas() }, [drawCanvas])

  const onMouseDown = (e) => {
    e.preventDefault()
    const pos = getPos(e, canvasRef.current)
    setIsDrawing(true)
    setStartPos(pos)
    setRect(null)
  }

  const onMouseMove = (e) => {
    if (!isDrawing) return
    e.preventDefault()
    const pos = getPos(e, canvasRef.current)
    const x = Math.min(startPos.x, pos.x)
    const y = Math.min(startPos.y, pos.y)
    const w = Math.abs(pos.x - startPos.x)
    const h = Math.abs(pos.y - startPos.y)
    setRect({ x, y, w, h })
  }

  const onMouseUp = () => { setIsDrawing(false) }

  const handleCrop = () => {
    if (!rect || rect.w < 10 || rect.h < 10) return
    const canvas = canvasRef.current
    const img = imgRef.current
    const scaleX = img.naturalWidth / canvas.width
    const scaleY = img.naturalHeight / canvas.height

    const offscreen = document.createElement('canvas')
    offscreen.width = rect.w * scaleX
    offscreen.height = rect.h * scaleY
    const ctx = offscreen.getContext('2d')
    ctx.drawImage(img,
      rect.x * scaleX, rect.y * scaleY, rect.w * scaleX, rect.h * scaleY,
      0, 0, offscreen.width, offscreen.height,
    )
    const b64 = offscreen.toDataURL('image/png').split(',')[1]
    onCrop(b64, {
      x: Math.round(rect.x * scaleX),
      y: Math.round(rect.y * scaleY),
      w: Math.round(rect.w * scaleX),
      h: Math.round(rect.h * scaleY),
    }, pageNumber)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400 flex items-center gap-2">
          <Crop size={14} className="text-primary-400" />
          Draw a rectangle to select a question
        </p>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => setRect(null)}>
            <RotateCcw size={13} /> Reset
          </Button>
          <Button size="sm" onClick={handleCrop} disabled={!rect || rect.w < 10}>
            <Crop size={13} /> Crop & Tag
          </Button>
        </div>
      </div>

      <div className="rounded-xl overflow-hidden border border-white/10 relative">
        <img
          ref={imgRef}
          src={imageUrl}
          alt=""
          crossOrigin="anonymous"
          style={{ display: 'none' }}
          onLoad={() => {
            const img = imgRef.current
            const canvas = canvasRef.current
            canvas.width = img.naturalWidth
            canvas.height = img.naturalHeight
            setImgLoaded(true)
          }}
        />
        <canvas
          ref={canvasRef}
          className="w-full cursor-crosshair select-none"
          style={{ touchAction: 'none' }}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
          onTouchStart={onMouseDown}
          onTouchMove={onMouseMove}
          onTouchEnd={onMouseUp}
        />
        {!imgLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface-2">
            <div className="text-slate-500 text-sm">Loading image…</div>
          </div>
        )}
      </div>

      {rect && rect.w > 10 && (
        <p className="text-xs text-slate-500 text-right">
          Selection: {Math.round(rect.w)} × {Math.round(rect.h)} px
        </p>
      )}
    </div>
  )
}
