import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Upload, Tag, BarChart3, ArrowRight, FileText } from 'lucide-react'
import Card from '../components/ui/Card'
import { useApi } from '../hooks/useApi'
import { getOverview, getPapers, getSubjects } from '../services/api'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <Card className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${color}`}>
        <Icon size={22} />
      </div>
      <div>
        <div className="text-2xl font-display font-bold text-white">{value ?? '—'}</div>
        <div className="text-sm text-slate-500">{label}</div>
      </div>
    </Card>
  )
}

export default function Dashboard() {
  const { data: overview } = useApi(getOverview)
  const { data: papers } = useApi(() => getPapers({}), [], { initial: [] })
  const { data: subjects } = useApi(getSubjects, [], { initial: [] })

  return (
    <div className="space-y-8 fade-up">
      <div>
        <h1 className="text-3xl font-display font-bold text-white">Dashboard</h1>
        <p className="text-slate-500 mt-1">Your KTU question paper workspace</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard icon={BookOpen} label="Subjects" value={overview?.subjects} color="bg-primary-500/10 text-primary-400" />
        <StatCard icon={FileText} label="Papers" value={overview?.papers} color="bg-accent-teal/10 text-accent-teal" />
        <StatCard icon={Tag} label="Questions Tagged" value={overview?.questions} color="bg-accent-gold/10 text-accent-gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Papers */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-white">Recent Papers</h2>
            <Link to="/browse" className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          {papers?.length === 0 ? (
            <div className="text-center py-8 text-slate-600">
              <FileText size={32} className="mx-auto mb-2 opacity-40" />
              <p className="text-sm">No papers yet. Upload one!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {papers?.slice(0, 5).map(p => (
                <Link key={p.id} to={`/viewer/${p.id}`}
                  className="flex items-center justify-between p-3 rounded-xl hover:bg-surface-3 transition-colors group">
                  <div>
                    <div className="text-sm text-slate-200 font-medium group-hover:text-white">{p.original_filename}</div>
                    <div className="text-xs text-slate-500">{p.year} · {p.file_type.toUpperCase()} · {p.page_count} pages</div>
                  </div>
                  <ArrowRight size={14} className="text-slate-600 group-hover:text-primary-400 transition-colors" />
                </Link>
              ))}
            </div>
          )}
        </Card>

        {/* Quick Actions */}
        <Card>
          <h2 className="font-display font-semibold text-white mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {[
              { to: '/upload', icon: Upload, label: 'Upload a Question Paper', sub: 'PDF or image files' },
              { to: '/browse', icon: BookOpen, label: 'Browse Questions', sub: 'Filter by module, type, year' },
              { to: '/analytics', icon: BarChart3, label: 'View Analytics', sub: 'Topic frequency & distribution' },
            ].map(({ to, icon: Icon, label, sub }) => (
              <Link key={to} to={to}
                className="flex items-center gap-3 p-3 rounded-xl hover:bg-surface-3 transition-colors group">
                <div className="w-9 h-9 rounded-xl bg-surface-3 flex items-center justify-center group-hover:bg-primary-500/10 transition-colors">
                  <Icon size={16} className="text-slate-400 group-hover:text-primary-400" />
                </div>
                <div>
                  <div className="text-sm text-slate-200 font-medium">{label}</div>
                  <div className="text-xs text-slate-500">{sub}</div>
                </div>
                <ArrowRight size={14} className="ml-auto text-slate-600 group-hover:text-primary-400 transition-colors" />
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
