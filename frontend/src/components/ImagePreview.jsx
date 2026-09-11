import { useState } from 'react'
import { ZoomIn, Image as ImageIcon } from 'lucide-react'

export default function ImagePreview({ file, src, alt = 'Uploaded image' }) {
  const [zoomed, setZoomed] = useState(false)
  const imgSrc = src || (file ? URL.createObjectURL(file) : null)
  if (!imgSrc) return null

  return (
    <>
      <div className="card overflow-hidden p-0">
        <div className="relative group cursor-zoom-in" onClick={() => setZoomed(true)}>
          <img
            src={imgSrc}
            alt={alt}
            className="w-full max-h-80 object-contain bg-black/20"
            onError={e => { e.target.src = ''; e.target.alt = 'Preview unavailable' }}
          />
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
            <div className="bg-white/10 backdrop-blur-sm rounded-full p-3">
              <ZoomIn className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
        {(file?.name || alt) && (
          <div className="px-4 py-2 flex items-center gap-2 border-t border-surface-border">
            <ImageIcon className="w-4 h-4 text-slate-500 flex-shrink-0" />
            <span className="text-xs text-slate-400 truncate">{file?.name || alt}</span>
          </div>
        )}
      </div>

      {/* Lightbox */}
      {zoomed && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4 animate-fade-in cursor-zoom-out"
          onClick={() => setZoomed(false)}
        >
          <img
            src={imgSrc}
            alt={alt}
            className="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
          />
        </div>
      )}
    </>
  )
}
