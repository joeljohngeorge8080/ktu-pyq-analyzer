import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Viewer from './pages/Viewer'
import Browse from './pages/Browse'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#10131f', color: '#e2e8f0', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 12 },
          success: { iconTheme: { primary: '#2dd4bf', secondary: '#10131f' } },
          error: { iconTheme: { primary: '#fb7185', secondary: '#10131f' } },
        }}
      />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/viewer/:id" element={<Viewer />} />
          <Route path="/browse" element={<Browse />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Layout>
    </>
  )
}
