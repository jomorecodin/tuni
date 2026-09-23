"use client";

import { useState, useRef } from "react";
import { Send, Loader2 } from "lucide-react";
import { askAi, type AiResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  elapsed_ms?: number;
}

const SUGGESTED_QUERIES = [
  "Cuales son las brechas mas criticas detectadas hasta ahora?",
  "Que materias tienen menos actividad y deberian preocuparme?",
  "Los estudiantes estan usando el bot de forma formativa o sustitutiva?",
  "Hay patrones de estudio de ultimo minuto antes de los examenes?",
  "Que temas reportan los estudiantes que no se explicaron bien en clase?",
];

export default function AiPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  async function handleSubmit(question?: string) {
    const q = question || input.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);

    try {
      const resp = await askAi(q);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: resp.answer, elapsed_ms: resp.elapsed_ms },
      ]);
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

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <h1 className="text-2xl font-bold mb-4">Consulta IA</h1>

      {/* Chat area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="space-y-3 mt-8">
            <p className="text-gray-500 text-sm text-center">
              Hazle preguntas al modelo sobre los datos recopilados en el piloto.
              El LLM recibe todo el contexto actualizado del piloto.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl mx-auto">
              {SUGGESTED_QUERIES.map((q, i) => (
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
            Analizando datos del piloto...
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
            placeholder="Escribe tu pregunta sobre el piloto..."
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
