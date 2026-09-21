"use client"

import SurveyForm from "@/components/survey/SurveyForm"
import { studentSurvey } from "@/lib/survey-student"

export default function EncuestaEstudiantePage() {
  return <SurveyForm survey={studentSurvey} />
}
