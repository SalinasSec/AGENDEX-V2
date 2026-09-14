-- Migración: agrega el sistema de justificativos y exigencia de recuperaciones
-- a una base de datos AgendEx que ya existe (creada antes de este cambio).
--
-- Uso: ejecutar este script UNA sola vez sobre tu base de datos actual,
-- por ejemplo:  mysql -u tu_usuario -p AgendEx < migracion_justificativos.sql
--
-- No borra ni modifica datos existentes: solo agrega columnas nuevas.

USE AgendEx;

ALTER TABLE asistencias
    ADD COLUMN justificado BOOLEAN NOT NULL DEFAULT FALSE
    AFTER motivo;

ALTER TABLE recuperaciones
    ADD COLUMN porcentaje_exigencia DECIMAL(5,2) NOT NULL DEFAULT 70.00
    AFTER motivo;

-- Listo. Todas las asistencias existentes quedan como "no justificadas"
-- y todas las recuperaciones existentes quedan con exigencia 70%
-- (puedes corregirlas manualmente si corresponde).
