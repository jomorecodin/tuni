-- Migration 005: Post-exam reflection support
-- UP

CREATE TABLE IF NOT EXISTS reflexion_post_evaluacion (
    id_reflexion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT NOT NULL REFERENCES usuario(telegram_id),
    materia TEXT NOT NULL,
    eval_tipo TEXT NOT NULL,
    eval_fecha DATE NOT NULL,
    self_assessment INTEGER CHECK (self_assessment BETWEEN 1 AND 5),
    perceived_gaps TEXT,
    teaching_gaps TEXT,
    response_delay_hours NUMERIC(6,2),
    timestamp TIMESTAMPTZ DEFAULT now(),

    UNIQUE(telegram_id, materia, eval_tipo, eval_fecha)
);

CREATE INDEX IF NOT EXISTS idx_reflexion_telegram ON reflexion_post_evaluacion(telegram_id);
CREATE INDEX IF NOT EXISTS idx_reflexion_materia ON reflexion_post_evaluacion(materia);
CREATE INDEX IF NOT EXISTS idx_reflexion_fecha ON reflexion_post_evaluacion(eval_fecha);

-- RLS
ALTER TABLE reflexion_post_evaluacion ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon insert on reflexion_post_evaluacion"
    ON reflexion_post_evaluacion FOR INSERT
    TO anon WITH CHECK (true);

CREATE POLICY "Allow anon select on reflexion_post_evaluacion"
    ON reflexion_post_evaluacion FOR SELECT
    TO anon USING (true);

-- DOWN:
-- DROP POLICY IF EXISTS "Allow anon select on reflexion_post_evaluacion" ON reflexion_post_evaluacion;
-- DROP POLICY IF EXISTS "Allow anon insert on reflexion_post_evaluacion" ON reflexion_post_evaluacion;
-- DROP INDEX IF EXISTS idx_reflexion_fecha;
-- DROP INDEX IF EXISTS idx_reflexion_materia;
-- DROP INDEX IF EXISTS idx_reflexion_telegram;
-- DROP TABLE IF EXISTS reflexion_post_evaluacion;
