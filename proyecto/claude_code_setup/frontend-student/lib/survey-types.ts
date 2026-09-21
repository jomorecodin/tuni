export interface RadioQuestion {
  id: string
  type: "radio"
  label: string
  options: string[]
  hasOther?: boolean
  required?: boolean
}

export interface CheckboxQuestion {
  id: string
  type: "checkbox"
  label: string
  options: string[]
  hasOther?: boolean
  required?: boolean
}

export interface LikertQuestion {
  id: string
  type: "likert"
  label: string
  statements: { id: string; text: string }[]
  scale: string[]
  required?: boolean
}

export interface TextQuestion {
  id: string
  type: "text"
  label: string
  multiline?: boolean
  placeholder?: string
  required?: boolean
}

export interface NumberQuestion {
  id: string
  type: "number"
  label: string
  placeholder?: string
  required?: boolean
}

export type Question =
  | RadioQuestion
  | CheckboxQuestion
  | LikertQuestion
  | TextQuestion
  | NumberQuestion

export interface SurveySection {
  id: string
  title: string
  description?: string
  questions: Question[]
}

export interface SurveyDefinition {
  id: string
  title: string
  description: string
  instructions: string
  sections: SurveySection[]
  tableName: string
}
