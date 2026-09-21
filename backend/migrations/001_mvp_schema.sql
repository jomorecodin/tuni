-- ============================================
-- TUNI MVP Schema — Run in Supabase SQL Editor
-- ============================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. materia — Subject catalog
CREATE TABLE materia (
    id_materia UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    codigo TEXT,
    descripcion_breve TEXT,
    area_disciplinar TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. usuario — Anonymous operational identity
CREATE TABLE usuario (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha_alta TIMESTAMPTZ DEFAULT now(),
    trimestre_actual INTEGER,
    estado_participacion TEXT DEFAULT 'activo'
);

-- 3. inscripcion — Links user to subjects
CREATE TABLE inscripcion (
    id_inscripcion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuario(user_id),
    id_materia UUID NOT NULL REFERENCES materia(id_materia),
    trimestre_periodo TEXT,
    seccion TEXT,
    profesor_declarado TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. parametrizacion_modelo — System prompt versioning
CREATE TABLE parametrizacion_modelo (
    id_parametrizacion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modo TEXT NOT NULL CHECK (modo IN ('neutral', 'tutor')),
    version INTEGER NOT NULL DEFAULT 1,
    contenido_md TEXT NOT NULL,
    fecha_activacion TIMESTAMPTZ DEFAULT now(),
    fecha_desactivacion TIMESTAMPTZ,
    autor TEXT,
    UNIQUE (modo, version)
);

-- 5. sesion — Groups interactions
CREATE TABLE sesion (
    id_sesion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuario(user_id),
    timestamp_inicio TIMESTAMPTZ DEFAULT now(),
    timestamp_fin TIMESTAMPTZ,
    dispositivo TEXT,
    modo_inicial TEXT NOT NULL CHECK (modo_inicial IN ('neutral', 'tutor')),
    materia_declarada UUID REFERENCES materia(id_materia),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. interaccion — Core telemetry record
CREATE TABLE interaccion (
    id_interaccion UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_sesion UUID NOT NULL REFERENCES sesion(id_sesion),
    timestamp TIMESTAMPTZ DEFAULT now(),
    modo_seleccionado TEXT NOT NULL CHECK (modo_seleccionado IN ('neutral', 'tutor')),
    prompt_estudiante TEXT NOT NULL,
    respuesta_modelo TEXT,
    longitud_prompt_tokens INTEGER,
    longitud_respuesta_tokens INTEGER,
    tiempo_generacion_ms INTEGER,
    id_parametrizacion UUID REFERENCES parametrizacion_modelo(id_parametrizacion),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_sesion_user_id ON sesion(user_id);
CREATE INDEX idx_sesion_timestamp ON sesion(timestamp_inicio);
CREATE INDEX idx_interaccion_sesion ON interaccion(id_sesion);
CREATE INDEX idx_interaccion_timestamp ON interaccion(timestamp);
CREATE INDEX idx_inscripcion_user ON inscripcion(user_id);

-- Seed subjects
INSERT INTO materia (nombre, codigo, area_disciplinar) VALUES
    ('Algebra Lineal', 'MAT-301', 'Matematicas'),
    ('Matematicas Discretas', 'MAT-250', 'Matematicas'),
    ('Optimizacion', 'MAT-400', 'Matematicas'),
    ('Calculo III', 'MAT-200', 'Matematicas'),
    ('Probabilidad y Estadistica', 'MAT-350', 'Matematicas'),
    ('Programacion I', 'COM-100', 'Computacion'),
    ('Estructuras de Datos', 'COM-200', 'Computacion'),
    ('Bases de Datos', 'COM-300', 'Computacion');
