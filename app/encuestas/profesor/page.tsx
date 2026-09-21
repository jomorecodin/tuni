"use client"

import SurveyForm from "@/components/survey/SurveyForm"
import { professorSurvey } from "@/lib/survey-professor"

export default function EncuestaProfesorPage() {
  return <SurveyForm survey={professorSurvey} />
}
