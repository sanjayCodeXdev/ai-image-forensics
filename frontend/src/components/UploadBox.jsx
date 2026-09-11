import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, ImageIcon, AlertCircle, X, CheckCircle } from 'lucide-react'
import clsx from 'clsx'

const MAX_MB = 20
const ALLOWED = ['.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff']
const ALLOWED_MIME = ['image/jpeg', 'image/png', 'image/webp', 'image/tiff']

function formatBytes(bytes) {
  if (bytes < 1024)       return `${bytes} B`
  if (bytes < 1024**2)    return `${(bytes/1024).toFixed(1)} KB`
  return `${(bytes/1024**2).toFixed(2)} MB`
}

export default function UploadBox({ onFileSelected, onRemove, selectedFile, error }) {
  const [localError, setLocalError] = useState('')

  const onDrop = useCallback((accepted, rejected) => {
    setLocalError('')

    if (rejected.length > 0) {
      const first = rejected[0]
      const codes  = first.errors.map(e => e.code)
      if (codes.includes('file-too-large'))
        setLocalError(`File exceeds ${MAX_MB} MB limit.`)
      else if (codes.includes('file-invalid-type'))
        setLocalError(`Unsupported file type. Allowed: ${ALLOWED.join(', ')}`)
      else
        setLocalError('File rejected. Please check the format and size.')
      return
    }

    if (accepted.length > 0) {
      const file = accepted[0]
      // Extra MIME check
      if (!ALLOWED_MIME.includes(file.type)) {
        setLocalError('File MIME type is not a supported image format.')
        return
      }
      onFileSelected(file)
    }
  }, [onFileSelected])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'],
              'image/webp': ['.webp'], 'image/tiff': ['.tif', '.tiff'] },
    maxSize: MAX_MB * 1024 * 1024,
    multiple: false,
    disabled: !!selectedFile,
  })

  const displayError = error || localError

  if (selectedFile) {
    return (
      <div className="card animate-fade-in">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle className="w-5 h-5" />
            <span className="font-semibold text-sm">Image Ready</span>
          </div>
          <button onClick={onRemove} className="btn-ghost p-1.5 text-slate-500 hover:text-red-400">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-4 p-4 bg-surface rounded-xl border border-surface-border">
          <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
            <ImageIcon className="w-6 h-6 text-primary-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate">{selectedFile.name}</p>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-slate-500">{formatBytes(selectedFile.size)}</span>
              <span className="text-xs text-slate-600">•</span>
              <span className="text-xs text-slate-500 uppercase">{selectedFile.type.split('/')[1]}</span>
            </div>
          </div>
        </div>

        {displayError && (
          <div className="mt-3 flex items-start gap-2 text-red-400 text-sm p-3 bg-red-900/20 rounded-lg border border-red-800/40">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            {displayError}
          </div>
        )}
      </div>
    )
  }

  return (
    <div>
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200',
          isDragActive && !isDragReject
            ? 'border-primary-500 bg-primary-500/10 scale-[1.01]'
            : isDragReject
            ? 'border-red-500 bg-red-500/10'
            : 'border-surface-border hover:border-primary-600 hover:bg-primary-500/5'
        )}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          <div className={clsx(
            'w-16 h-16 rounded-2xl flex items-center justify-center transition-colors',
            isDragActive ? 'bg-primary-500/20' : 'bg-surface-card'
          )}>
            <Upload className={clsx('w-8 h-8', isDragActive ? 'text-primary-400' : 'text-slate-500')} />
          </div>

          {isDragActive && !isDragReject && (
            <p className="text-primary-300 font-semibold">Drop your image here!</p>
          )}
          {isDragReject && (
            <p className="text-red-400 font-semibold">File type not supported</p>
          )}
          {!isDragActive && (
            <>
              <div>
                <p className="text-slate-300 font-semibold">
                  Drag & drop an image, or{' '}
                  <span className="text-primary-400 underline underline-offset-2">browse</span>
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  Supports: JPG, PNG, WEBP, TIFF · Max {MAX_MB} MB
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {displayError && (
        <div className="mt-3 flex items-start gap-2 text-red-400 text-sm p-3 bg-red-900/20 rounded-lg border border-red-800/40 animate-fade-in">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          {displayError}
        </div>
      )}

      <p className="text-xs text-slate-600 mt-3 text-center">
        ⚠ Avoid uploading confidential or sensitive images. Files are used for analysis only.
      </p>
    </div>
  )
}
