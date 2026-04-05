import React from 'react'

const colors = {
  blue: 'bg-primary-500/15 text-primary-400 border-primary-500/30',
  gold: 'bg-accent-gold/15 text-accent-gold border-accent-gold/30',
  teal: 'bg-accent-teal/15 text-accent-teal border-accent-teal/30',
  rose: 'bg-accent-rose/15 text-accent-rose border-accent-rose/30',
  gray: 'bg-surface-3 text-slate-400 border-white/10',
}

export default function Badge({ children, color = 'blue', className = '' }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-medium border ${colors[color]} ${className}`}>
      {children}
    </span>
  )
}
