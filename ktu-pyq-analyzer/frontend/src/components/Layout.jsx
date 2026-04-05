import React, { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { LayoutDashboard, Upload, BookOpen, BarChart3, Menu, X, Zap } from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload' },
  { to: '/browse', icon: BookOpen, label: 'Browse' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
]

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full z-40 w-64 bg-surface-1 border-r border-white/07
        flex flex-col transition-transform duration-300
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0`}>
        
        <div className="p-6 border-b border-white/07">
          <Link to="/" className="flex items-center gap-3 group" onClick={() => setMobileOpen(false)}>
            <div className="w-9 h-9 rounded-xl bg-primary-500 flex items-center justify-center glow">
              <Zap size={18} className="text-white" />
            </div>
            <div>
              <div className="font-display font-bold text-white text-sm leading-none">KTU PYQ</div>
              <div className="text-xs text-slate-500 mt-0.5">Analyzer</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
                 ${isActive
                   ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                   : 'text-slate-400 hover:text-slate-200 hover:bg-surface-3'}`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/07">
          <div className="glass rounded-xl p-3 text-center">
            <p className="text-xs text-slate-500">KTU PYQ Analyzer</p>
            <p className="text-xs text-slate-600">v1.0.0</p>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/60 z-30 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* Main */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="sticky top-0 z-20 bg-surface-0/80 backdrop-blur-xl border-b border-white/07">
          <div className="flex items-center h-14 px-4 gap-4">
            <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 rounded-lg hover:bg-surface-3 text-slate-400">
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <div className="flex-1" />
            <div className="text-xs font-mono text-slate-600 hidden sm:block">
              KTU Previous Year Question Analyzer
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 bg-grid-subtle bg-grid-size">
          {children}
        </main>
      </div>
    </div>
  )
}
