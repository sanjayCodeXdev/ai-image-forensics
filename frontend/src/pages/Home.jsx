import { Link } from 'react-router-dom'
import {
  Upload, Shield, ScanSearch, Database, Cpu, FileSearch,
  AlertTriangle, ChevronRight, Users, Layers, CheckCircle2
} from 'lucide-react'

const features = [
  { icon: FileSearch,  title: 'Metadata Analysis',       desc: 'EXIF, XMP, IPTC extraction with AI-software detection' },
  { icon: Shield,      title: 'Provenance Checking',      desc: 'C2PA / Content Credentials detection' },
  { icon: Cpu,         title: 'AI Visual Detection',      desc: 'EfficientNet-B0 real vs AI image classifier' },
  { icon: ScanSearch,  title: 'Digital Forensics',        desc: 'ELA, noise, frequency, texture, edge analysis' },
  { icon: Layers,      title: 'Evidence Fusion',          desc: 'Transparent weighted multi-signal classification' },
  { icon: Database,    title: 'Analysis History',         desc: 'Review and compare past analyses' },
]

const steps = [
  { n: '01', title: 'Upload Image',        desc: 'Drag & drop or browse a JPG, PNG, WEBP, or TIFF image.' },
  { n: '02', title: 'Automated Analysis',  desc: 'Our pipeline runs metadata, provenance, AI model, and forensic checks.' },
  { n: '03', title: 'Evidence Fusion',     desc: 'All signals are combined with transparent weights into a final score.' },
  { n: '04', title: 'Detailed Report',     desc: 'View a full report with evidence cards, charts, and honest limitations.' },
]

const team = [
  { name: 'Subasri N',      role: 'ML & Backend' },
  { name: 'Sanjay Kumar M', role: 'Frontend & Integration' },
  { name: 'Soundharya K',   role: 'Forensics & Research' },
]

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 space-y-24">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="text-center space-y-6 animate-slide-up">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-primary-600/15 border border-primary-600/30 rounded-full text-primary-300 text-sm font-medium mb-2">
          <span className="dot-green animate-pulse" />
          Final Year Mini Project · Computer Science
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight">
          <span className="text-gradient">AI Image Authenticity</span>
          <br />
          <span className="text-slate-100">Detection System</span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Analyse images using metadata extraction, provenance checking, AI visual
          detection, and digital forensics to estimate whether an image is real or
          AI-generated — with transparent confidence scores and honest limitations.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Link to="/analyze" className="btn-primary text-base py-3 px-8">
            <Upload className="w-5 h-5" /> Start Analysis
            <ChevronRight className="w-4 h-4" />
          </Link>
          <Link to="/about" className="btn-secondary text-base py-3 px-8">
            Learn More
          </Link>
        </div>

        {/* Disclaimer */}
        <div className="inline-flex items-start gap-2 p-3 bg-amber-900/15 border border-amber-800/30 rounded-xl text-amber-300/80 text-xs max-w-lg mx-auto text-left">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          Results are estimations based on technical evidence and should not be
          used as definitive legal or forensic proof. No system achieves 100% accuracy.
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section>
        <div className="text-center mb-10">
          <p className="section-label mb-2">Capabilities</p>
          <h2 className="text-3xl font-bold text-slate-100">Multi-Signal Analysis Pipeline</h2>
          <p className="text-slate-500 mt-2">Six independent evidence sources combined into one transparent verdict</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass-card hover:border-primary-600/30 transition-all group">
              <div className="w-10 h-10 bg-primary-600/20 rounded-xl flex items-center justify-center mb-4 group-hover:bg-primary-600/30 transition-colors">
                <Icon className="w-5 h-5 text-primary-400" />
              </div>
              <h3 className="font-semibold text-slate-200 mb-1">{title}</h3>
              <p className="text-sm text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────────── */}
      <section>
        <div className="text-center mb-10">
          <p className="section-label mb-2">Workflow</p>
          <h2 className="text-3xl font-bold text-slate-100">How It Works</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {steps.map(({ n, title, desc }) => (
            <div key={n} className="card text-center relative group hover:border-primary-600/40 transition-colors">
              <div className="text-4xl font-black text-gradient mb-3">{n}</div>
              <h3 className="font-semibold text-slate-200 mb-2">{title}</h3>
              <p className="text-sm text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Important Principles ──────────────────────────────────────────── */}
      <section className="card bg-gradient-to-br from-surface-card to-primary-950/30 border-primary-800/30">
        <h2 className="font-bold text-xl text-slate-100 mb-5">Important Analysis Principles</h2>
        <ul className="space-y-3">
          {[
            'Metadata alone is not proof. It can be removed, edited, or falsified.',
            'Missing metadata does NOT mean an image is AI-generated.',
            'Camera metadata does NOT automatically prove an image is real.',
            'Absence of C2PA credentials does not indicate the image is fake.',
            '"Signal not detected" for watermarks does NOT prove an image is real.',
            'Results are estimates — not definitive forensic or legal evidence.',
          ].map(p => (
            <li key={p} className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-primary-400 flex-shrink-0 mt-0.5" />
              {p}
            </li>
          ))}
        </ul>
      </section>

      {/* ── Team ──────────────────────────────────────────────────────────── */}
      <section className="text-center">
        <p className="section-label mb-2">Team</p>
        <h2 className="text-3xl font-bold text-slate-100 mb-8">Project Team</h2>
        <div className="flex flex-wrap justify-center gap-5">
          {team.map(({ name, role }) => (
            <div key={name} className="glass-card text-center w-52">
              <div className="w-14 h-14 mx-auto bg-gradient-to-br from-primary-500 to-violet-600 rounded-2xl flex items-center justify-center mb-3 text-2xl font-bold text-white">
                {name[0]}
              </div>
              <p className="font-semibold text-slate-200 text-sm">{name}</p>
              <p className="text-xs text-slate-500 mt-1">{role}</p>
            </div>
          ))}
        </div>
      </section>

    </div>
  )
}
