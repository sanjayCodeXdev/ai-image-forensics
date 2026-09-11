import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FileText, ArrowLeft, RefreshCw, AlertTriangle,
         Database, Shield, Cpu, ScanSearch, Layers, Tag } from 'lucide-react'
import ResultBadge    from '../components/ResultBadge'
import ConfidenceCard from '../components/ConfidenceCard'
import EvidenceCard   from '../components/EvidenceCard'
import ImagePreview   from '../components/ImagePreview'
import { AiRealPie, EvidenceBar, ForensicRadar } from '../components/Charts'
import { getReport, getImageUrl } from '../services/api'

function InfoRow({ label, value }) {
  if (!value && value !== 0) return null
  return (
    <div className="flex justify-between items-center py-2 border-b border-surface-border last:border-0">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm text-slate-200 font-medium">{String(value)}</span>
    </div>
  )
}

export default function Results() {
  const { analysisId } = useParams()
  const [report, setReport] = useState(null)
  const [error, setError]   = useState('')

  useEffect(() => {
    getReport(analysisId)
      .then(setReport)
      .catch(e => setError(e.message))
  }, [analysisId])

  if (error) return (
    <div className="max-w-lg mx-auto px-4 py-20 text-center">
      <p className="text-red-400 font-semibold mb-2">Failed to load results</p>
      <p className="text-slate-500 text-sm mb-6">{error}</p>
      <Link to="/analyze" className="btn-primary">Try Again</Link>
    </div>
  )

  if (!report) return (
    <div className="max-w-lg mx-auto px-4 py-20 text-center">
      <div className="flex justify-center mb-4">
        <RefreshCw className="w-10 h-10 text-primary-400 animate-spin" />
      </div>
      <p className="text-slate-400">Loading results…</p>
    </div>
  )

  const { file_info, final_verdict, evidence, fusion_details } = report
  const meta     = evidence?.metadata   || {}
  const prov     = evidence?.provenance || {}
  const wm       = evidence?.watermark  || {}
  const visual   = evidence?.visual_ai  || {}
  const forensics= evidence?.forensics  || {}

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-8 animate-fade-in">

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <Link to="/analyze" className="btn-ghost text-sm mb-3 -ml-2">
            <ArrowLeft className="w-4 h-4" /> New Analysis
          </Link>
          <h1 className="text-2xl font-bold text-slate-100">Analysis Results</h1>
          <p className="text-sm text-slate-500 mt-1 font-mono">{analysisId}</p>
        </div>
        <div className="flex gap-3">
          <Link to={`/report/${analysisId}`} className="btn-secondary text-sm py-2">
            <FileText className="w-4 h-4" /> Full Report
          </Link>
        </div>
      </div>

      {/* ── Summary strip ── */}
      <div className="card bg-gradient-to-r from-surface-card to-primary-950/20 border-primary-800/30">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 items-center">
          <div className="lg:col-span-1">
            <p className="text-xs text-slate-500 mb-2">Final Verdict</p>
            <ResultBadge result={final_verdict?.classification} large />
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">AI Probability</p>
            <p className="text-3xl font-bold text-red-400">
              {final_verdict?.ai_probability != null
                ? `${(final_verdict.ai_probability * 100).toFixed(1)}%`
                : '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Real Probability</p>
            <p className="text-3xl font-bold text-green-400">
              {final_verdict?.real_probability != null
                ? `${(final_verdict.real_probability * 100).toFixed(1)}%`
                : '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">File</p>
            <p className="text-sm text-slate-200 font-medium truncate">{file_info?.original_filename}</p>
            <p className="text-xs text-slate-500 mt-0.5">
              {file_info?.image_width}×{file_info?.image_height} · {file_info?.file_type}
            </p>
          </div>
        </div>
        <p className="text-xs text-amber-300/70 mt-4 flex items-start gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
          {final_verdict?.disclaimer}
        </p>
      </div>

      {/* ── 2-col layout ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left col */}
        <div className="space-y-5">
          <ImagePreview src={getImageUrl(analysisId)} alt={file_info?.original_filename} />

          <ConfidenceCard
            aiProbability   ={final_verdict?.ai_probability}
            realProbability ={final_verdict?.real_probability}
            confidenceScore ={final_verdict?.confidence_score}
            result          ={final_verdict?.classification}
          />

          {/* File info */}
          <div className="card">
            <h3 className="font-semibold text-slate-200 text-sm mb-3">File Information</h3>
            <InfoRow label="Filename"    value={file_info?.original_filename} />
            <InfoRow label="Format"      value={file_info?.file_type} />
            <InfoRow label="MIME Type"   value={file_info?.mime_type} />
            <InfoRow label="Dimensions"  value={file_info?.image_width && `${file_info.image_width} × ${file_info.image_height} px`} />
            <InfoRow label="Analysis ID" value={analysisId} />
          </div>
        </div>

        {/* Right col — evidence cards */}
        <div className="lg:col-span-2 space-y-4">
          <EvidenceCard
            title="Metadata Analysis" icon={Tag}
            status={meta.status}
            score={meta.score}
            summary={meta.summary}
            limitations={meta.limitations}
            details={{ findings: meta.findings, exif_keys: Object.keys(meta.exif || {}) }}
          />
          <EvidenceCard
            title="C2PA / Content Credentials" icon={Shield}
            status={prov.status}
            summary={prov.summary}
            limitations={prov.limitations}
            details={prov.details}
          />
          <EvidenceCard
            title="AI Watermark / Provider Signals" icon={Database}
            status={wm.overall_status}
            summary={wm.summary}
            limitations={wm.limitations}
            details={wm.providers_checked}
          />
          <EvidenceCard
            title="AI Visual Detection Model" icon={Cpu}
            status={visual.status}
            score={visual.ai_probability}
            summary={visual.status === 'model_not_configured'
              ? 'AI model is not configured. See instructions below.'
              : `Prediction: ${(visual.prediction || '—').replace(/_/g,' ')} — AI ${(visual.ai_probability||0)*100}% / Real ${(visual.real_probability||0)*100}%`}
            limitations={visual.limitations || visual.instructions}
            details={{ model: visual.model_name, version: visual.model_version, device: visual.device_used }}
            badge={visual.model_name}
          />
          <EvidenceCard
            title="Digital Forensics" icon={ScanSearch}
            status={forensics.status}
            score={forensics.anomaly_score}
            summary={forensics.summary}
            limitations={forensics.limitations}
            details={forensics.details}
          />
          <EvidenceCard
            title="Evidence Fusion" icon={Layers}
            status={final_verdict?.classification}
            score={final_verdict?.ai_probability}
            summary={final_verdict?.summary}
            limitations="Evidence fusion combines all signals with transparent weights. The result is an estimate, not proof."
            details={{
              contributions: fusion_details?.contributions,
              weights: fusion_details?.weights_used,
              thresholds: fusion_details?.thresholds,
            }}
          />
        </div>
      </div>

      {/* ── Charts ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <AiRealPie
          aiProbability  ={final_verdict?.ai_probability}
          realProbability={final_verdict?.real_probability}
        />
        <EvidenceBar contributions={fusion_details?.contributions} />
        <ForensicRadar chartData={forensics.chart_data} />
      </div>

      {/* ── Positive / Negative indicators ── */}
      {(fusion_details?.positive_indicators?.length > 0 || fusion_details?.negative_indicators?.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="card border-green-800/30">
            <h3 className="font-semibold text-green-400 text-sm mb-3 flex items-center gap-2">
              <span className="dot-green" /> Indicators Suggesting Real
            </h3>
            <ul className="space-y-1">
              {fusion_details.positive_indicators.map((p, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-green-400 mt-1 flex-shrink-0">✓</span>{p}
                </li>
              ))}
            </ul>
          </div>
          <div className="card border-red-800/30">
            <h3 className="font-semibold text-red-400 text-sm mb-3 flex items-center gap-2">
              <span className="dot-red" /> Indicators Suggesting AI-Generated
            </h3>
            <ul className="space-y-1">
              {fusion_details.negative_indicators.map((p, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-red-400 mt-1 flex-shrink-0">✕</span>{p}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

    </div>
  )
}
