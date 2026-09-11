import { AlertTriangle, Github, BookOpen, Users, Cpu, Database, Code2, Layers } from 'lucide-react'

const stack = [
  { cat: 'Frontend',        items: ['React 18', 'Vite', 'Tailwind CSS', 'Recharts', 'Lucide React', 'React Router v6'] },
  { cat: 'Backend',         items: ['Python 3.11', 'FastAPI', 'Uvicorn', 'Pydantic v2', 'SQLAlchemy (async)'] },
  { cat: 'Image Analysis',  items: ['Pillow', 'OpenCV', 'NumPy', 'piexif'] },
  { cat: 'Machine Learning',items: ['PyTorch', 'Torchvision', 'EfficientNet-B0', 'Scikit-learn'] },
  { cat: 'Database',        items: ['SQLite', 'aiosqlite', 'SQLAlchemy ORM'] },
]

const limitations = [
  'No detection system achieves 100% accuracy. Results are estimates.',
  'The AI visual model depends on training data and may not generalise to new AI generators.',
  'Metadata can be stripped, edited, or falsified — it is supporting evidence only.',
  'C2PA credentials are absent from most images — absence is not evidence of AI generation.',
  'Watermark verification APIs are not publicly available for most providers.',
  'Forensic signals may appear in compressed, resized, or heavily edited real photographs.',
  'Screenshot or re-upload strips most provenance signals from images.',
]

const future = [
  'Integration of additional forensic techniques (GAN fingerprint detection)',
  'Support for video file analysis',
  'Real-time collaborative analysis workspace',
  'Integration with public C2PA verification registry',
  'Batch image analysis mode',
  'Export reports as PDF',
  'API rate limiting and authentication',
]

const team = [
  { name: 'Subasri N',      role: 'ML & Backend',              desc: 'PyTorch model training, FastAPI services, database design' },
  { name: 'Sanjay Kumar M', role: 'Frontend & Integration',    desc: 'React UI, API integration, responsive design' },
  { name: 'Soundharya K',   role: 'Forensics & Research',      desc: 'Digital forensics analysis, evidence fusion, research' },
]

export default function About() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-12 space-y-14 animate-fade-in">

      {/* Header */}
      <div className="text-center">
        <p className="section-label mb-2">About This Project</p>
        <h1 className="text-3xl font-bold text-slate-100">AI Image Authenticity Detection &amp; Digital Forensics System</h1>
        <p className="text-slate-400 mt-3 max-w-2xl mx-auto text-sm leading-relaxed">
          A final-year computer science project that combines machine learning, digital forensics,
          metadata analysis, and content provenance checking to estimate whether an image is real or
          AI-generated — with full transparency about confidence and limitations.
        </p>
      </div>

      {/* Purpose */}
      <section className="card">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-5 h-5 text-primary-400" />
          <h2 className="font-bold text-slate-100 text-lg">Project Purpose</h2>
        </div>
        <p className="text-slate-300 text-sm leading-relaxed mb-3">
          The rapid advancement of AI image generation (Stable Diffusion, Midjourney, DALL-E, etc.)
          has made it increasingly difficult to distinguish AI-generated images from real photographs.
          This poses challenges in journalism, social media verification, academic integrity, and legal contexts.
        </p>
        <p className="text-slate-300 text-sm leading-relaxed">
          This system aims to provide a transparent, evidence-based tool for image authenticity estimation.
          It deliberately avoids making absolute claims and always presents multiple evidence streams,
          confidence ranges, and clear limitations.
        </p>
      </section>

      {/* Tech stack */}
      <section>
        <div className="flex items-center gap-2 mb-6">
          <Code2 className="w-5 h-5 text-primary-400" />
          <h2 className="font-bold text-slate-100 text-lg">Technology Stack</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {stack.map(({ cat, items }) => (
            <div key={cat} className="card-sm">
              <h3 className="font-semibold text-primary-300 text-sm mb-2">{cat}</h3>
              <ul className="space-y-1">
                {items.map(it => (
                  <li key={it} className="text-xs text-slate-400 flex items-center gap-1.5">
                    <span className="w-1 h-1 rounded-full bg-primary-600 flex-shrink-0" />
                    {it}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section>
        <div className="flex items-center gap-2 mb-6">
          <Users className="w-5 h-5 text-primary-400" />
          <h2 className="font-bold text-slate-100 text-lg">Project Team</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          {team.map(({ name, role, desc }) => (
            <div key={name} className="card text-center">
              <div className="w-14 h-14 mx-auto bg-gradient-to-br from-primary-500 to-violet-600 rounded-2xl flex items-center justify-center text-2xl font-bold text-white mb-3">
                {name[0]}
              </div>
              <h3 className="font-bold text-slate-200">{name}</h3>
              <p className="text-primary-400 text-xs font-semibold mt-1 mb-2">{role}</p>
              <p className="text-slate-500 text-xs leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Limitations */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h2 className="font-bold text-slate-100 text-lg">Known Limitations</h2>
        </div>
        <div className="card bg-amber-900/10 border-amber-800/30 space-y-2">
          {limitations.map((l, i) => (
            <div key={i} className="flex items-start gap-2 text-sm text-amber-300/80">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-400" />
              {l}
            </div>
          ))}
        </div>
      </section>

      {/* Future scope */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Layers className="w-5 h-5 text-primary-400" />
          <h2 className="font-bold text-slate-100 text-lg">Future Scope</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {future.map((f, i) => (
            <div key={i} className="card-sm flex items-start gap-2 text-sm text-slate-300">
              <span className="text-primary-400 font-bold flex-shrink-0">{String(i+1).padStart(2,'0')}</span>
              {f}
            </div>
          ))}
        </div>
      </section>

    </div>
  )
}
