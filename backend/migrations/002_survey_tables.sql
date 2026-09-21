-- UP: Survey response tables
CREATE TABLE IF NOT EXISTS respuesta_encuesta_estudiante (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    responses JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS respuesta_encuesta_profesor (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    responses JSONB NOT NULL
);

-- RLS: allow anonymous insert and read
ALTER TABLE respuesta_encuesta_estudiante ENABLE ROW LEVEL SECURITY;
ALTER TABLE respuesta_encuesta_profesor ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_insert_estudiante" ON respuesta_encuesta_estudiante
    FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select_estudiante" ON respuesta_encuesta_estudiante
    FOR SELECT TO anon USING (true);

CREATE POLICY "anon_insert_profesor" ON respuesta_encuesta_profesor
    FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_select_profesor" ON respuesta_encuesta_profesor
    FOR SELECT TO anon USING (true);

-- DOWN:
-- DROP POLICY IF EXISTS "anon_select_profesor" ON respuesta_encuesta_profesor;
-- DROP POLICY IF EXISTS "anon_insert_profesor" ON respuesta_encuesta_profesor;
-- DROP POLICY IF EXISTS "anon_select_estudiante" ON respuesta_encuesta_estudiante;
-- DROP POLICY IF EXISTS "anon_insert_estudiante" ON respuesta_encuesta_estudiante;
-- DROP TABLE IF EXISTS respuesta_encuesta_profesor;
-- DROP TABLE IF EXISTS respuesta_encuesta_estudiante;
