import { GraduationCap, BookOpen } from "lucide-react"
import Link from "next/link"

export default function EncuestasPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-orange-100 p-4">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-800">
          Encuestas <span className="text-orange-500">TUNI</span>
        </h1>
        <p className="text-gray-600 mt-2 max-w-md mx-auto">
          Plataforma piloto de asistencia academica con telemetria — Universidad Metropolitana de
          Caracas
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-6">
        <Link
          href="/encuestas/estudiante"
          className="bg-white/60 backdrop-blur-xl p-8 rounded-xl shadow-lg w-72 flex flex-col items-center justify-center border border-gray-200 transition-transform duration-200 ease-in-out hover:scale-105 hover:-translate-y-2"
        >
          <GraduationCap className="w-16 h-16 text-orange-500" />
          <h2 className="text-xl font-semibold text-gray-800 mt-4">Soy Estudiante</h2>
          <p className="text-sm text-gray-500 text-center mt-2">
            Encuesta sobre tu experiencia con IA y expectativas academicas. ~12 minutos.
          </p>
        </Link>

        <Link
          href="/encuestas/profesor"
          className="bg-white/60 backdrop-blur-xl p-8 rounded-xl shadow-lg w-72 flex flex-col items-center justify-center border border-gray-200 transition-transform duration-200 ease-in-out hover:scale-105 hover:-translate-y-2"
        >
          <BookOpen className="w-16 h-16 text-orange-500" />
          <h2 className="text-xl font-semibold text-gray-800 mt-4">Soy Profesor</h2>
          <p className="text-sm text-gray-500 text-center mt-2">
            Encuesta sobre percepcion docente ante IA generativa. ~10 minutos.
          </p>
        </Link>
      </div>

      <p className="mt-10 text-xs text-gray-400 max-w-sm text-center">
        Tu participacion es voluntaria y anonima. Los datos se reportaran de forma agregada.
      </p>
    </div>
  )
}
