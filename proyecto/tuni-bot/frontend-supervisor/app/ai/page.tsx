"use client";

import { useState, useRef } from "react";
import { Send, Loader2, Database, Brain } from "lucide-react";
import { askAi, type AiResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  elapsed_ms?: number;
  sql?: string;
}

type QueryMode = "patterns" | "sql";

const SUGGESTED_PATTERNS = [
  "Cuales son las brechas mas criticas detectadas hasta ahora?",
  "Los estudiantes estan usando el bot de forma formativa o sustitutiva?",
  "Hay patrones de estudio de ultimo minuto antes de los examenes?",
  "Que temas reportan los estudiantes que no se explicaron bien en clase?",
];

const SUGGESTED_SQL = [
  "Cuantas sesiones se han creado en total?",
  "Cual es el promedio de interacciones por sesion?",
  "Cuantos estudiantes se registraron esta semana?",
  "Cual es el tiempo promedio de generacion por respuesta?",
];

async function askSql(question: string): Promise<{ answer: string; sql: string; elapsed_ms: number }> {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api";
  const res = await fetch(`${API_BASE}/ai/sql-query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export default function AiPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<QueryMode>("patterns");
  const scrollRef = useRef<HTMLDivElement>(null);

  async function handleSubmit(question?: string) {
    const q = question || input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      if (mode === "sql") {
        const resp = await askSql(q);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: resp.answer,
            elapsed_ms: resp.elapsed_ms,
            sql: resp.sql,
          },
        ]);
      } else {
        const resp = await askAi(q);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: resp.answer, elapsed_ms: resp.elapsed_ms },
        ]);
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${e instanceof Error ? e.message : "desconocido"}` },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight), 100);
    }
  }

  const suggestions = mode === "sql" ? SUGGESTED_SQL : SUGGESTED_PATTERNS;

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <div className="flex items-center gap-4 mb-4">
        <h1 className="text-2xl font-bold">Consulta IA</h1>
        <div className="flex gap-1 text-xs">
          <button
            onClick={() => setMode("patterns")}
            className={`flex items-center gap-1 px-3 py-1.5 rounded ${
              mode === "patterns" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
          >
            <Brain size={14} /> Patrones
          </button>
          <button
            onClick={() => setMode("sql")}
            className={`flex items-center gap-1 px-3 py-1.5 rounded ${
              mode === "sql" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
          >
            <Database size={14} /> SQL exploratorio
          </button>
        </div>
      </div>

      {/* Chat area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="space-y-3 mt-8">
            <p className="text-gray-500 text-sm text-center">
              {mode === "sql"
                ? "Haz preguntas en lenguaje natural y el modelo generara consultas SQL contra Supabase."
                : "Hazle preguntas al modelo sobre los datos recopilados en el piloto."}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
              {suggestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSubmit(q)}
                  className="text-left text-sm p-3 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-3xl ${msg.role === "user" ? "ml-auto" : "mr-auto"}`}
          >
            <div
              className={`rounded-lg px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-white border border-gray-200"
              }`}
            >
              {msg.content}
            </div>
            {msg.sql && (
              <details className="mt-1">
                <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
                  Ver SQL generado
                </summary>
                <pre className="mt-1 p-2 bg-gray-900 text-green-400 rounded text-xs overflow-x-auto">
                  {msg.sql}
                </pre>
              </details>
            )}
            {msg.elapsed_ms && (
              <p className="text-xs text-gray-400 mt-1">
                {(msg.elapsed_ms / 1000).toFixed(1)}s
              </p>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Loader2 size={16} className="animate-spin" />
            {mode === "sql" ? "Generando y ejecutando SQL..." : "Analizando datos del piloto..."}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 pt-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              mode === "sql"
                ? "Pregunta sobre los datos (se traduce a SQL)..."
                : "Escribe tu pregunta sobre el piloto..."
            }
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
