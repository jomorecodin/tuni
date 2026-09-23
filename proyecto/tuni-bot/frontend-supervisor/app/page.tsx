"use client";

import { useEffect, useState } from "react";
import { Users, MessageSquare, ClipboardCheck, CalendarClock } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { StatsCard } from "@/components/StatsCard";
import { getPilotHealth, getWeeklyReport, type PilotHealth, type WeeklyReport } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<PilotHealth | null>(null);
  const [report, setReport] = useState<WeeklyReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getPilotHealth(), getWeeklyReport(2)])
      .then(([h, r]) => {
        setHealth(h);
        setReport(r);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="p-8">
        <h2 className="text-lg font-semibold text-red-600">Error de conexion</h2>
        <p className="text-gray-600 mt-2">
          No se pudo conectar con la API del supervisor. Asegurate de que el servidor este corriendo en el puerto 8001.
        </p>
        <pre className="mt-2 text-sm text-red-500">{error}</pre>
      </div>
    );
  }

  if (!health || !report) {
    return <div className="p-8 text-gray-500">Cargando datos del piloto...</div>;
  }

  const subjectData = Object.entries(health.subject_usage_week).map(([name, count]) => ({
    name: name.length > 20 ? name.slice(0, 18) + "..." : name,
    sesiones: count,
  }));

  const topGaps = report.top_gaps.slice(0, 8);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Panel del Piloto</h1>
        <p className="text-sm text-gray-500">
          Ultima actualizacion: {new Date(health.timestamp).toLocaleString("es-VE")}
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          title="Estudiantes registrados"
          value={health.registered_students}
          subtitle={`${health.active_students_week} activos esta semana`}
          icon={<Users size={18} />}
        />
        <StatsCard
          title="Sesiones hoy"
          value={health.sessions_today}
          subtitle={`${health.sessions_this_week} esta semana`}
          icon={<MessageSquare size={18} />}
        />
        <StatsCard
          title="Check-ins"
          value={health.total_checkins}
          subtitle="Registros de clase completados"
          icon={<ClipboardCheck size={18} />}
        />
        <StatsCard
          title="Reflexiones"
          value={health.total_reflections}
          subtitle="Post-examen completadas"
          icon={<CalendarClock size={18} />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subject usage chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium mb-3">Uso por materia (ultima semana)</h3>
          {subjectData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={subjectData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="sesiones" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 py-8 text-center">Sin datos de sesiones esta semana</p>
          )}
        </div>

        {/* Top gaps */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium mb-3">Brechas mas mencionadas</h3>
          {topGaps.length > 0 ? (
            <div className="space-y-2">
              {topGaps.map((gap, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <div>
                    <span className="font-medium">{gap.topic}</span>
                    <span className="text-gray-400 ml-2">({gap.subject})</span>
                  </div>
                  <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded text-xs font-medium">
                    {gap.mentions}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-8 text-center">
              Aun no hay brechas detectadas. Los datos apareceran cuando los estudiantes completen check-ins y reflexiones.
            </p>
          )}
        </div>
      </div>

      {/* Upcoming evaluations */}
      {health.upcoming_evaluations.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="font-medium mb-3">Evaluaciones proximas</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {health.upcoming_evaluations.map((ev, i) => (
              <div
                key={i}
                className={`rounded-md p-3 border text-sm ${
                  ev.dias <= 3
                    ? "border-red-200 bg-red-50"
                    : ev.dias <= 7
                    ? "border-amber-200 bg-amber-50"
                    : "border-gray-200 bg-gray-50"
                }`}
              >
                <p className="font-medium">{ev.nombre}</p>
                <p className="text-gray-500">{ev.materia}</p>
                <p className="text-xs mt-1">
                  {ev.fecha} &mdash;{" "}
                  <span className="font-medium">
                    {ev.dias === 0 ? "Hoy" : ev.dias === 1 ? "Manana" : `en ${ev.dias} dias`}
                  </span>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overview period */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-medium mb-3">Resumen del periodo ({report.period.start} - {report.period.end})</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center text-sm">
          <div>
            <p className="text-2xl font-semibold">{report.overview.total_sessions}</p>
            <p className="text-gray-500">Sesiones</p>
          </div>
          <div>
            <p className="text-2xl font-semibold">{report.overview.total_exchanges}</p>
            <p className="text-gray-500">Intercambios</p>
          </div>
          <div>
            <p className="text-2xl font-semibold">{report.overview.active_students}</p>
            <p className="text-gray-500">Estudiantes activos</p>
          </div>
          <div>
            <p className="text-2xl font-semibold">{report.overview.subjects_with_data}</p>
            <p className="text-gray-500">Materias activas</p>
          </div>
          <div>
            <p className="text-2xl font-semibold">{report.overview.total_students}</p>
            <p className="text-gray-500">Total registrados</p>
          </div>
        </div>
      </div>
    </div>
  );
}
