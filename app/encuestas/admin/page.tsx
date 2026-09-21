"use client"

import { useState, useEffect, useCallback } from "react"
import { RefreshCw, Users, BookOpen, Download } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts"
import { supabase } from "@/lib/supabase"
import { studentSurvey } from "@/lib/survey-student"
import { professorSurvey } from "@/lib/survey-professor"
import type { SurveyDefinition, Question } from "@/lib/survey-types"

const COLORS = ["#f97316", "#fb923c", "#fdba74", "#fed7aa", "#ffedd5", "#6b7280", "#9ca3af", "#d1d5db"]

interface ResponseRow {
  id: string
  created_at: string
  responses: Record<string, unknown>
}

export default function AdminDashboard() {
  const [tab, setTab] = useState<"estudiante" | "profesor">("estudiante")
  const [studentData, setStudentData] = useState<ResponseRow[]>([])
  const [professorData, setProfessorData] = useState<ResponseRow[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    const [s, p] = await Promise.all([
      supabase.from("respuesta_encuesta_estudiante").select("*").order("created_at", { ascending: false }),
      supabase.from("respuesta_encuesta_profesor").select("*").order("created_at", { ascending: false }),
    ])
    setStudentData((s.data as ResponseRow[]) ?? [])
    setProfessorData((p.data as ResponseRow[]) ?? [])
    setLoading(false)
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const data = tab === "estudiante" ? studentData : professorData
  const survey = tab === "estudiante" ? studentSurvey : professorSurvey

  function exportCsv() {
    if (data.length === 0) return
    const keys = Object.keys(data[0].responses)
    const header = ["id", "created_at", ...keys].join(",")
    const rows = data.map((r) => {
      const vals = keys.map((k) => {
        const v = r.responses[k]
        if (typeof v === "object" && v !== null) return `"${JSON.stringify(v).replace(/"/g, '""')}"`
        return `"${String(v ?? "").replace(/"/g, '""')}"`
      })
      return [r.id, r.created_at, ...vals].join(",")
    })
    const csv = [header, ...rows].join("\n")
    const blob = new Blob([csv], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `encuesta_${tab}_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-800">
              TUNI — Dashboard de Encuestas
            </h1>
            <p className="text-sm text-gray-500">Panel administrativo</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={exportCsv}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="w-4 h-4" />
              Exportar CSV
            </button>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Actualizar
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("estudiante")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === "estudiante"
                ? "bg-orange-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <Users className="w-4 h-4" />
            Estudiantes ({studentData.length})
          </button>
          <button
            onClick={() => setTab("profesor")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === "profesor"
                ? "bg-orange-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Profesores ({professorData.length})
          </button>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <StatCard label="Total respuestas" value={data.length} />
          <StatCard
            label="Ultima respuesta"
            value={
              data.length > 0
                ? new Date(data[0].created_at).toLocaleDateString("es-VE", {
                    day: "numeric",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "—"
            }
          />
          <StatCard
            label="Hoy"
            value={
              data.filter(
                (r) =>
                  new Date(r.created_at).toDateString() === new Date().toDateString()
              ).length
            }
          />
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          </div>
        ) : data.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            No hay respuestas todavia para esta encuesta.
          </div>
        ) : (
          <div className="space-y-8">
            {survey.sections.map((section) => (
              <div key={section.id}>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">{section.title}</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {section.questions.map((q) => (
                    <QuestionChart key={q.id} question={q} responses={data} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
    </div>
  )
}

function QuestionChart({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  if (question.type === "text") {
    return <TextResponses question={question} responses={responses} />
  }
  if (question.type === "number") {
    return <NumberSummary question={question} responses={responses} />
  }
  if (question.type === "likert") {
    return <LikertChart question={question} responses={responses} />
  }
  if (question.type === "radio") {
    return <DistributionChart question={question} responses={responses} />
  }
  if (question.type === "checkbox") {
    return <CheckboxChart question={question} responses={responses} />
  }
  return null
}

function DistributionChart({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  const counts: Record<string, number> = {}
  for (const r of responses) {
    const val = r.responses[question.id] as string
    if (val) counts[val] = (counts[val] || 0) + 1
  }
  const chartData = Object.entries(counts)
    .map(([name, count]) => ({ name: name.length > 30 ? name.slice(0, 30) + "..." : name, count, fullName: name }))
    .sort((a, b) => b.count - a.count)

  if (chartData.length === 0) return null

  return (
    <ChartCard title={question.label}>
      {chartData.length <= 5 ? (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={chartData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ""} (${((percent ?? 0) * 100).toFixed(0)}%)`}>
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 32)}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" allowDecimals={false} />
            <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#f97316" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </ChartCard>
  )
}

function CheckboxChart({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  if (question.type !== "checkbox") return null
  const counts: Record<string, number> = {}
  for (const r of responses) {
    const val = r.responses[question.id] as string[]
    if (Array.isArray(val)) {
      for (const v of val) {
        const label = v === "__other__" ? `Otra: ${(r.responses[`${question.id}_other`] as string) || ""}` : v
        counts[label] = (counts[label] || 0) + 1
      }
    }
  }
  const chartData = Object.entries(counts)
    .map(([name, count]) => ({ name: name.length > 40 ? name.slice(0, 40) + "..." : name, count }))
    .sort((a, b) => b.count - a.count)

  if (chartData.length === 0) return null

  return (
    <ChartCard title={question.label}>
      <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 32)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" allowDecimals={false} />
          <YAxis type="category" dataKey="name" width={200} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#fb923c" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

function LikertChart({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  if (question.type !== "likert") return null
  const scale = question.scale

  const chartData = question.statements.map((stmt) => {
    let total = 0
    let count = 0
    for (const r of responses) {
      const val = r.responses[question.id] as Record<string, string> | undefined
      if (val?.[stmt.id]) {
        const idx = scale.indexOf(val[stmt.id])
        if (idx >= 0) {
          total += idx + 1
          count++
        }
      }
    }
    return {
      name: stmt.text.length > 35 ? stmt.text.slice(0, 35) + "..." : stmt.text,
      promedio: count > 0 ? Math.round((total / count) * 10) / 10 : 0,
      n: count,
    }
  })

  return (
    <ChartCard title={question.label} subtitle={`Escala: 1=${scale[0]} ... ${scale.length}=${scale[scale.length - 1]}`}>
      <ResponsiveContainer width="100%" height={Math.max(200, chartData.length * 40)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, scale.length]} allowDecimals={false} />
          <YAxis type="category" dataKey="name" width={200} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(value) => [`${value} / ${scale.length}`, "Promedio"]} />
          <Bar dataKey="promedio" fill="#f97316" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

function TextResponses({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  const texts = responses
    .map((r) => r.responses[question.id] as string)
    .filter((t) => t && t.trim().length > 0)

  if (texts.length === 0) return null

  return (
    <ChartCard title={question.label}>
      <div className="max-h-48 overflow-y-auto space-y-2">
        {texts.map((t, i) => (
          <p key={i} className="text-sm text-gray-600 border-l-2 border-orange-300 pl-3">
            {t}
          </p>
        ))}
      </div>
    </ChartCard>
  )
}

function NumberSummary({ question, responses }: { question: Question; responses: ResponseRow[] }) {
  const nums = responses
    .map((r) => r.responses[question.id] as number)
    .filter((n) => typeof n === "number" && !isNaN(n))

  if (nums.length === 0) return null

  const avg = Math.round((nums.reduce((a, b) => a + b, 0) / nums.length) * 10) / 10
  const min = Math.min(...nums)
  const max = Math.max(...nums)

  return (
    <ChartCard title={question.label}>
      <div className="flex gap-6 py-4">
        <div>
          <p className="text-xs text-gray-500">Promedio</p>
          <p className="text-2xl font-bold text-orange-500">{avg}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Min</p>
          <p className="text-2xl font-bold text-gray-600">{min}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Max</p>
          <p className="text-2xl font-bold text-gray-600">{max}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Respuestas</p>
          <p className="text-2xl font-bold text-gray-600">{nums.length}</p>
        </div>
      </div>
    </ChartCard>
  )
}

function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <p className="text-sm font-medium text-gray-700 mb-1">{title}</p>
      {subtitle && <p className="text-xs text-gray-400 mb-2">{subtitle}</p>}
      {children}
    </div>
  )
}
