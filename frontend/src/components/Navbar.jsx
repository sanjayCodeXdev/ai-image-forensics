import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { Shield, ScanSearch, History, Info, Menu, X, Upload } from 'lucide-react'
import clsx from 'clsx'

const navLinks = [
  { to: '/',        label: 'Home',    icon: Shield   },
  { to: '/analyze', label: 'Analyze', icon: Upload   },
  { to: '/history', label: 'History', icon: History  },
  { to: '/about',   label: 'About',   icon: Info     },
]

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-surface-border bg-surface/80 backdrop-blur-lg">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-violet-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-primary-500/30 transition-shadow">
            <ScanSearch className="w-5 h-5 text-white" />
          </div>
          <div className="hidden sm:block">
            <span className="font-bold text-slate-100 text-sm leading-none">AI Forensics</span>
            <p className="text-xs text-slate-400 leading-none mt-0.5">Authenticity Detection</p>
          </div>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                clsx('flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-primary-600/20 text-primary-300 border border-primary-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                )
              }
            >
              <Icon className="w-4 h-4" /> {label}
            </NavLink>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
          <Link to="/analyze" className="btn-primary text-sm py-2 px-4">
            <Upload className="w-4 h-4" /> Analyze Image
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden btn-ghost p-2"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-surface-border bg-surface/95 backdrop-blur-lg px-4 pb-4 pt-2 animate-fade-in">
          {navLinks.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                clsx('flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
                  isActive
                    ? 'bg-primary-600/20 text-primary-300'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                )
              }
            >
              <Icon className="w-4 h-4" /> {label}
            </NavLink>
          ))}
          <Link
            to="/analyze"
            onClick={() => setMobileOpen(false)}
            className="btn-primary w-full mt-3 justify-center"
          >
            <Upload className="w-4 h-4" /> Analyze Image
          </Link>
        </div>
      )}
    </header>
  )
}
