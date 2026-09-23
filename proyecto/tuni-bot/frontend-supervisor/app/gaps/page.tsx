"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getSubjects, getSubjectGaps, type SubjectGapDetail } from "@/lib/api";

export default function GapsPage() {
  const [subjects, setSubjects] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [detail, setDetail] = useState<SubjectGapDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSubjects().then((data) => {
      setSubjects(data.subjects);
      if (data.subjects.length > 0) setSelected(data.subjects[0]);
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    setDetail(null);
    getSubjectGaps(selected)
      .then((d) => { if (!cancelled) setDetail(d); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [selected]);

  const topicData = detail
    ? Object.entries(detail.topic_gap_frequency)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([topic, count]) => ({ topic, menciones: count }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analisis de Brechas</h1>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-1.5 text-sm bg-white"
        >
          {subjects.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="text-gray-500">Cargando...</p>}

      {detail && !loading && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold">{detail.sessions_count}</p>
              <p className="text-sm text-gray-500">Sesiones</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold">{detail.avg_session_depth}</p>
              <p className="text-sm text-gray-500">Prof. promedio</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold">
                {detail.avg_self_assessment?.toFixed(1) ?? "-"}
              </p>
              <p className="text-sm text-gray-500">Autoevaluacion</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <p className="text-2xl font-semibold">{detail.pre_eval_spikes.length}</p>
              <p className="text-sm text-gray-500">Picos pre-examen</p>
            </div>
          </div>

          {/* Topic gap frequency */}
          {topicData.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium mb-3">Temas mas mencionados como dificiles</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topicData} layout="vertical" margin={{ left: 10 }}>
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="topic" width={200} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="menciones" fill="#ef4444" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Eval timeline */}
          {detail.eval_timeline.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium mb-3">Cronograma de evaluaciones</h3>
              <div className="space-y-2">
                {detail.eval_timeline.map((ev, i) => {
                  const isPast = new Date(ev.fecha) < new Date();
                  return (
                    <div
                      key={i}
                      className={`flex items-center gap-4 text-sm p-2 rounded ${
                        isPast ? "bg-gray-50 text-gray-400" : "bg-white"
                      }`}
                    >
                      <span className="w-24 font-mono text-xs">{ev.fecha}</span>
                      <span className="font-medium w-48">{ev.nombre}</span>
                      <span className="text-gray-500">{ev.peso}%</span>
                      <span className="text-gray-400 text-xs truncate">
                        {ev.temas.join(", ")}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Raw gaps */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Check-in gaps */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium mb-2 text-sm">
                Dudas de check-in ({detail.checkin_gaps.length})
              </h3>
              {detail.checkin_gaps.length > 0 ? (
                <ul className="space-y-2 text-sm max-h-80 overflow-y-auto">
                  {detail.checkin_gaps.map((g, i) => (
                    <li key={i} className="border-l-2 border-amber-400 pl-2 py-1">
                      <p>{g.text}</p>
                      <p className="text-xs text-gray-400">
                        {g.attended ? "Asistio" : "No asistio"} &middot; Tema: {g.last_topic || "-"}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">Sin datos</p>
              )}
            </div>

            {/* Perceived gaps */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium mb-2 text-sm">
                Brechas percibidas ({detail.perceived_gaps.length})
              </h3>
              {detail.perceived_gaps.length > 0 ? (
                <ul className="space-y-2 text-sm max-h-80 overflow-y-auto">
                  {detail.perceived_gaps.map((g, i) => (
                    <li key={i} className="border-l-2 border-red-400 pl-2 py-1">
                      <p>{g.text}</p>
                      <p className="text-xs text-gray-400">{g.eval_tipo}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">Sin datos</p>
              )}
            </div>

            {/* Teaching gaps */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium mb-2 text-sm">
                Brechas de ensenanza ({detail.teaching_gaps.length})
              </h3>
              {detail.teaching_gaps.length > 0 ? (
                <ul className="space-y-2 text-sm max-h-80 overflow-y-auto">
                  {detail.teaching_gaps.map((g, i) => (
                    <li key={i} className="border-l-2 border-purple-400 pl-2 py-1">
                      <p>{g.text}</p>
                      <p className="text-xs text-gray-400">{g.eval_tipo}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-400">Sin datos</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
