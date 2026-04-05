import React from 'react'

const variants = {
  primary: 'bg-primary-500 hover:bg-primary-600 text-white shadow-lg shadow-primary-500/20',
  secondary: 'bg-surface-3 hover:bg-surface-4 text-slate-200 border border-white/10',
  ghost: 'hover:bg-surface-3 text-slate-300',
  danger: 'bg-accent-rose/10 hover:bg-accent-rose/20 text-accent-rose border border-accent-rose/30',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2',
  lg: 'px-6 py-3 text-lg',
}

export default function Button({
  children, variant = 'primary', size = 'md',
  className = '', loading = false, ...props
}) {
  return (
    <button
      className={`inline-flex items-center gap-2 rounded-xl font-medium transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed font-body
        ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      )}
      {children}
    </button>
  )
}
