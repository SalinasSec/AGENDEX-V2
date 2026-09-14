# AgendEx · Sistema de Gestión de Evaluaciones Escolares

Plataforma de calendarización, control de cupos y seguimiento de evaluaciones escolares desarrollada para el **Liceo Industrial Bicentenario RBL**.

---

## 🚀 Inicio Rápido en tu Computador Local (Flask + MySQL)

### Requisitos previos:
1. **Python 3.10** o superior instalado con `pip` y agregado al PATH.
2. **Servidor MySQL** encendido (por ejemplo, mediante **XAMPP**, **WampServer** o el servicio oficial de MySQL).

### Paso 1: Instalación y Configuración Automática
Haz doble clic en:
```cmd
setup.bat
```
*Este asistente:*
- Instalará las dependencias necesarias (`Flask`, `PyMySQL`, `python-dotenv`, etc.).
- Te solicitará tu contraseña de MySQL (o enter si no tiene).
- Creará la base de datos `agendex_db`, sus tablas con llaves foráneas y los procedimientos almacenados de validación (`sp_validar_disponibilidad` y `sp_crear_evaluacion`).
- Cargará la nómina completa de cursos (1° a 4° Medio), asignaturas, profesores, alumnos y usuarios.
- Generará automáticamente tu archivo `.env` local.

### Paso 2: Iniciar la Aplicación
Haz doble clic en:
```cmd
start.bat
```
El navegador se abrirá automáticamente en:
👉 **`http://localhost:5000`**

---

## 👥 Cuentas de Acceso para Pruebas

| Rol | Correo Institucional | Contraseña | Funciones Principales |
| :--- | :--- | :--- | :--- |
| **UTP / Directivo** | `utp@liceorbl.cl` | `utp123` | Gestión curricular, carga académica, configuración y nóminas. |
| **Profesor** | `carolina.reyes@liceosofofa.cl` | `profe123` | Calendarizar pruebas, validar tope de 2 diarias, pasar lista. |
| **Profesor** | `rodrigo.araya@liceosofofa.cl` | `profe123` | Especialidad programación. |
| **Inspectoría** | `inspe.diaz@liceorbl.cl` | `inspe123` | Justificación de inasistencias y fijación de recuperaciones. |
| **Alumno** | `joaquin.rivas@liceorbl.cl` | `alumno123` | Consulta de fechas, pruebas de su curso y recuperaciones. |

---

## 📐 Reglas de Negocio Implementadas

1. **Límite Diario Estricto**:
   - Cada curso puede tener como **máximo 2 evaluaciones al día**.
   - El sistema valida en tiempo real al seleccionar fecha y bloquea intentos que excedan el cupo diario.
2. **Exigencia según Justificación**:
   - Inasistencia con justificativo médico o administrativo: **60% de exigencia**.
   - Inasistencia sin justificar: **70% de exigencia**.

---

## 📁 Estructura del Repositorio

```text
├── app.py                 # Backend nativo en Python Flask
├── config.py              # Configuración y conector a MySQL
├── requirements.txt       # Dependencias de Python
├── setup.bat              # Instalador automático en Windows
├── start.bat              # Lanzador en Windows
├── database/
│   ├── schema.sql         # Tablas relacionales y procedimientos almacenados
│   ├── datos_iniciales.sql# Cursos, asignaturas, alumnos y usuarios
│   └── init_db.py         # Script interactivo de inicialización de la BD
├── templates/             # Plantillas HTML con Jinja2 (Flask)
├── public/                # Archivos estáticos CSS y JS
│   ├── css/
│   └── js/
├── server.js              # Servidor Node.js para la vista previa en la nube
└── src/                   # Datos para la vista previa en la nube
```
