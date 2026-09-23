-- Migration 004: Update materia table with real curriculum subjects
-- Ingenieria de Sistemas, trimestres 3, 4 y 5

-- Add new columns
ALTER TABLE materia ADD COLUMN IF NOT EXISTS carrera TEXT DEFAULT 'Ingenieria de Sistemas';
ALTER TABLE materia ADD COLUMN IF NOT EXISTS trimestre INTEGER;
ALTER TABLE materia ADD COLUMN IF NOT EXISTS codigo TEXT;

-- Remove old subjects (they don't match the real curriculum)
DELETE FROM materia;

-- Trimestre III
INSERT INTO materia (nombre, carrera, trimestre, codigo) VALUES
  ('Matematicas II', 'Ingenieria de Sistemas', 3, 'BPTMI02'),
  ('Fisica I', 'Ingenieria de Sistemas', 3, 'BPTFI01'),
  ('Algoritmos y Programacion', 'Ingenieria de Sistemas', 3, 'BPTSP05'),
  ('Laboratorio de Quimica General', 'Ingenieria de Sistemas', 3, NULL),
  ('Ideas emprendedoras', 'Ingenieria de Sistemas', 3, 'FBTEM02');

-- Trimestre IV
INSERT INTO materia (nombre, carrera, trimestre, codigo) VALUES
  ('Matematicas III', 'Ingenieria de Sistemas', 4, 'BPTMI03'),
  ('Fisica II', 'Ingenieria de Sistemas', 4, 'BPTFI02'),
  ('Estructuras de Datos', 'Ingenieria de Sistemas', 4, 'BPTSP06'),
  ('Matematicas Discretas', 'Ingenieria de Sistemas', 4, 'BPTMI30'),
  ('Venezuela, identidad y contexto', 'Ingenieria de Sistemas', 4, 'FBTHE11');

-- Trimestre V
INSERT INTO materia (nombre, carrera, trimestre, codigo) VALUES
  ('Matematicas IV', 'Ingenieria de Sistemas', 5, 'BPTMI04'),
  ('Laboratorio de Fisica aplicada', 'Ingenieria de Sistemas', 5, 'BPTFI05'),
  ('Sistemas de Informacion', 'Ingenieria de Sistemas', 5, 'FPTSP04'),
  ('Arquitectura del Computador', 'Ingenieria de Sistemas', 5, 'BPTEN12'),
  ('Algebra Lineal', 'Ingenieria de Sistemas', 5, 'BPTMI31');

-- DOWN migration:
-- ALTER TABLE materia DROP COLUMN IF EXISTS carrera;
-- ALTER TABLE materia DROP COLUMN IF EXISTS trimestre;
-- ALTER TABLE materia DROP COLUMN IF EXISTS codigo;
-- DELETE FROM materia;
-- INSERT INTO materia (nombre) VALUES ('Algebra Lineal'), ('Matematicas Discretas'), ('Optimizacion'), ('Calculo III'), ('Probabilidad y Estadistica'), ('Programacion I'), ('Estructuras de Datos'), ('Bases de Datos');
