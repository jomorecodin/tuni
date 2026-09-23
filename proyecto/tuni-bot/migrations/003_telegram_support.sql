-- Migration 003: Telegram bot support
-- UP

-- Add Telegram identity mapping to usuario table
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS telegram_id BIGINT UNIQUE;
CREATE INDEX IF NOT EXISTS idx_usuario_telegram_id ON usuario(telegram_id);

-- Behavioral event tracking for pedagogical analysis
CREATE TABLE IF NOT EXISTS evento_interaccion (
    id_evento UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interaccion UUID REFERENCES interaccion(id_interaccion),
    id_sesion UUID NOT NULL REFERENCES sesion(id_sesion),
    tipo_evento TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    metadata_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_evento_sesion ON evento_interaccion(id_sesion);
CREATE INDEX IF NOT EXISTS idx_evento_tipo ON evento_interaccion(tipo_evento);

-- Enable RLS
ALTER TABLE evento_interaccion ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon insert on evento_interaccion"
    ON evento_interaccion FOR INSERT
    TO anon WITH CHECK (true);

CREATE POLICY "Allow anon select on evento_interaccion"
    ON evento_interaccion FOR SELECT
    TO anon USING (true);

-- DOWN (for rollback):
-- DROP POLICY IF EXISTS "Allow anon select on evento_interaccion" ON evento_interaccion;
-- DROP POLICY IF EXISTS "Allow anon insert on evento_interaccion" ON evento_interaccion;
-- DROP INDEX IF EXISTS idx_evento_tipo;
-- DROP INDEX IF EXISTS idx_evento_sesion;
-- DROP TABLE IF EXISTS evento_interaccion;
-- DROP INDEX IF EXISTS idx_usuario_telegram_id;
-- ALTER TABLE usuario DROP COLUMN IF EXISTS telegram_id;
