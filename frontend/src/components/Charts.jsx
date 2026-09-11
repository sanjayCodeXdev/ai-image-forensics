import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'

const DARK_TOOLTIP = {
  contentStyle: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '10px',
    color: '#e2e8f0',
    fontSize: '12px',
  },
}

// ── AI vs Real Pie ─────────────────────────────────────────────────────────────
export function AiRealPie({ aiProbability, realProbability }) {
  if (aiProbability == null && realProbability == null) return null
  const data = [
    { name: 'AI-Generated', value: Math.round((aiProbability || 0) * 100) },
    { name: 'Real / Authentic', value: Math.round((realProbability || 0) * 100) },
  ]
  const COLORS = ['#ef4444', '#22c55e']

  return (
    <div className="card">
      <h3 className="font-semibold text-slate-200 text-sm mb-4">AI vs Real Probability</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={85}
               paddingAngle={4} dataKey="value">
            {data.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
          </Pie>
          <Tooltip {...DARK_TOOLTIP} formatter={v => `${v}%`} />
          <Legend iconType="circle" iconSize={10}
                  wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── Evidence Contribution Bar ──────────────────────────────────────────────────
export function EvidenceBar({ contributions }) {
  if (!contributions) return null
  const data = Object.entries(contributions)
    .filter(([, v]) => v != null)
    .map(([key, val]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      'AI Score': Math.round(val * 100),
    }))

  return (
    <div className="card">
      <h3 className="font-semibold text-slate-200 text-sm mb-4">Evidence Contributions (AI direction)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`}
                 tick={{ fill: '#64748b', fontSize: 11 }} />
          <YAxis type="category" dataKey="name" width={120}
                 tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Tooltip {...DARK_TOOLTIP} formatter={v => `${v}%`} />
          <Bar dataKey="AI Score" fill="#6366f1" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-600 mt-2">Higher = more AI-generation evidence from this signal.</p>
    </div>
  )
}

// ── Forensic Radar ─────────────────────────────────────────────────────────────
export function ForensicRadar({ chartData }) {
  if (!chartData || chartData.length === 0) return null
  const data = chartData.map(d => ({ ...d, score: Math.round(d.score * 100) }))

  return (
    <div className="card">
      <h3 className="font-semibold text-slate-200 text-sm mb-4">Forensic Feature Scores</h3>
      <ResponsiveContainer width="100%" height={260}>
        <RadarChart data={data}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} />
          <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 9 }} />
          <Radar dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} />
          <Tooltip {...DARK_TOOLTIP} formatter={v => `${v}/100`} />
        </RadarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-600 mt-2">Higher score = more anomaly detected in that dimension.</p>
    </div>
  )
}
