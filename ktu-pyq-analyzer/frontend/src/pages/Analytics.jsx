import React, { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts'
import Card from '../components/ui/Card'
import Select from '../components/ui/Select'
import Badge from '../components/ui/Badge'
import { useApi } from '../hooks/useApi'
import { getAnalytics, getSubjects, getOverview } from '../services/api'
import { TrendingUp, Hash, Layers } from 'lucide-react'

const COLORS = ['#4c6ef5', '#2dd4bf', '#f5c542', '#fb7185', '#a78bfa', '#34d399']

export default function Analytics() {
  const [subjectId, setSubjectId] = useState('')
  const { data: subjects } = useApi(getSubjects, [], { initial: [] })
  const subjectOpts = [{ value: '', label: 'All Subjects' }, ...(subjects?.map(s => ({ value: s.id, label: s.name })) ?? [])]

  const { data: analytics, loading } = useApi(
    () => getAnalytics({ subject_id: subjectId || undefined }),
    [subjectId]
  )
  const { data: overview } = useApi(getOverview)

  const moduleData = analytics?.module_distribution
    ? Object.entries(analytics.module_distribution).map(([k, v]) => ({
        name: k, short: v.short, long: v.long, total: v.total
      }))
    : []

  const yearData = analytics?.year_distribution
    ? Object.entries(analytics.year_distribution).map(([y, c]) => ({ year: y, count: c }))
    : []

  return (
    <div className="space-y-6 fade-up">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Analytics</h1>
          <p className="text-slate-500 mt-1">Topic frequency and question distribution</p>
        </div>
        <Select value={subjectId} onChange={setSubjectId} options={subjectOpts} className="w-48" />
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Questions', value: analytics?.total_questions ?? 0, icon: Hash, color: 'text-primary-400' },
          { label: 'Unique Tags', value: analytics?.top_tags?.length ?? 0, icon: TrendingUp, color: 'text-accent-teal' },
          { label: 'Modules Covered', value: moduleData.filter(m => m.total > 0).length, icon: Layers, color: 'text-accent-gold' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="text-center">
            <Icon size={24} className={`mx-auto mb-2 ${color}`} />
            <div className="text-2xl font-display font-bold text-white">{value}</div>
            <div className="text-xs text-slate-500">{label}</div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Module Distribution */}
        <Card>
          <h2 className="font-display font-semibold text-white mb-4">Questions per Module</h2>
          {moduleData.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-slate-600">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={moduleData} barGap={2}>
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#10131f', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 8, color: '#e2e8f0' }} />
                <Bar dataKey="short" fill="#2dd4bf" radius={[4,4,0,0]} name="Short" />
                <Bar dataKey="long" fill="#4c6ef5" radius={[4,4,0,0]} name="Long" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Year Distribution */}
        <Card>
          <h2 className="font-display font-semibold text-white mb-4">Questions by Year</h2>
          {yearData.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-slate-600">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={yearData}>
                <XAxis dataKey="year" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#10131f', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 8, color: '#e2e8f0' }} />
                <Bar dataKey="count" radius={[4,4,0,0]} name="Questions">
                  {yearData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Top Tags */}
      <Card>
        <h2 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
          <TrendingUp size={16} className="text-accent-gold" /> Top Repeated Topics
        </h2>
        {analytics?.top_tags?.length === 0 ? (
          <p className="text-slate-600 text-sm text-center py-6">Tag questions to see topic frequency here</p>
        ) : (
          <div className="space-y-2">
            {analytics?.top_tags?.map((item, i) => (
              <div key={item.tag} className="flex items-center gap-3">
                <span className="w-6 text-xs text-slate-600 text-right font-mono">{i + 1}</span>
                <div className="flex-1 bg-surface-3 rounded-full h-7 overflow-hidden relative">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${(item.count / analytics.top_tags[0].count) * 100}%`,
                      background: `linear-gradient(90deg, ${COLORS[i % COLORS.length]}40, ${COLORS[i % COLORS.length]})`,
                    }}
                  />
                  <span className="absolute inset-y-0 left-3 flex items-center text-xs text-white font-medium">{item.tag}</span>
                </div>
                <Badge color="gray" className="min-w-[2.5rem] justify-center">{item.count}</Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
