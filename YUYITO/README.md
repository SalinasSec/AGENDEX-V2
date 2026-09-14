# AgendEx - Sistema de Gestión de Evaluaciones

Sistema web (Flask + MySQL) para el **Liceo Industrial Bicentenario de Electrotecnia RBL** que permite calendarizar evaluaciones, controlar el **límite de máximo 2 pruebas por curso por día** (validado a nivel de base de datos mediante procedimientos almacenados) y gestionar la recuperación de alumnos ausentes.

## Roles del sistema

El sistema cuenta con **4 roles** con permisos distintos:

| Rol | Acceso |
|-----|--------|
| **UTP** | Administración total: registro de cursos, asignaturas, profesores, alumnos y usuarios. Ve todos los reportes. También puede registrar asistencia y justificar ausencias. |
| **Profesor** | Registra evaluaciones (máx. 2 por curso/día), registra asistencia (ausencias) y motivo, asigna recuperaciones, consulta calendario. **No** puede justificar una ausencia. |
| **Inspectoría (inspe)** | Registra asistencia y **es quien justifica las ausencias** (define si el alumno rinde su recuperación al 60% o al 70%), asigna/gestiona recuperaciones, consulta calendario. |
| **Alumno** | Solo consulta: ve el calendario de su curso, su historial de asistencia y sus propias recuperaciones (con el % de exigencia). |

## Credenciales de acceso

Los **usuarios de ejemplo** se entregan aparte (no se publican en el proyecto). Puedes crear más usuarios desde **Configuración → Usuarios** (solo UTP).

## Base de datos desde cero

La base de datos se crea **VACÍA** (solo la estructura y los usuarios iniciales). Los datos de cursos, asignaturas, profesores, alumnos y evaluaciones se registran según el uso cotidiano:

1. Inicia sesión como **UTP**.
2. Ve a **Configuración** y registra Cursos, Asignaturas y Profesores.
3. Registra los alumnos (Alumnos → Nuevo Alumno).
4. Crea los usuarios para profesores, Inspectoría y alumnos (Configuración → Usuarios).
5. Los profesores ingresan y agendan evaluaciones.

### Cursos del liceo

El liceo tiene cursos de **1° a 4° medio**: 1°–2° van de la **A a la F**, y 3°–4° de la **A a la G** (26 cursos en total). Se cargan con el script `cursos_liceo.sql`:

- **1° y 2° Medio**: 1A, 1B, 1C, 1D, 1E, 1F · 2A–2F
- **3° y 4° Medio**: 3A–3G · 4A–4G
- **3G y 4G**: especialidad de **Programación** (registradas en el campo `nivel`; cuando se formalice el módulo de especialidades se detallarán).

> Estas especialidades se dejaron como un dato puntual. Cuando quieras, se puede ampliar para registrar cada especialidad (mecánica, electrónica, etc.).

### Datos de ejemplo (para probar)

Para testear el sistema como si estuviera en práctica, hay dos scripts:

- **`seed_ejemplo.py`** — crea asignaturas por nivel, profesores repartidos, alumnos, usuarios vinculados y evaluaciones de ejemplo.
  ```
  .venv\Scripts\python.exe seed_ejemplo.py
  ```
- **`limpiar_ejemplo.py`** — borra los datos de ejemplo y deja solo los cursos y usuarios iniciales (para pasar a la realidad).
  ```
  .venv\Scripts\python.exe limpiar_ejemplo.py
  ```

**Cuentas de ejemplo** (creadas por el seed):

| Rol | Correo | Contraseña |
|-----|--------|------------|
| UTP | `utp@liceorbl.cl` | `utp123` |
| Profesor (Matemática) | `carolina.reyes@liceosofofa.cl` | `profe123` |
| Profesor (Programación) | `rodrigo.araya@liceosofofa.cl` | `profe123` |
| Inspectoría | `inspe.diaz@liceorbl.cl` | `inspe123` |
| Alumno (4G) | `joaquin.rivas@liceorbl.cl` | `alumno123` |

> Ojo: el sistema graba el usuario en la tabla local (hashes), pero las cuentas de ejemplo se entregan aquí en la documentación del proyecto para que puedas probar. Cuando lo lleves a la realidad, borra estas cuentas con `limpiar_ejemplo.py` o elimínalas desde **Configuración → Usuarios**.

## Requisitos

- Python 3.12+
- MySQL 8.x (servicio en ejecución)
- Credenciales de MySQL (por defecto `root` / `root`)

## Instalación

1. Ejecuta **`setup.bat`** (doble clic). Esto:
   - Crea el entorno virtual `.venv`
   - Instala las dependencias de `requirements.txt`
   - Crea la base de datos `AgendEx` con la estructura de `schema.sql` (incluye los **procedimientos almacenados** de validación)
   - Carga los usuarios iniciales con `usuarios_iniciales.sql`

2. Ejecuta **`start.bat`** para iniciar el servidor. Se abrirá automáticamente en `http://localhost:5000`.

### Si ya tenías la base de datos creada (actualización)

Si tu base `AgendEx` ya existía antes de agregar el sistema de justificativos/exigencia, no hace falta recrearla desde cero: ejecuta una sola vez el script de migración, que solo agrega las columnas nuevas sin borrar datos:

```
mysql -u root -p AgendEx < migracion_justificativos.sql
```

## Funcionalidades

- **Autenticación y roles**: inicio de sesión con **correo institucional** y contraseña, identificación por RUT (clave primaria) y control de acceso por rol.

## Autenticación con correo institucional

El usuario se identifica por **RUT** (clave primaria en la tabla `usuarios`) pero **inicia sesión con su correo institucional**. Los correos se guardan en minúsculas y el login los normaliza, de modo que escribir en mayúsculas o minúsculas funciona igual.

Dominios institucionales del liceo (referencial): alumnos y funcionarios en `@liceorbl.cl`, profesores en `@liceosofofa.cl`. Ajusta estos dominios según corresponda al crear usuarios en **Configuración → Usuarios** (solo UTP).
- **Dashboard**: resumen con estadísticas adaptadas a cada rol.
- **Evaluaciones**: CRUD con **validación automática del límite de 2 evaluaciones por curso por día**, realizada por un **procedimiento almacenado** en MySQL (R.4 y R.11). Además se valida en tiempo real en el frontend.
- **Asistencia**: registro de alumnos presentes/ausentes por evaluación con motivo (Profesor, Inspectoría y UTP).
- **Justificativos y exigencia de recuperación**: solo **Inspectoría (o UTP)** puede marcar una ausencia como **justificada**. Al asignar la fecha de recuperación, el sistema calcula automáticamente la exigencia: **60%** si la ausencia fue justificada (igual que el resto del curso), **70%** si no se justificó.
- **Recuperaciones**: asignación de fechas de recuperación a ausentes, con estados (pendiente/completada/cancelada) y el % de exigencia calculado según el justificativo.
- **Alumnos**: registro y gestión por curso (UTP), con historial de asistencias y recuperaciones.
- **Reportes**: calendario mensual, alumnos pendientes de recuperación, carga académica por curso.

## Procedimientos almacenados

La base de datos incluye (en `schema.sql`):

- `sp_validar_disponibilidad(curso_id, fecha)` — devuelve cuántas evaluaciones existen y cuántos espacios quedan.
- `sp_crear_evaluacion(...)` — inserta una evaluación **validando el límite de 2 por día**; lanza un error si se excede.
- `sp_actualizar_evaluacion(...)` — actualiza validando de nuevo el límite (excluyendo la propia evaluación).
- `sp_pendientes_recuperacion()` — reporte de alumnos pendientes de recuperación.

## Estructura del proyecto

```
YUYITO/
├── app.py              # Aplicación Flask principal
├── config.py           # Configuración (conexión a BD)
├── auth.py             # Autenticación (login/logout) y decoradores de roles
├── models.py           # Modelos SQLAlchemy (incluye Usuario + roles)
├── schema.sql          # Estructura de BD + procedimientos almacenados
├── usuarios_iniciales.sql  # Usuarios iniciales de acceso
├── cursos_liceo.sql    # Cursos del liceo (1°-4° medio)
├── seed_ejemplo.py     # Datos de ejemplo para probar (asignaturas, profesores, alumnos, evaluaciones, cuentas)
├── limpiar_ejemplo.py  # Borra los datos de ejemplo (deja cursos + usuarios iniciales)
├── requirements.txt    # Dependencias Python
├── setup.bat           # Instalación automática
├── start.bat           # Inicio del servidor
├── routes/
│   ├── dashboard.py    # Panel según rol
│   ├── evaluaciones.py
│   ├── alumnos.py
│   ├── recuperaciones.py
│   ├── reportes.py
│   └── admin.py        # Gestión de cursos/asignaturas/profesores/usuarios (UTP)
├── static/css/login.css  # Estilos de la pantalla de inicio de sesión
├── static/css/style.css  # Estilos generales (identidad navy/papel/mostaza)
├── static/js/main.js
└── templates/          # Plantillas HTML
```

## Configurar credenciales MySQL

La conexión se define en `config.py`:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/AgendEx"
```

Si tu contraseña es distinta, edita esa línea (o usa la variable de entorno `DATABASE_URL`).
