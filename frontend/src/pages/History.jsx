import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { History as HistIcon, FileText, Trash2, RefreshCw, InboxIcon } from 'lucide-react'
import ResultBadge from '../components/ResultBadge'
import { getHistory, deleteAnalysis } from '../services/api'

function formatDate(iso) {
  try { return new Date(iso).toLocaleString() } catch { return iso }
}
function formatBytes(b) {
  if (!b) return '—'
  if (b < 1024) return `${b} B`
  if (b < 1024**2) return `${(b/1024).toFixed(1)} KB`
  return `${(b/1024**2).toFixed(2)} MB`
}

export default function History() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting,setDeleting]= useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await getHistory()
      setData(res)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete analysis for "${name}"?`)) return
    setDeleting(id)
    try {
      await deleteAnalysis(id)
      toast.success('Analysis deleted.')
      setData(prev => prev ? { ...prev, items: prev.items.filter(i => i.analysis_id !== id), total: prev.total - 1 } : prev)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <HistIcon className="w-6 h-6 text-primary-400" /> Analysis History
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            {data ? `${data.total} analysis${data.total !== 1 ? 'es' : ''} found` : ''}
          </p>
        </div>
        <button onClick={load} className="btn-ghost text-sm" disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {loading && (
        <div className="text-center py-20">
          <RefreshCw className="w-8 h-8 text-primary-400 animate-spin mx-auto" />
        </div>
      )}

      {!loading && (!data?.items?.length) && (
        <div className="text-center py-20 space-y-4">
          <InboxIcon className="w-14 h-14 text-slate-700 mx-auto" />
          <p className="text-slate-400 font-semibold">No analyses yet</p>
          <p className="text-slate-600 text-sm">Upload and analyse an image to see results here.</p>
          <Link to="/analyze" className="btn-primary inline-flex mt-4">Start Analysis</Link>
        </div>
      )}

      {!loading && data?.items?.length > 0 && (
        <div className="space-y-3">
          {data.items.map(item => (
            <div key={item.analysis_id}
                 className="card hover:border-slate-600 transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <ResultBadge result={item.final_result} />
                  <span className="text-sm font-medium text-slate-200 truncate max-w-xs">
                    {item.original_filename}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-2 text-xs text-slate-500 flex-wrap">
                  <span>{formatDate(item.created_at)}</span>
                  <span>·</span>
                  <span>{item.file_type}</span>
                  <span>·</span>
                  <span>{formatBytes(item.file_size)}</span>
                  {item.confidence_score != null && (
                    <>
                      <span>·</span>
                      <span>Confidence: {Math.round(item.confidence_score * 100)}%</span>
                    </>
                  )}
                </div>
                <p className="text-xs text-slate-600 font-mono mt-1">{item.analysis_id}</p>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <Link to={`/results/${item.analysis_id}`} className="btn-ghost text-sm py-1.5 px-3">
                  <FileText className="w-4 h-4" /> View
                </Link>
                <button
                  onClick={() => handleDelete(item.analysis_id, item.original_filename)}
                  disabled={deleting === item.analysis_id}
                  className="btn-danger py-1.5 px-3"
                >
                  <Trash2 className="w-4 h-4" />
                  {deleting === item.analysis_id ? 'Deleting…' : 'Delete'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
