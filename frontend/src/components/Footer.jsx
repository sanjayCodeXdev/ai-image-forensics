import { Link } from 'react-router-dom'
import { ScanSearch, Github, AlertTriangle } from 'lucide-react'

const team = ['Subasri N', 'Sanjay Kumar M', 'Soundharya K']

export default function Footer() {
  return (
    <footer className="border-t border-surface-border bg-surface mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-violet-600 rounded-lg flex items-center justify-center">
                <ScanSearch className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-200 text-sm">AI Image Forensics</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Authenticity Detection & Digital Forensics System.
              A final-year project combining ML and digital forensics.
            </p>
          </div>

          {/* Team */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Project Team</h3>
            <ul className="space-y-1">
              {team.map(name => (
                <li key={name} className="text-sm text-slate-400 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary-500 flex-shrink-0" />
                  {name}
                </li>
              ))}
            </ul>
          </div>

          {/* Disclaimer */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Disclaimer
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Results are estimations based on technical evidence.
              No system can detect AI-generated images with 100% accuracy.
              Do not use for legal or forensic purposes without expert review.
            </p>
          </div>
        </div>

        <div className="divider" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-slate-600">
            © 2024 AI Image Forensics System. Final Year Mini Project.
          </p>
          <p className="text-xs text-slate-600">
            Built with FastAPI · React · PyTorch · OpenCV
          </p>
        </div>
      </div>
    </footer>
  )
}
