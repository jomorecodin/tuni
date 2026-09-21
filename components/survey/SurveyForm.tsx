"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Send, CheckCircle, Loader2 } from "lucide-react"
import { supabase } from "@/lib/supabase"
import type { SurveyDefinition, Question } from "@/lib/survey-types"

interface SurveyFormProps {
  survey: SurveyDefinition
}

type Answers = Record<string, string | string[] | number | Record<string, string>>

export default function SurveyForm({ survey }: SurveyFormProps) {
  const [answers, setAnswers] = useState<Answers>({})
  const [section, setSection] = useState(0)
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle")
  const [errorMsg, setErrorMsg] = useState("")

  const current = survey.sections[section]
  const isLast = section === survey.sections.length - 1

  function set(id: string, value: string | string[] | number | Record<string, string>) {
    setAnswers((prev) => ({ ...prev, [id]: value }))
  }

  async function handleSubmit() {
    setStatus("submitting")
    const { error } = await supabase.from(survey.tableName).insert({ responses: answers })
    if (error) {
      setErrorMsg(error.message)
      setStatus("error")
    } else {
      setStatus("success")
    }
  }

  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-orange-100 p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Gracias por tu participacion</h2>
          <p className="text-gray-600">
            Tus respuestas han sido registradas de forma anonima. Puedes cerrar esta pagina.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-orange-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">{survey.title}</h1>
          <p className="text-sm text-gray-500 mt-1">{survey.description}</p>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>
              Seccion {section + 1} de {survey.sections.length}
            </span>
            <span>{Math.round(((section + 1) / survey.sections.length) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((section + 1) / survey.sections.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Section card */}
        <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-1">{current.title}</h2>
          {current.description && (
            <p className="text-sm text-gray-500 mb-6">{current.description}</p>
          )}

          <div className="space-y-8">
            {current.questions.map((q) => (
              <QuestionRenderer key={q.id} question={q} answers={answers} onChange={set} />
            ))}
          </div>
        </div>

        {/* Error */}
        {status === "error" && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            Error al enviar: {errorMsg}
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={() => setSection((s) => s - 1)}
            disabled={section === 0}
            className="flex items-center gap-1 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Anterior
          </button>

          {isLast ? (
            <button
              onClick={handleSubmit}
              disabled={status === "submitting"}
              className="flex items-center gap-2 px-6 py-2 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg shadow transition-colors disabled:opacity-50"
            >
              {status === "submitting" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Enviar respuestas
            </button>
          ) : (
            <button
              onClick={() => setSection((s) => s + 1)}
              className="flex items-center gap-1 px-4 py-2 text-sm bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg shadow transition-colors"
            >
              Siguiente
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─── Question renderers ─── */

function QuestionRenderer({
  question: q,
  answers,
  onChange,
}: {
  question: Question
  answers: Answers
  onChange: (id: string, value: string | string[] | number | Record<string, string>) => void
}) {
  switch (q.type) {
    case "radio":
      return <RadioField q={q} value={(answers[q.id] as string) ?? ""} otherValue={(answers[`${q.id}_other`] as string) ?? ""} onChange={onChange} />
    case "checkbox":
      return <CheckboxField q={q} value={(answers[q.id] as string[]) ?? []} otherValue={(answers[`${q.id}_other`] as string) ?? ""} onChange={onChange} />
    case "likert":
      return <LikertField q={q} value={(answers[q.id] as Record<string, string>) ?? {}} onChange={onChange} />
    case "text":
      return <TextField q={q} value={(answers[q.id] as string) ?? ""} onChange={onChange} />
    case "number":
      return <NumberField q={q} value={answers[q.id] as number | undefined} onChange={onChange} />
  }
}

function RadioField({
  q,
  value,
  otherValue,
  onChange,
}: {
  q: Extract<Question, { type: "radio" }>
  value: string
  otherValue: string
  onChange: (id: string, v: string) => void
}) {
  return (
    <fieldset>
      <legend className="text-sm font-medium text-gray-700 mb-3">
        {q.label}
        {q.required && <span className="text-red-400 ml-1">*</span>}
      </legend>
      <div className="space-y-2">
        {q.options.map((opt) => (
          <label key={opt} className="flex items-start gap-3 cursor-pointer group">
            <input
              type="radio"
              name={q.id}
              checked={value === opt}
              onChange={() => onChange(q.id, opt)}
              className="mt-0.5 w-4 h-4 text-orange-500 focus:ring-orange-500"
            />
            <span className="text-sm text-gray-600 group-hover:text-gray-800">{opt}</span>
          </label>
        ))}
        {q.hasOther && (
          <label className="flex items-start gap-3 cursor-pointer group">
            <input
              type="radio"
              name={q.id}
              checked={value === "__other__"}
              onChange={() => onChange(q.id, "__other__")}
              className="mt-0.5 w-4 h-4 text-orange-500 focus:ring-orange-500"
            />
            <div className="flex-1">
              <span className="text-sm text-gray-600">Otra:</span>
              <input
                type="text"
                value={otherValue}
                onChange={(e) => {
                  onChange(q.id, "__other__")
                  onChange(`${q.id}_other`, e.target.value)
                }}
                onFocus={() => onChange(q.id, "__other__")}
                className="ml-2 border-b border-gray-300 focus:border-orange-500 outline-none text-sm px-1 py-0.5 w-48"
                placeholder="Especifica..."
              />
            </div>
          </label>
        )}
      </div>
    </fieldset>
  )
}

function CheckboxField({
  q,
  value,
  otherValue,
  onChange,
}: {
  q: Extract<Question, { type: "checkbox" }>
  value: string[]
  otherValue: string
  onChange: (id: string, v: string | string[]) => void
}) {
  function toggle(opt: string) {
    const next = value.includes(opt) ? value.filter((v) => v !== opt) : [...value, opt]
    onChange(q.id, next)
  }

  return (
    <fieldset>
      <legend className="text-sm font-medium text-gray-700 mb-3">
        {q.label}
        {q.required && <span className="text-red-400 ml-1">*</span>}
      </legend>
      <div className="space-y-2">
        {q.options.map((opt) => (
          <label key={opt} className="flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={value.includes(opt)}
              onChange={() => toggle(opt)}
              className="mt-0.5 w-4 h-4 text-orange-500 rounded focus:ring-orange-500"
            />
            <span className="text-sm text-gray-600 group-hover:text-gray-800">{opt}</span>
          </label>
        ))}
        {q.hasOther && (
          <label className="flex items-start gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={value.includes("__other__")}
              onChange={() => toggle("__other__")}
              className="mt-0.5 w-4 h-4 text-orange-500 rounded focus:ring-orange-500"
            />
            <div className="flex-1">
              <span className="text-sm text-gray-600">Otra:</span>
              <input
                type="text"
                value={otherValue}
                onChange={(e) => {
                  if (!value.includes("__other__")) onChange(q.id, [...value, "__other__"])
                  onChange(`${q.id}_other`, e.target.value)
                }}
                className="ml-2 border-b border-gray-300 focus:border-orange-500 outline-none text-sm px-1 py-0.5 w-48"
                placeholder="Especifica..."
              />
            </div>
          </label>
        )}
      </div>
    </fieldset>
  )
}

function LikertField({
  q,
  value,
  onChange,
}: {
  q: Extract<Question, { type: "likert" }>
  value: Record<string, string>
  onChange: (id: string, v: Record<string, string>) => void
}) {
  function setStatement(statementId: string, scaleValue: string) {
    onChange(q.id, { ...value, [statementId]: scaleValue })
  }

  return (
    <fieldset>
      <legend className="text-sm font-medium text-gray-700 mb-4">
        {q.label}
        {q.required && <span className="text-red-400 ml-1">*</span>}
      </legend>
      <div className="space-y-5">
        {q.statements.map((stmt) => (
          <div key={stmt.id} className="border border-gray-100 rounded-lg p-4 bg-gray-50/50">
            <p className="text-sm text-gray-700 mb-3">{stmt.text}</p>
            <div className="flex flex-wrap gap-2">
              {q.scale.map((s, i) => (
                <label
                  key={s}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs cursor-pointer border transition-colors ${
                    value[stmt.id] === s
                      ? "bg-orange-500 text-white border-orange-500"
                      : "bg-white text-gray-600 border-gray-200 hover:border-orange-300"
                  }`}
                >
                  <input
                    type="radio"
                    name={`${q.id}_${stmt.id}`}
                    value={s}
                    checked={value[stmt.id] === s}
                    onChange={() => setStatement(stmt.id, s)}
                    className="sr-only"
                  />
                  <span className="font-medium">{i + 1}</span>
                  <span className="hidden sm:inline">{s}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </fieldset>
  )
}

function TextField({
  q,
  value,
  onChange,
}: {
  q: Extract<Question, { type: "text" }>
  value: string
  onChange: (id: string, v: string) => void
}) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700 block mb-2">
        {q.label}
        {q.required && <span className="text-red-400 ml-1">*</span>}
      </label>
      {q.multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(q.id, e.target.value)}
          rows={4}
          placeholder={q.placeholder}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 resize-y"
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(q.id, e.target.value)}
          placeholder={q.placeholder}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
        />
      )}
    </div>
  )
}

function NumberField({
  q,
  value,
  onChange,
}: {
  q: Extract<Question, { type: "number" }>
  value: number | undefined
  onChange: (id: string, v: number) => void
}) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700 block mb-2">
        {q.label}
        {q.required && <span className="text-red-400 ml-1">*</span>}
      </label>
      <input
        type="number"
        value={value ?? ""}
        onChange={(e) => onChange(q.id, Number(e.target.value))}
        placeholder={q.placeholder}
        className="w-40 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
      />
    </div>
  )
}
