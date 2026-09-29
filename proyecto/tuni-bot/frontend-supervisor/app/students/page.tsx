"use client";

import { useEffect, useState } from "react";
import { getStudents, type StudentSummary } from "@/lib/api";
import { getAllUsers, getRecentSessions, type SupabaseUser, type SupabaseSession } from "@/lib/supabase";

function fsiColor(fsi: number): string {
  if (fsi >= 0.3) return "text-green-600 bg-green-50";
  if (fsi <= -0.3) return "text-red-600 bg-red-50";
  return "text-gray-600 bg-gray-50";
}

interface DbUserRow {
  user_id: string;
  telegram_id: number;
  created_at: string;
  session_count: number;
}

export default function StudentsPage() {
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [dbUsers, setDbUsers] = useState<DbUserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState<"api" | "supabase">("api");

  useEffect(() => {
    // Try API first (richer data from student JSONs)
    getStudents()
      .then((data) => {
        setStudents(data);
        setSource("api");
      })
      .catch(() => {
        // Fallback to Supabase
        setSource("supabase");
      })
      .finally(() => setLoading(false));

    // Always fetch Supabase users for the raw data tab
    Promise.all([getAllUsers(), getRecentSessions(200)])
      .then(([users, sessions]) => {
        const sessionCounts: Record<string, number> = {};
        for (const s of sessions) {
          sessionCounts[s.user_id] = (sessionCounts[s.user_id] || 0) + 1;
        }
        setDbUsers(
          users.map((u) => ({
            user_id: u.user_id,
            telegram_id: u.telegram_id,
            created_at: u.created_at,
            session_count: sessionCounts[u.user_id] || 0,
          }))
        );
      });
  }, []);

  if (loading) return <p className="p-8 text-gray-500">Cargando estudiantes...</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold">Estudiantes</h1>
        <div className="flex gap-1 text-xs">
          <button
            onClick={() => setSource("api")}
            className={`px-2 py-1 rounded ${
              source === "api" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
            disabled={students.length === 0}
          >
            API ({students.length})
          </button>
          <button
            onClick={() => setSource("supabase")}
            className={`px-2 py-1 rounded ${
              source === "supabase" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600"
            }`}
          >
            Supabase ({dbUsers.length})
          </button>
        </div>
      </div>

      {source === "api" && students.length > 0 ? (
        <>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
                  <tr>
                    <th className="px-4 py-3">ID</th>
                    <th className="px-4 py-3">Sesiones</th>
                    <th className="px-4 py-3">Interacc.</th>
                    <th className="px-4 py-3">Prof. prom.</th>
                    <th className="px-4 py-3">FSI</th>
                    <th className="px-4 py-3">Check-ins</th>
                    <th className="px-4 py-3">Reflex.</th>
                    <th className="px-4 py-3">Materias</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {students.map((s) => (
                    <tr key={s.telegram_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 font-mono text-xs">{s.telegram_id}</td>
                      <td className="px-4 py-2 text-center">{s.total_sessions}</td>
                      <td className="px-4 py-2 text-center">{s.total_interactions}</td>
                      <td className="px-4 py-2 text-center">{s.avg_session_depth.toFixed(1)}</td>
                      <td className="px-4 py-2 text-center">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${fsiColor(
                            s.formative_substitutive_index
                          )}`}
                        >
                          {s.formative_substitutive_index.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-center">{s.checkin_count}</td>
                      <td className="px-4 py-2 text-center">{s.reflection_count}</td>
                      <td className="px-4 py-2 text-xs text-gray-500">
                        {s.subjects_used.join(", ") || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="flex gap-4 text-xs text-gray-500">
            <span><strong>FSI</strong> = Indice Formativo-Sustitutivo (-1 sustitutivo, +1 formativo)</span>
            <span><strong>Prof. prom.</strong> = Profundidad promedio (mensajes/sesion)</span>
          </div>
        </>
      ) : (
        <>
          {dbUsers.length === 0 ? (
            <p className="text-gray-500">No hay estudiantes registrados todavia.</p>
          ) : (
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <p className="px-4 py-2 text-xs text-amber-600 bg-amber-50">
                Datos directos de Supabase — informacion basica de registro y sesiones
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="px-4 py-3">User ID</th>
                      <th className="px-4 py-3">Telegram ID</th>
                      <th className="px-4 py-3">Registro</th>
                      <th className="px-4 py-3">Sesiones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {dbUsers.map((u) => (
                      <tr key={u.user_id} className="hover:bg-gray-50">
                        <td className="px-4 py-2 font-mono text-xs">{u.user_id.slice(0, 8)}...</td>
                        <td className="px-4 py-2 font-mono text-xs">{u.telegram_id}</td>
                        <td className="px-4 py-2 text-xs">
                          {new Date(u.created_at).toLocaleDateString("es-VE")}
                        </td>
                        <td className="px-4 py-2 text-center">{u.session_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
