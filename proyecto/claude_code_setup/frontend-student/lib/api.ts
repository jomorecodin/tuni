import type { Subject, ChatParams, StreamDone } from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? ""

export async function fetchSubjects(): Promise<Subject[]> {
  const res = await fetch(`${API_BASE}/api/subjects`)
  if (!res.ok) throw new Error(`Failed to fetch subjects: ${res.status}`)
  const data = await res.json()
  return data.subjects
}

export async function createSession(params: {
  user_id: string
  mode: string
  materia_id: string | null
}): Promise<string> {
  const res = await fetch(`${API_BASE}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Failed to create session: ${res.status}`)
  const data = await res.json()
  return data.id_sesion
}

export async function streamChat(
  params: ChatParams,
  onToken: (token: string) => void,
  onDone: (meta: StreamDone) => void,
  onError: (error: string) => void,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })

  if (!res.ok || !res.body) {
    onError(`Chat request failed: ${res.status}`)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n\n")
    buffer = lines.pop() ?? ""

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue
      try {
        const data = JSON.parse(line.slice(6))
        if (data.error) {
          onError(data.error)
          return
        }
        if (data.done) {
          onDone(data as StreamDone)
        } else {
          onToken(data.content)
        }
      } catch {
        // skip malformed chunks
      }
    }
  }
}
