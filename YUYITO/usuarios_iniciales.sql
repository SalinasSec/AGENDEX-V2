-- Usuarios iniciales para ingresar al sistema AgendEx
-- La base se crea vacía desde cero: aquí solo se crean los usuarios de prueba
-- para poder iniciar sesión. Los datos de cursos, asignaturas, profesores y
-- alumnos se registran según el uso cotidiano del sistema.
-- Identificación por RUT (clave primaria) e inicio de sesión por CORREO.

USE AgendEx;

-- Credenciales iniciales por rol (loguearse con el correo):
--   utp@liceorbl.cl      / utp123
--   profe@liceosofofa.cl / profe123
--   inspe@liceorbl.cl    / inspe123
--   alumno@liceorbl.cl   / alumno123

INSERT INTO usuarios (rut, correo, clave, nombre, rol, activo) VALUES
('19.000.001-1', 'utp@liceorbl.cl',      'scrypt:32768:8:1$VlAr7EmNFMvokSw8$bfd07a5c50748a5a64eb8f05d0e51a3e8a6b44906d24a0c600b76a2ba9def8e6607ca807f9b7823257b6cad3319d25d1cfe61c670838dbf8fabe27423b6692ee', 'Usuario UTP',        'utp',    TRUE),
('19.000.002-2', 'profe@liceosofofa.cl', 'scrypt:32768:8:1$aRogAPtpmbDxH0HK$7a3d5da1ca5cdd5b6336cf80e1fbbbb407fac2cc5c967b5829f2638881b5938a37dc7b88cd7c7765e1551d905825ceba2d3cd736076b115c74143dd25fe3c079', 'Usuario Profesor',    'profe',  TRUE),
('19.000.003-3', 'inspe@liceorbl.cl',    'scrypt:32768:8:1$dIbwT0uTIqpJAPDx$d451663aba1dc805f21ef67c74c2f2ed939840b9fb8edccb1ab65933c01ff3406c17a7fb3e21f2ae8b2dddb6100bf28224241823063889f600e1bff6c5c44bb1', 'Usuario Inspectoria', 'inspe',  TRUE),
('20.000.004-4', 'alumno@liceorbl.cl',   'scrypt:32768:8:1$oo2WHrYJXLOWfBga$0d91b06f44661ee36f16eadf00b07e8340dafbbd38b31b0ffa45448d1bbf81d3ce49f30272c4d2c0b1b9b92bfc5f3be2a8806e6cf2da8ea438333a5fde28d954', 'Usuario Alumno',      'alumno', TRUE);
