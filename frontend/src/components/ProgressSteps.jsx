import { CheckCircle, Circle, Loader2 } from 'lucide-react'
import clsx from 'clsx'

const STEPS = [
  { id: 'upload',     label: 'Validating image',         desc: 'Checking file integrity and format' },
  { id: 'metadata',   label: 'Extracting metadata',      desc: 'EXIF, XMP, IPTC analysis' },
  { id: 'provenance', label: 'Checking provenance',      desc: 'C2PA / Content Credentials' },
  { id: 'watermark',  label: 'Checking AI signals',      desc: 'Provider watermark detection' },
  { id: 'visual',     label: 'Running AI model',         desc: 'EfficientNet-B0 inference' },
  { id: 'forensics',  label: 'Digital forensic analysis',desc: 'ELA, noise, frequency, texture' },
  { id: 'fusion',     label: 'Generating report',        desc: 'Evidence fusion & classification' },
]

export default function ProgressSteps({ currentStep }) {
  const currentIdx = STEPS.findIndex(s => s.id === currentStep)

  return (
    <div className="space-y-2">
      {STEPS.map((step, idx) => {
        const done    = idx < currentIdx
        const active  = idx === currentIdx
        const pending = idx > currentIdx

        return (
          <div
            key={step.id}
            className={clsx(
              'flex items-center gap-4 p-3.5 rounded-xl transition-all duration-300',
              active  ? 'bg-primary-600/15 border border-primary-600/30' :
              done    ? 'bg-green-900/10 border border-green-800/20' :
                        'bg-surface-card/50 border border-transparent opacity-40'
            )}
          >
            <div className="flex-shrink-0">
              {done    && <CheckCircle className="w-5 h-5 text-green-400" />}
              {active  && <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />}
              {pending && <Circle className="w-5 h-5 text-slate-600" />}
            </div>
            <div>
              <p className={clsx(
                'text-sm font-medium',
                active ? 'text-primary-300' : done ? 'text-green-400' : 'text-slate-500'
              )}>
                {step.label}
              </p>
              {active && (
                <p className="text-xs text-slate-500 mt-0.5 animate-fade-in">{step.desc}</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
