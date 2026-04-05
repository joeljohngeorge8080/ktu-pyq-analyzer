import React from 'react'

export default function Select({ label, value, onChange, options, className = '' }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm text-slate-400 mb-1.5 font-medium">{label}</label>}
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full bg-surface-3 border border-white/10 rounded-xl px-3 py-2.5 text-slate-200
          focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30
          transition-colors appearance-none text-sm"
      >
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}
