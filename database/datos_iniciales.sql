-- ============================================================
-- AgendEx · Datos Iniciales (Liceo Industrial Bicentenario RBL)
-- ============================================================

USE agendex_db;

-- 1. Cursos Oficiales (1° Medio a 4° Medio con especialidades)
INSERT INTO cursos (id, nombre, nivel) VALUES
(1, '1A', 'Media'), (2, '1B', 'Media'), (3, '1C', 'Media'), (4, '1D', 'Media'), (5, '1E', 'Media'), (6, '1F', 'Media'),
(7, '2A', 'Media'), (8, '2B', 'Media'), (9, '2C', 'Media'), (10, '2D', 'Media'), (11, '2E', 'Media'), (12, '2F', 'Media'),
(13, '3A', 'Electricidad'), (14, '3B', 'Electricidad'), (15, '3C', 'Electronica'), (16, '3D', 'Electronica'), (17, '3E', 'Telecomunicación'), (18, '3F', 'Telecomunicación'), (19, '3G', 'Programacion'),
(20, '4A', 'Electricidad'), (21, '4B', 'Electricidad'), (22, '4C', 'Electronica'), (23, '4D', 'Electronica'), (24, '4E', 'Telecomunicación'), (25, '4F', 'Telecomunicación'), (26, '4G', 'Programacion')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), nivel=VALUES(nivel);

-- 2. Asignaturas con colores institucionales
INSERT INTO asignaturas (id, nombre, color) VALUES
(1, 'Lenguaje y Comunicación', '#2F6F4E'),
(2, 'Matemática', '#14213D'),
(3, 'Historia, Geografía y Cs. Sociales', '#A87F2C'),
(4, 'Idioma Extranjero: Inglés', '#2C5F7A'),
(5, 'Educación Física y Salud', '#A5332A'),
(6, 'Ciencias Naturales', '#3B7A6B'),
(7, 'Programación y Algoritmos', '#1E3157'),
(8, 'Bases de Datos Relacionales', '#4A3B7A')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), color=VALUES(color);

-- 3. Profesores
INSERT INTO profesores (id, nombre, apellido, email, materia) VALUES
(1, 'Carolina', 'Reyes', 'carolina.reyes@liceosofofa.cl', 'Matemática'),
(2, 'Patricio', 'Muñoz', 'patricio.munoz@liceosofofa.cl', 'Lenguaje y Comunicación'),
(3, 'Valentina', 'Soto', 'valentina.soto@liceorbl.cl', 'Historia, Geografía y Cs. Sociales'),
(4, 'Diego', 'Fuentes', 'diego.fuentes@liceorbl.cl', 'Idioma Extranjero: Inglés'),
(5, 'Marcela', 'Vargas', 'marcela.vargas@liceorbl.cl', 'Ciencias Naturales'),
(6, 'Rodrigo', 'Araya', 'rodrigo.araya@liceosofofa.cl', 'Programación y Algoritmos'),
(7, 'Andrea', 'Pizarro', 'andrea.pizarro@liceorbl.cl', 'Bases de Datos Relacionales')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), apellido=VALUES(apellido);

-- 4. Alumnos
INSERT INTO alumnos (id, rut, nombre, apellido, curso_id) VALUES
(1, '20.123.456-1', 'Joaquín', 'Rivas', 26),
(2, '20.234.567-2', 'Camila', 'Torres', 26),
(3, '20.345.678-3', 'Bastián', 'Núñez', 26),
(4, '21.111.222-3', 'Francisca', 'Lara', 19),
(5, '20.555.666-7', 'Matías', 'González', 1),
(6, '19.888.999-0', 'Antonia', 'Sepúlveda', 12)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), apellido=VALUES(apellido), curso_id=VALUES(curso_id);

-- 5. Cuentas de Acceso (Usuarios iniciales)
INSERT INTO usuarios (rut, correo, clave, nombre, rol, profesor_id, alumno_id, activo) VALUES
('19.000.001-1', 'utp@liceorbl.cl', 'utp123', 'Equipo Directivo UTP', 'utp', NULL, NULL, 1),
('15.111.222-3', 'carolina.reyes@liceosofofa.cl', 'profe123', 'Prof. Carolina Reyes', 'profe', 1, NULL, 1),
('13.444.555-6', 'rodrigo.araya@liceosofofa.cl', 'profe123', 'Prof. Rodrigo Araya', 'profe', 6, NULL, 1),
('18.777.888-9', 'inspe.diaz@liceorbl.cl', 'inspe123', 'Claudia Díaz (Inspectoría)', 'inspe', NULL, NULL, 1),
('20.123.456-1', 'joaquin.rivas@liceorbl.cl', 'alumno123', 'Joaquín Rivas (Alumno 4°G)', 'alumno', NULL, 1, 1)
ON DUPLICATE KEY UPDATE clave=VALUES(clave), nombre=VALUES(nombre), rol=VALUES(rol);

-- 6. Evaluaciones de muestra
INSERT INTO evaluaciones (id, titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id) VALUES
(1, 'Prueba Números Enteros y Fracciones', 'Operaciones combinadas y problemas aplicados.', CURDATE() - INTERVAL 2 DAY, '10:00:00', 2, 1, 1),
(2, 'Ensayo de Literatura Contemporánea', 'Redacción guiada sobre narrativa hispanoamericana.', CURDATE(), '08:30:00', 1, 1, 2),
(3, 'Evaluación Práctica Programación', 'Desarrollo de módulos en Python y programación orientada a objetos.', CURDATE(), '10:00:00', 7, 26, 6),
(4, 'Modelo Entidad-Relación y Normalización', 'Diseño de bases de datos relacionales en 3FN.', CURDATE() + INTERVAL 2 DAY, '11:00:00', 8, 26, 7),
(5, 'Evaluación Comprensión Lectora Inglés', 'Lectura técnica sobre circuitos y vocabulario específico.', CURDATE() + INTERVAL 4 DAY, '10:30:00', 4, 19, 4)
ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), fecha=VALUES(fecha);
