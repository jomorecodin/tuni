"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Loader2 } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import { streamChat } from "@/lib/api"
import type { Message } from "@/lib/types"
import SubjectSelector from "@/components/SubjectSelector"

function UnimetLogo() {
  return (
    <svg
      className="w-1/2 h-1/2 text-gray-200"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 14l9-5-9-5-9 5 9 5z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 14l6.16-3.422A12.083 12.083 0 0112 21a12.083 12.083 0 01-6.16-10.422L12 14z"
      />
    </svg>
  )
}

interface ChatInterfaceProps {
  sessionId: string
  userId: string
  subjectId: string | null
  onSubjectChange: (id: string | null) => void
}

export default function ChatInterface({
  sessionId,
  userId,
  subjectId,
  onSubjectChange,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hola! Soy TUNI, tu asistente academico. Estoy aqui para guiarte en tu aprendizaje. Que tema te gustaria trabajar hoy?",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollContainerRef.current?.scrollTo({
      top: scrollContainerRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [messages])

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const trimmed = inputValue.trim()
    if (!trimmed || isStreaming) return

    setError(null)

    const userMessage: Message = {
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    }

    // Build history from previous messages (skip the initial greeting)
    const history = messages
      .slice(1)
      .map((m) => ({ role: m.role, content: m.content }))

    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "assistant", content: "", timestamp: new Date() },
    ])
    setInputValue("")
    setIsStreaming(true)

    try {
      await streamChat(
        {
          user_id: userId,
          session_id: sessionId,
          mode: "tutor",
          message: trimmed,
          materia_id: subjectId,
          history,
        },
        (token) => {
          setMessages((prev) => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            updated[updated.length - 1] = {
              ...last,
              content: last.content + token,
            }
            return updated
          })
        },
        () => {
          setIsStreaming(false)
        },
        (errMsg) => {
          setError(errMsg)
          setIsStreaming(false)
          // Remove the empty assistant message
          setMessages((prev) => prev.filter((m) => m.content !== ""))
        },
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error de conexión")
      setIsStreaming(false)
      setMessages((prev) => prev.filter((m) => m.content !== ""))
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-white">
      {/* Header bar */}
      <div className="px-4 py-2 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full font-medium">
            Asistente Academico
          </span>
        </div>
        <SubjectSelector selectedId={subjectId} onChange={onSubjectChange} />
      </div>

      {/* Error banner */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-b border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Messages area with watermark */}
      <div ref={scrollContainerRef} className="relative flex-1 p-6 overflow-y-auto">
        <div className="absolute inset-0 flex items-center justify-center z-0 pointer-events-none opacity-10">
          <UnimetLogo />
        </div>
        <div className="relative z-10 space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}
            >
              <div
                className={
                  msg.role === "user"
                    ? "bg-orange-500 text-white rounded-xl p-4 max-w-lg"
                    : "bg-gray-100 rounded-xl p-4 max-w-lg"
                }
              >
                {msg.role === "assistant" && msg.content === "" && isStreaming ? (
                  <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                ) : msg.role === "assistant" ? (
                  <div className="text-gray-800 prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Input form */}
      <div className="p-4 bg-transparent">
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Escribe tu mensaje..."
              disabled={isStreaming}
              className="w-full pl-4 pr-12 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 shadow-sm disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isStreaming}
              className="absolute inset-y-0 right-0 flex items-center justify-center w-12 h-full text-gray-500 hover:text-orange-500 transition-colors disabled:opacity-50"
            >
              <Send className="w-6 h-6" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
