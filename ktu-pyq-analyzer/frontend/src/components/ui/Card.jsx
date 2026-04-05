import React from 'react'

export default function Card({ children, className = '', hover = false }) {
  return (
    <div className={`glass rounded-2xl p-5 ${hover ? 'hover:border-primary-500/30 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer' : ''} ${className}`}>
      {children}
    </div>
  )
}
