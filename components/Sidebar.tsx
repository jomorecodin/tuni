'use client'

import { Plus, MessageSquare } from 'lucide-react'

interface Session {
  id: string
  label: string
  timestamp: Date
}

interface SidebarProps {
  sessions: Session[]
  currentSessionId: string | null
  onNewSession: () => void
}

export default function Sidebar({
  sessions,
  currentSessionId,
  onNewSession,
}: SidebarProps) {
  return (
    <div className="w-64 bg-gray-100/80 backdrop-blur-lg p-4 h-screen border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="text-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">TUNI</h2>
        <p className="text-xs text-gray-500 mt-1">Asistente Academico</p>
      </div>

      {/* New session button */}
      <button
        onClick={onNewSession}
        className="flex items-center justify-center gap-2 w-full px-3 py-2 mb-4 bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium rounded-lg transition-colors"
      >
        <Plus className="w-4 h-4" />
        Nueva sesion
      </button>

      {/* Session history */}
      <div className="flex-1 overflow-y-auto">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Sesiones recientes
        </h3>
        <ul className="space-y-1">
          {sessions.map((session) => (
            <li key={session.id}>
              <button
                className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-left text-sm transition-colors ${
                  session.id === currentSessionId
                    ? 'bg-orange-100 text-orange-800'
                    : 'hover:bg-orange-50 text-gray-700'
                }`}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{session.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
