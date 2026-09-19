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

-- 2. Asignaturas con colores institucionales y Módulos de Especialidad
INSERT INTO asignaturas (id, nombre, color) VALUES
(1, 'Lenguaje y Comunicación', '#2F6F4E'),
(2, 'Matemática', '#14213D'),
(3, 'Historia, Geografía y Cs. Sociales', '#A87F2C'),
(4, 'Idioma Extranjero: Inglés', '#2C5F7A'),
(5, 'Educación Física y Salud', '#A5332A'),
(6, 'Ciencias Naturales', '#3B7A6B'),
(7, 'M8: Desarrollo de Aplicaciones Web', '#1E3157'),
(8, 'M5: Diseño y Consulta de Base de Datos (DBD)', '#4A3B7A'),
(9, 'M6: Programación Orientada a Objetos Java Escritorio (POO)', '#006699'),
(10, 'M7: Programación en PL/SQL (ABD)', '#8E2800'),
(11, 'Taller Aprestos Técnicos (Rotación 2° Medios)', '#D97706')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), color=VALUES(color);

-- 3. Profesores (con Marcela Rubio y Antonio Velásquez para Programación 4°G y 3°G)
INSERT INTO profesores (id, nombre, apellido, email, materia) VALUES
(1, 'Marcela', 'Rubio', 'marcela.rubio@liceorbl.cl', 'M8: Desarrollo de Aplicaciones Web'),
(2, 'Antonio', 'Velásquez', 'antonio.velasquez@liceorbl.cl', 'M5 DBD / M6 POO / M7 ABD'),
(3, 'Carolina', 'Reyes', 'carolina.reyes@liceosofofa.cl', 'Matemática'),
(4, 'Patricio', 'Muñoz', 'patricio.munoz@liceosofofa.cl', 'Lenguaje y Comunicación'),
(5, 'Valentina', 'Soto', 'valentina.soto@liceorbl.cl', 'Historia, Geografía y Cs. Sociales'),
(6, 'Diego', 'Fuentes', 'diego.fuentes@liceorbl.cl', 'Idioma Extranjero: Inglés'),
(7, 'Docente', 'Aprestos', 'aprestos@liceorbl.cl', 'Taller Aprestos Técnicos')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), apellido=VALUES(apellido), email=VALUES(email), materia=VALUES(materia);

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
('14.222.333-4', 'marcela.rubio@liceorbl.cl', 'profe123', 'Prof. Marcela Rubio (Jefa 4°G)', 'profe', 1, NULL, 1),
('13.333.444-5', 'antonio.velasquez@liceorbl.cl', 'profe123', 'Prof. Antonio Velásquez (Jefe 3°G)', 'profe', 2, NULL, 1),
('15.111.222-3', 'carolina.reyes@liceosofofa.cl', 'profe123', 'Prof. Carolina Reyes', 'profe', 3, NULL, 1),
('18.777.888-9', 'inspe.diaz@liceorbl.cl', 'inspe123', 'Claudia Díaz (Inspectoría)', 'inspe', NULL, NULL, 1),
('20.123.456-1', 'joaquin.rivas@liceorbl.cl', 'alumno123', 'Joaquín Rivas (Alumno 4°G)', 'alumno', NULL, 1, 1)
ON DUPLICATE KEY UPDATE clave=VALUES(clave), nombre=VALUES(nombre), rol=VALUES(rol);

-- 6. Evaluaciones de muestra
INSERT INTO evaluaciones (id, titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id) VALUES
(1, 'Prueba Desarrollo Frontend Web (Vue/React)', 'Construcción de componentes e integración de APIs en entorno frontend.', CURDATE(), '08:30:00', 7, 26, 1),
(2, 'Prueba Consultas SQL y Normalización', 'Consultas multi-tabla JOIN, agrupamientos y subconsultas.', CURDATE(), '10:15:00', 8, 19, 2),
(3, 'Evaluación Práctica Java Desktop (POO y Swing)', 'Programación en Java con patrones de herencia y ventanas.', CURDATE() + INTERVAL 2 DAY, '09:45:00', 9, 26, 2),
(4, 'Prueba Procedimientos y Triggers en PL/SQL', 'Estructuras de control y cursores explícitos en base de datos.', CURDATE() + INTERVAL 4 DAY, '11:30:00', 10, 19, 2),
(5, 'Rotación Técnica: Introducción a Programación y Circuitos', 'Módulo rotativo de aprestos técnicos en 2° medio.', CURDATE() + INTERVAL 3 DAY, '10:00:00', 11, 12, 7)
ON DUPLICATE KEY UPDATE titulo=VALUES(titulo), fecha=VALUES(fecha);
