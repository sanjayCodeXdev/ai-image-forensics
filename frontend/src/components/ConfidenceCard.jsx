import { TrendingUp } from 'lucide-react'
import clsx from 'clsx'

function ConfidenceBar({ value, result }) {
  const color =
    result === 'likely_ai_generated' ? 'bg-red-500' :
    result === 'likely_real'         ? 'bg-green-500' :
                                       'bg-amber-500'
  return (
    <div className="w-full bg-surface rounded-full h-3 overflow-hidden">
      <div
        className={clsx('h-full rounded-full transition-all duration-1000', color)}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  )
}

export default function ConfidenceCard({ aiProbability, realProbability, confidenceScore, result }) {
  const aiPct   = aiProbability   != null ? Math.round(aiProbability   * 100) : null
  const realPct = realProbability != null ? Math.round(realProbability * 100) : null
  const confPct = confidenceScore != null ? Math.round(confidenceScore * 100) : null

  return (
    <div className="card space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <TrendingUp className="w-5 h-5 text-primary-400" />
        <h3 className="font-semibold text-slate-200">Confidence Scores</h3>
      </div>

      {/* Overall confidence */}
      {confPct != null && (
        <div className="text-center py-4 bg-surface rounded-xl border border-surface-border">
          <p className="text-5xl font-bold text-gradient">{confPct}%</p>
          <p className="text-sm text-slate-400 mt-1">Overall Confidence</p>
        </div>
      )}

      {/* AI vs Real bars */}
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-red-400 font-medium flex items-center gap-1.5">
              <span className="dot-red" /> AI-Generated Probability
            </span>
            <span className="font-bold text-red-300">{aiPct != null ? `${aiPct}%` : '—'}</span>
          </div>
          {aiProbability != null && (
            <div className="w-full bg-surface rounded-full h-2.5">
              <div
                className="bg-red-500 h-2.5 rounded-full transition-all duration-1000"
                style={{ width: `${aiPct}%` }}
              />
            </div>
          )}
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-green-400 font-medium flex items-center gap-1.5">
              <span className="dot-green" /> Real / Authentic Probability
            </span>
            <span className="font-bold text-green-300">{realPct != null ? `${realPct}%` : '—'}</span>
          </div>
          {realProbability != null && (
            <div className="w-full bg-surface rounded-full h-2.5">
              <div
                className="bg-green-500 h-2.5 rounded-full transition-all duration-1000"
                style={{ width: `${realPct}%` }}
              />
            </div>
          )}
        </div>
      </div>

      <p className="text-xs text-slate-600 border-t border-surface-border pt-3">
        ℹ Scores are estimates. No system achieves 100% accuracy in detecting AI-generated images.
      </p>
    </div>
  )
}
