import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, RefreshCw, Download } from 'lucide-react'
import ResultBadge   from '../components/ResultBadge'
import MetadataTable from '../components/MetadataTable'
import { getReport }  from '../services/api'

function Section({ title, children }) {
  return (
    <section>
      <h2 className="text-lg font-bold text-slate-100 mb-4 pb-2 border-b border-surface-border">{title}</h2>
      {children}
    </section>
  )
}

function LimitationList({ items }) {
  if (!items?.length) return null
  return (
    <ul className="space-y-2 mt-3">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-sm text-amber-300/80">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-400" />
          {item}
        </li>
      ))}
    </ul>
  )
}

export default function Report() {
  const { analysisId } = useParams()
  const [report, setReport] = useState(null)
  const [error,  setError]  = useState('')

  useEffect(() => {
    getReport(analysisId).then(setReport).catch(e => setError(e.message))
  }, [analysisId])

  const handleDownload = () => {
    const json = JSON.stringify(report, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href = url
    a.download = `report_${analysisId}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (error) return (
    <div className="max-w-lg mx-auto py-20 text-center px-4">
      <p className="text-red-400 mb-2 font-semibold">Failed to load report</p>
      <p className="text-slate-500 text-sm">{error}</p>
      <Link to="/history" className="btn-secondary mt-6 inline-flex">Back to History</Link>
    </div>
  )

  if (!report) return (
    <div className="max-w-lg mx-auto py-20 text-center px-4">
      <RefreshCw className="w-8 h-8 text-primary-400 animate-spin mx-auto mb-4" />
      <p className="text-slate-400">Loading report…</p>
    </div>
  )

  const { file_info, final_verdict, evidence, fusion_details, limitations } = report
  const meta      = evidence?.metadata   || {}
  const prov      = evidence?.provenance || {}
  const wm        = evidence?.watermark  || {}
  const visual    = evidence?.visual_ai  || {}
  const forensics = evidence?.forensics  || {}

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-10 animate-fade-in">

      {/* Top bar */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <Link to={`/results/${analysisId}`} className="btn-ghost text-sm">
          <ArrowLeft className="w-4 h-4" /> Back to Results
        </Link>
        <button onClick={handleDownload} className="btn-secondary text-sm py-2">
          <Download className="w-4 h-4" /> Download JSON
        </button>
      </div>

      {/* Report header */}
      <div className="card text-center">
        <p className="section-label mb-2">Detailed Analysis Report</p>
        <h1 className="text-2xl font-bold text-slate-100 mb-3">{file_info?.original_filename}</h1>
        <ResultBadge result={final_verdict?.classification} large />
        <p className="text-slate-500 text-xs mt-3 font-mono">{analysisId}</p>
        <p className="text-slate-600 text-xs mt-1">Generated: {report.generated_at}</p>
      </div>

      {/* File info */}
      <Section title="File Information">
        <MetadataTable data={file_info} title="File Details" />
      </Section>

      {/* Metadata */}
      <Section title="Metadata Analysis">
        <div className="card mb-4">
          <p className="text-sm text-slate-300 mb-2">{meta.summary}</p>
          <div className="p-3 bg-amber-900/10 border border-amber-800/30 rounded-lg mt-3">
            <p className="text-xs text-amber-300/80">{meta.limitations}</p>
          </div>
        </div>
        {meta.exif && Object.keys(meta.exif).length > 0 && (
          <MetadataTable data={meta.exif} title="EXIF Data" />
        )}
        {meta.xmp && Object.keys(meta.xmp).length > 0 && (
          <MetadataTable data={meta.xmp} title="XMP Metadata" />
        )}
      </Section>

      {/* Provenance */}
      <Section title="C2PA / Content Credentials">
        <div className="card">
          <p className="text-sm text-slate-300 mb-2">{prov.summary}</p>
          <p className="badge-neutral text-xs inline-flex mt-2">
            Status: {(prov.status || '—').replace(/_/g, ' ')}
          </p>
          <p className="text-xs text-amber-300/80 mt-3">{prov.limitations}</p>
        </div>
      </Section>

      {/* Watermark */}
      <Section title="AI Watermark / Provider Signals">
        <div className="card">
          <p className="text-sm text-slate-300 mb-3">{wm.summary}</p>
          {wm.providers_checked?.map((p, i) => (
            <div key={i} className="card-sm mb-2">
              <div className="flex justify-between">
                <span className="font-semibold text-sm text-slate-200">{p.provider}</span>
                <span className="badge-neutral text-xs">{(p.status||'').replace(/_/g,' ')}</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{p.note}</p>
            </div>
          ))}
          <p className="text-xs text-amber-300/80 mt-3">{wm.limitations}</p>
        </div>
      </Section>

      {/* AI Model */}
      <Section title="AI Visual Detection Model">
        <div className="card">
          {visual.status === 'model_not_configured' ? (
            <div>
              <p className="text-amber-300 font-semibold text-sm mb-2">Model Not Configured</p>
              <pre className="text-xs text-slate-400 font-mono whitespace-pre-wrap bg-surface p-3 rounded-lg">
                {visual.instructions}
              </pre>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Prediction</span>
                <span className="font-semibold text-slate-200 text-sm capitalize">
                  {(visual.prediction||'—').replace(/_/g,' ')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">AI Probability</span>
                <span className="font-bold text-red-400">
                  {visual.ai_probability != null ? `${(visual.ai_probability*100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Real Probability</span>
                <span className="font-bold text-green-400">
                  {visual.real_probability != null ? `${(visual.real_probability*100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Model</span>
                <span className="text-slate-200 text-sm">{visual.model_name} v{visual.model_version}</span>
              </div>
            </div>
          )}
          <p className="text-xs text-amber-300/80 mt-3">{visual.limitations}</p>
        </div>
      </Section>

      {/* Forensics */}
      <Section title="Digital Forensics">
        <div className="card mb-4">
          <p className="text-sm text-slate-300 mb-2">{forensics.summary}</p>
          <p className="text-xs text-amber-300/80">{forensics.limitations}</p>
        </div>
        {forensics.details && <MetadataTable data={
          Object.fromEntries(
            Object.entries(forensics.details).map(([k, v]) => [
              k, typeof v === 'object' ? `score: ${v?.score ?? '—'} — ${v?.interpretation || ''}` : v
            ])
          )
        } title="Forensic Feature Scores" />}
      </Section>

      {/* Fusion */}
      <Section title="Evidence Fusion & Final Verdict">
        <div className="card">
          <ResultBadge result={final_verdict?.classification} large />
          <p className="text-sm text-slate-300 mt-4 mb-4">{final_verdict?.summary}</p>
          {fusion_details?.contributions && (
            <MetadataTable
              data={Object.fromEntries(
                Object.entries(fusion_details.contributions).map(([k, v]) => [
                  k.replace(/_/g,' '), v != null ? `${(v*100).toFixed(1)}% AI direction` : 'Unavailable'
                ])
              )}
              title="Signal Contributions"
            />
          )}
        </div>
      </Section>

      {/* Limitations */}
      <Section title="System Limitations">
        <div className="card bg-amber-900/10 border-amber-800/30">
          <LimitationList items={limitations} />
        </div>
      </Section>

      {/* Final conclusion */}
      <div className="card border-primary-800/30 bg-primary-950/20 text-center">
        <p className="text-slate-300 text-sm italic leading-relaxed">
          "{final_verdict?.disclaimer}"
        </p>
      </div>

    </div>
  )
}
