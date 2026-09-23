const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface PilotHealth {
  timestamp: string;
  registered_students: number;
  active_students_week: number;
  sessions_today: number;
  sessions_this_week: number;
  total_conversations: number;
  total_checkins: number;
  total_reflections: number;
  subject_usage_week: Record<string, number>;
  upcoming_evaluations: {
    materia: string;
    nombre: string;
    fecha: string;
    dias: number;
  }[];
}

export interface WeeklyReport {
  period: { start: string; end: string };
  overview: {
    total_students: number;
    active_students: number;
    total_sessions: number;
    total_exchanges: number;
    subjects_with_data: number;
  };
  per_subject: Record<
    string,
    {
      sessions_count: number;
      total_exchanges: number;
      checkin_unclear_points: string[];
      checkin_count: number;
      reflection_perceived_gaps: string[];
      reflection_teaching_gaps: string[];
      reflection_avg_score: number | null;
      reflection_count: number;
      pre_eval_spikes: number;
      topic_gap_frequency: Record<string, number>;
    }
  >;
  top_gaps: { topic: string; subject: string; mentions: number }[];
}

export interface StudentSummary {
  telegram_id: number;
  consent_date: string;
  career: string;
  trimestre: number | string;
  subjects_used: string[];
  total_sessions: number;
  total_interactions: number;
  avg_session_depth: number;
  formative_substitutive_index: number;
  copy_paste_indicators: number;
  self_correction_count: number;
  checkin_count: number;
  reflection_count: number;
}

export interface SubjectGapDetail {
  materia: string;
  checkin_gaps: { text: string; timestamp: string; attended: boolean; last_topic: string }[];
  perceived_gaps: { text: string; eval_tipo: string; timestamp: string }[];
  teaching_gaps: { text: string; eval_tipo: string; timestamp: string }[];
  self_assessment_scores: number[];
  avg_self_assessment: number | null;
  pre_eval_spikes: Record<string, unknown>[];
  sessions_count: number;
  avg_session_depth: number;
  eval_timeline: { tipo: string; nombre: string; fecha: string; temas: string[]; peso: number }[];
  topic_gap_frequency: Record<string, number>;
}

export interface AiResponse {
  answer: string;
  elapsed_ms: number;
  context_length: number;
}

export function getPilotHealth() {
  return fetchApi<PilotHealth>("/pilot-health");
}

export function getWeeklyReport(weeks = 1) {
  return fetchApi<WeeklyReport>(`/analysis/weekly-report?weeks=${weeks}`);
}

export function getStudents() {
  return fetchApi<StudentSummary[]>("/analysis/students");
}

export function getSubjectGaps(materia: string) {
  return fetchApi<SubjectGapDetail>(`/analysis/gaps/${encodeURIComponent(materia)}`);
}

export function getSubjects() {
  return fetchApi<{ subjects: string[]; count: number }>("/analysis/subjects");
}

export function askAi(question: string) {
  return fetchApi<AiResponse>("/ai/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
