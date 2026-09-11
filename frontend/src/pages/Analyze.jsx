import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { ScanSearch, FileText, Ruler, Image as ImageIcon } from 'lucide-react'
import UploadBox from '../components/UploadBox'
import ImagePreview from '../components/ImagePreview'
import { analyzeImage } from '../services/api'

function formatBytes(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024)     return `${bytes} B`
  if (bytes < 1024**2)  return `${(bytes/1024).toFixed(1)} KB`
  return `${(bytes/1024**2).toFixed(2)} MB`
}

export default function Analyze() {
  const navigate = useNavigate()
  const [file, setFile]         = useState(null)
  const [loading, setLoading]   = useState(false)
  const [uploadPct, setUploadPct] = useState(0)
  const [apiError, setApiError] = useState('')

  const handleFile = useCallback((f) => {
    setFile(f)
    setApiError('')
  }, [])

  const handleRemove = useCallback(() => {
    setFile(null)
    setApiError('')
    setUploadPct(0)
  }, [])

  const handleAnalyze = async () => {
    if (!file) {
      toast.error('Please select an image first.')
      return
    }
    setLoading(true)
    setApiError('')

    // Show a temporary loading toast
    const toastId = toast.loading('Uploading and analysing image…')

    try {
      const result = await analyzeImage(file, setUploadPct)
      toast.dismiss(toastId)
      toast.success('Analysis complete!')
      navigate(`/results/${result.analysis_id}`)
    } catch (err) {
      toast.dismiss(toastId)
      const msg = err.message || 'Analysis failed. Please try again.'
      setApiError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 animate-slide-up">
      <div className="text-center mb-8">
        <p className="section-label mb-2">Step 1</p>
        <h1 className="text-3xl font-bold text-slate-100">Upload Image for Analysis</h1>
        <p className="text-slate-400 mt-2 text-sm">
          Supported formats: JPG, JPEG, PNG, WEBP, TIFF · Maximum 20 MB
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left — upload */}
        <div className="space-y-4">
          <UploadBox
            onFileSelected={handleFile}
            onRemove={handleRemove}
            selectedFile={file}
            error={apiError}
          />

          {/* File details */}
          {file && (
            <div className="card-sm grid grid-cols-2 gap-3 animate-fade-in">
              {[
                { icon: FileText, label: 'Name',   value: file.name, full: true },
                { icon: FileText, label: 'Size',   value: formatBytes(file.size) },
                { icon: ImageIcon, label: 'Type',  value: file.type.split('/')[1]?.toUpperCase() },
              ].map(({ icon: Icon, label, value, full }) => (
                <div key={label} className={full ? 'col-span-2' : ''}>
                  <p className="text-xs text-slate-500 mb-0.5">{label}</p>
                  <p className="text-sm text-slate-200 font-medium truncate flex items-center gap-1.5">
                    <Icon className="w-3.5 h-3.5 text-primary-400 flex-shrink-0" />
                    {value || '—'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Upload progress */}
          {loading && uploadPct > 0 && uploadPct < 100 && (
            <div className="space-y-1 animate-fade-in">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Uploading…</span>
                <span>{uploadPct}%</span>
              </div>
              <div className="w-full bg-surface-border rounded-full h-1.5">
                <div className="bg-primary-500 h-1.5 rounded-full transition-all duration-300"
                     style={{ width: `${uploadPct}%` }} />
              </div>
            </div>
          )}

          {/* Analyze button */}
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="btn-primary w-full justify-center py-3.5 text-base"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Analysing…
              </>
            ) : (
              <><ScanSearch className="w-5 h-5" /> Analyse Image</>
            )}
          </button>
        </div>

        {/* Right — preview */}
        <div>
          {file ? (
            <ImagePreview file={file} />
          ) : (
            <div className="card h-64 flex flex-col items-center justify-center text-center border-dashed">
              <ImageIcon className="w-12 h-12 text-slate-700 mb-3" />
              <p className="text-slate-600 text-sm">Image preview will appear here</p>
            </div>
          )}
        </div>
      </div>

      {/* Notice */}
      <p className="text-center text-xs text-slate-600 mt-8">
        ⚠ Avoid uploading confidential or sensitive personal images.
        Files are stored temporarily for analysis only.
      </p>
    </div>
  )
}
