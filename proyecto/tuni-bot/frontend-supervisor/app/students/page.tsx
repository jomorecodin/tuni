"use client";

import { useEffect, useState } from "react";
import { getStudents, type StudentSummary } from "@/lib/api";

function fsiColor(fsi: number): string {
  if (fsi >= 0.3) return "text-green-600 bg-green-50";
  if (fsi <= -0.3) return "text-red-600 bg-red-50";
  return "text-gray-600 bg-gray-50";
}

export default function StudentsPage() {
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStudents()
      .then(setStudents)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-8 text-gray-500">Cargando estudiantes...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Estudiantes ({students.length})</h1>

      {students.length === 0 ? (
        <p className="text-gray-500">No hay estudiantes registrados todavia.</p>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Carrera</th>
                  <th className="px-4 py-3">Trim.</th>
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
                    <td className="px-4 py-2">{s.career || "-"}</td>
                    <td className="px-4 py-2 text-center">{s.trimestre || "-"}</td>
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
      )}

      {/* Legend */}
      <div className="flex gap-4 text-xs text-gray-500">
        <span>
          <strong>FSI</strong> = Indice Formativo-Sustitutivo (-1 sustitutivo, +1 formativo)
        </span>
        <span>
          <strong>Prof. prom.</strong> = Profundidad promedio (mensajes/sesion)
        </span>
      </div>
    </div>
  );
}
