"use client"

import { GraduationCap, BookOpen, Lightbulb, Calculator } from "lucide-react"

interface OnboardingProps {
  onStart: () => void
}

export default function Onboarding({ onStart }: OnboardingProps) {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-50 to-orange-100">
      <div className="text-center mb-8 animate-fade-in-down max-w-lg">
        <GraduationCap className="w-20 h-20 text-orange-500 mx-auto mb-6" />
        <h1 className="text-5xl font-bold text-gray-800">
          Bienvenido a <span className="text-orange-500">TUNI</span>
        </h1>
        <p className="text-lg text-gray-600 mt-4 leading-relaxed">
          Tu asistente academico de la Universidad Metropolitana. Estoy aqui
          para ayudarte a estudiar, resolver dudas y guiarte en tu aprendizaje.
        </p>
        <div className="mt-6 space-y-3 text-left mx-auto max-w-sm">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <BookOpen className="w-5 h-5 text-orange-400 flex-shrink-0" />
            <span>Preguntame sobre tus materias</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <Calculator className="w-5 h-5 text-orange-400 flex-shrink-0" />
            <span>Te guio paso a paso en ejercicios</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <Lightbulb className="w-5 h-5 text-orange-400 flex-shrink-0" />
            <span>Explico conceptos de forma clara</span>
          </div>
        </div>
      </div>
      <button
        onClick={onStart}
        className="px-8 py-3 bg-orange-500 hover:bg-orange-600 text-white text-lg font-semibold rounded-xl shadow-lg transition-all duration-200 hover:scale-105"
      >
        Comenzar
      </button>
    </div>
  )
}
