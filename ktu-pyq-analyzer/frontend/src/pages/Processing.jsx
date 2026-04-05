import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ServerCog, CheckCircle, XCircle } from 'lucide-react'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import { processPaper } from '../services/api'
import toast from 'react-hot-toast'

export default function Processing() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('processing') // processing, success, error
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    let mounted = true
    const triggerProcess = async () => {
      try {
        await processPaper(id)
        if (mounted) {
          setStatus('success')
          toast.success('Paper processed successfully!')
          setTimeout(() => {
            navigate(`/review/${id}`)
          }, 1500)
        }
      } catch (err) {
        if (mounted) {
          setStatus('error')
          setErrorMsg(err.message || 'An error occurred during processing.')
        }
      }
    }
    triggerProcess()
    return () => { mounted = false }
  }, [id, navigate])

  return (
    <div className="max-w-xl mx-auto mt-20 text-center fade-up">
      <Card className="py-12 flex flex-col items-center">
        {status === 'processing' && (
          <>
            <ServerCog size={48} className="text-primary-500 animate-pulse mb-6" />
            <h2 className="text-2xl font-display font-bold text-white mb-2">Analyzing Question Paper</h2>
            <p className="text-slate-400">Extracting questions via OCR. This might take a minute...</p>
            <div className="w-64 h-2 bg-surface-3 rounded-full overflow-hidden mt-6">
              <div className="h-full bg-primary-500 rounded-full w-full animate-[pulse_2s_ease-in-out_infinite]" />
            </div>
          </>
        )}
        
        {status === 'success' && (
          <>
            <CheckCircle size={48} className="text-accent-teal mb-6" />
            <h2 className="text-2xl font-display font-bold text-white mb-2">Processing Complete</h2>
            <p className="text-slate-400">Taking you to the review interface...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle size={48} className="text-red-500 mb-6" />
            <h2 className="text-2xl font-display font-bold text-white mb-2">Processing Failed</h2>
            <p className="text-slate-400 mb-6">{errorMsg}</p>
            <Button onClick={() => navigate('/upload')}>Try Another Upload</Button>
          </>
        )}
      </Card>
    </div>
  )
}
