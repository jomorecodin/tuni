import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// --- Typed query helpers ---

export interface SupabaseSession {
  id_sesion: string;
  user_id: string;
  modo_inicial: string;
  dispositivo: string;
  materia_declarada: string | null;
  timestamp_fin: string | null;
  created_at: string;
}

export interface SupabaseInteraction {
  id_interaccion: string;
  id_sesion: string;
  modo_seleccionado: string;
  prompt_estudiante: string;
  respuesta_modelo: string;
  longitud_prompt_tokens: number;
  longitud_respuesta_tokens: number;
  tiempo_generacion_ms: number;
  created_at: string;
}

export interface SupabaseUser {
  user_id: string;
  telegram_id: number;
  estado_participacion: string;
  created_at: string;
}

export async function getSessionCount(): Promise<number> {
  const { count } = await supabase
    .from("sesion")
    .select("*", { count: "exact", head: true });
  return count ?? 0;
}

export async function getInteractionCount(): Promise<number> {
  const { count } = await supabase
    .from("interaccion")
    .select("*", { count: "exact", head: true });
  return count ?? 0;
}

export async function getStudentCount(): Promise<number> {
  const { count } = await supabase
    .from("usuario")
    .select("*", { count: "exact", head: true });
  return count ?? 0;
}

export async function getTodaySessionCount(): Promise<number> {
  const today = new Date().toISOString().split("T")[0];
  const { count } = await supabase
    .from("sesion")
    .select("*", { count: "exact", head: true })
    .gte("created_at", today);
  return count ?? 0;
}

export async function getRecentSessions(limit = 50): Promise<SupabaseSession[]> {
  const { data } = await supabase
    .from("sesion")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);
  return data ?? [];
}

export async function getStudentSessions(userId: string): Promise<SupabaseSession[]> {
  const { data } = await supabase
    .from("sesion")
    .select("*")
    .eq("user_id", userId)
    .order("created_at", { ascending: false });
  return data ?? [];
}

export async function getAllUsers(): Promise<SupabaseUser[]> {
  const { data } = await supabase
    .from("usuario")
    .select("*")
    .order("created_at", { ascending: false });
  return data ?? [];
}

export async function getInteractionsForSession(
  sessionId: string
): Promise<SupabaseInteraction[]> {
  const { data } = await supabase
    .from("interaccion")
    .select("*")
    .eq("id_sesion", sessionId)
    .order("created_at", { ascending: true });
  return data ?? [];
}

export async function getInteractionCountPerSubject(): Promise<
  { materia: string; count: number }[]
> {
  // Since interactions don't have a direct subject field,
  // we join through sesion.materia_declarada
  const { data } = await supabase
    .from("sesion")
    .select("materia_declarada, interaccion(count)")
    .not("materia_declarada", "is", null);

  if (!data) return [];

  const counts: Record<string, number> = {};
  for (const row of data) {
    const materia = row.materia_declarada || "Sin materia";
    const interactionCount =
      Array.isArray(row.interaccion) ? row.interaccion.length : 0;
    counts[materia] = (counts[materia] || 0) + interactionCount;
  }

  return Object.entries(counts).map(([materia, count]) => ({ materia, count }));
}
