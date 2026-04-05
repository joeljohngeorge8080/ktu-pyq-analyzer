import React from 'react'

export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className={className}>
      {label && <label className="block text-sm text-slate-400 mb-1.5 font-medium">{label}</label>}
      <input
        className={`w-full bg-surface-3 border rounded-xl px-3 py-2.5 text-slate-200 placeholder:text-slate-600
          focus:outline-none focus:ring-1 transition-colors text-sm
          ${error ? 'border-accent-rose focus:border-accent-rose focus:ring-accent-rose/30'
                  : 'border-white/10 focus:border-primary-500 focus:ring-primary-500/30'}`}
        {...props}
      />
      {error && <p className="text-accent-rose text-xs mt-1">{error}</p>}
    </div>
  )
}
