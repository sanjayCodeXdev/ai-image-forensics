import { Bot, CheckCircle, HelpCircle } from 'lucide-react'
import clsx from 'clsx'

const CONFIG = {
  likely_ai_generated: {
    label:   'Likely AI-Generated',
    icon:    Bot,
    classes: 'badge-ai',
    dot:     'dot-red',
    glow:    'glow-red',
  },
  likely_real: {
    label:   'Likely Real / Authentic',
    icon:    CheckCircle,
    classes: 'badge-real',
    dot:     'dot-green',
    glow:    'glow-green',
  },
  inconclusive: {
    label:   'Inconclusive',
    icon:    HelpCircle,
    classes: 'badge-inconclusive',
    dot:     'dot-amber',
    glow:    '',
  },
}

export default function ResultBadge({ result, large = false }) {
  const cfg = CONFIG[result] || {
    label: result || 'Unknown',
    icon: HelpCircle,
    classes: 'badge-neutral',
    dot: 'dot-gray',
    glow: '',
  }
  const Icon = cfg.icon

  return (
    <span className={clsx(cfg.classes, large && 'text-base px-4 py-2')}>
      <span className={clsx(cfg.dot, 'animate-pulse')} aria-hidden />
      <Icon className={clsx(large ? 'w-5 h-5' : 'w-4 h-4')} />
      {cfg.label}
    </span>
  )
}
