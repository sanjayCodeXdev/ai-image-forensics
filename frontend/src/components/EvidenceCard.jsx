import { useState } from 'react'
import { ChevronDown, ChevronUp, AlertTriangle, CheckCircle, HelpCircle, XCircle, Info } from 'lucide-react'
import clsx from 'clsx'

function StatusIcon({ status }) {
  const s = (status || '').toLowerCase()
  if (s.includes('found') || s.includes('success') || s.includes('completed'))
    return <CheckCircle className="w-4 h-4 text-green-400" />
  if (s.includes('ai') || s.includes('missing') || s.includes('error') || s.includes('anomal'))
    return <XCircle className="w-4 h-4 text-red-400" />
  if (s.includes('inconclusive') || s.includes('unavailable') || s.includes('not_configured'))
    return <HelpCircle className="w-4 h-4 text-amber-400" />
  return <Info className="w-4 h-4 text-slate-400" />
}

function scoreColor(score) {
  if (score == null) return 'text-slate-500'
  if (score > 0.65)  return 'text-red-400'
  if (score < 0.35)  return 'text-green-400'
  return 'text-amber-400'
}

export default function EvidenceCard({
  title,
  icon: Icon,
  status,
  score,
  summary,
  limitations,
  details,
  badge,
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="card hover:border-slate-600 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 bg-primary-600/15 rounded-lg flex items-center justify-center flex-shrink-0">
            <Icon className="w-4.5 h-4.5 text-primary-400" style={{width:'18px',height:'18px'}} />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-slate-200 text-sm">{title}</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <StatusIcon status={status} />
              <span className="text-xs text-slate-400 truncate">
                {(status || 'unknown').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          {score != null && (
            <div className="text-right">
              <p className={clsx('text-lg font-bold tabular-nums', scoreColor(score))}>
                {(score * 100).toFixed(0)}
              </p>
              <p className="text-xs text-slate-600">score</p>
            </div>
          )}
          {badge && <span className="badge-neutral text-xs">{badge}</span>}
          <button
            onClick={() => setExpanded(!expanded)}
            className="btn-ghost p-1.5"
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-sm text-slate-400 mt-3 leading-relaxed">{summary}</p>
      )}

      {/* Expanded details */}
      {expanded && (
        <div className="mt-4 space-y-3 animate-fade-in">
          {limitations && (
            <div className="flex items-start gap-2 p-3 bg-amber-900/10 border border-amber-800/30 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-amber-300/80 leading-relaxed">{limitations}</p>
            </div>
          )}
          {details && (
            <div className="bg-surface rounded-lg p-3 overflow-auto max-h-64">
              <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap break-words">
                {typeof details === 'string' ? details : JSON.stringify(details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
