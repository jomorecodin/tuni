"use client"

import { useState, useCallback, useRef } from "react"
import Sidebar from "@/components/Sidebar"
import ChatInterface from "@/components/ChatInterface"
import { createSession } from "@/lib/api"

interface Session {
  id: string
  label: string
  timestamp: Date
}

export default function ChatLayout() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(null)
  const [isCreatingSession, setIsCreatingSession] = useState(false)

  // Stable user ID for this browser session
  const userIdRef = useRef<string>(crypto.randomUUID())
  const userId = userIdRef.current

  const startSession = useCallback(
    async (subjectId: string | null) => {
      setIsCreatingSession(true)
      try {
        const sessionId = await createSession({
          user_id: userId,
          mode: "tutor",
          materia_id: subjectId,
        })
        setSessions((prev) => [
          ...prev,
          {
            id: sessionId,
            label: `Sesion ${prev.length + 1}`,
            timestamp: new Date(),
          },
        ])
        setCurrentSessionId(sessionId)
      } catch {
        // If backend is down, use a local UUID so the UI still works
        const fallbackId = crypto.randomUUID()
        setSessions((prev) => [
          ...prev,
          {
            id: fallbackId,
            label: `Sesion ${prev.length + 1}`,
            timestamp: new Date(),
          },
        ])
        setCurrentSessionId(fallbackId)
      } finally {
        setIsCreatingSession(false)
      }
    },
    [userId],
  )

  // Auto-create the first session
  if (currentSessionId === null && !isCreatingSession) {
    startSession(selectedSubjectId)
  }

  function handleNewSession() {
    startSession(selectedSubjectId)
  }

  function handleSubjectChange(id: string | null) {
    setSelectedSubjectId(id)
    // Changing subject creates a new session (per MODELO.md)
    startSession(id)
  }

  if (!currentSessionId) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-gray-500">Iniciando sesion...</p>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewSession={handleNewSession}
      />
      <ChatInterface
        key={currentSessionId}
        sessionId={currentSessionId}
        userId={userId}
        subjectId={selectedSubjectId}
        onSubjectChange={handleSubjectChange}
      />
    </div>
  )
}
