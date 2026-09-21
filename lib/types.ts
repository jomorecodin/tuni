export type Mode = "tutor"

export interface Subject {
  id_materia: string
  nombre: string
  codigo: string | null
  area_disciplinar: string | null
}

export interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export interface ChatParams {
  user_id: string
  session_id: string
  mode: Mode
  message: string
  materia_id: string | null
  history: Array<{ role: string; content: string }>
}

export interface StreamDone {
  done: true
  total_tokens: number
  elapsed_ms: number
}
