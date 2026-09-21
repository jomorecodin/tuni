"use client"

import { useState, useEffect } from "react"
import { BookOpen } from "lucide-react"
import { fetchSubjects } from "@/lib/api"
import type { Subject } from "@/lib/types"

interface SubjectSelectorProps {
  selectedId: string | null
  onChange: (id: string | null) => void
}

export default function SubjectSelector({ selectedId, onChange }: SubjectSelectorProps) {
  const [subjects, setSubjects] = useState<Subject[]>([])

  useEffect(() => {
    fetchSubjects()
      .then(setSubjects)
      .catch(() => setSubjects([]))
  }, [])

  return (
    <div className="flex items-center gap-2">
      <BookOpen className="w-4 h-4 text-gray-500" />
      <select
        value={selectedId ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
        className="text-sm bg-transparent border border-gray-300 rounded-lg px-2 py-1 text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-500"
      >
        <option value="">General (sin materia)</option>
        {subjects.map((s) => (
          <option key={s.id_materia} value={s.id_materia}>
            {s.nombre} {s.codigo ? `(${s.codigo})` : ""}
          </option>
        ))}
      </select>
    </div>
  )
}
