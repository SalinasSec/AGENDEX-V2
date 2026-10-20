# 📚 AgendEx · Sistema de Gestión de Evaluaciones Escolares
Plataforma de calendarización, control de cupos y seguimiento de evaluaciones escolares desarrollada para el **Liceo Industrial Bicentenario RBL** (Red de **Liceos SOFOFA**).

---

## 💡 Aclaración Importante: ¿Qué tecnologías utiliza este proyecto?
Para tu entrega y presentación oficial en el liceo, **tu aplicación está construida 100% en:**
* **🐍 Backend**: Python (Flask)
* **🗄️ Base de Datos**: MySQL (con procedimientos almacenados)
* **🎨 Frontend**: HTML5 + CSS3 (Bootstrap 5) con plantillas Jinja2 (`.html`)

> **¿Por qué ves archivos `.ejs` y `server.js` en el repositorio?**  
> `EJS` significa **Embedded JavaScript** (JavaScript incrustado). Google AI Studio es una plataforma en la nube basada en Node.js (JavaScript). Esos archivos (`server.js`, `views/*.ejs`, `package.json`) sirven **únicamente como simulador en la nube** para que pudieras ver la vista previa en vivo en la pantalla de la derecha sin necesidad de instalar MySQL en Google.  
> **Para tu presentación en el colegio, esos archivos se ignoran:** tu proyecto real está en `app.py`, `database/` y `templates/`.

---

## 🏆 Documentación Oficial según Rúbrica de Evaluación (100% Excelente)

Para dar estricto cumplimiento a los criterios de las **Rúbricas Parte 1 (Presentación)** y **Parte 2 (Desarrollo)**, se han preparado los siguientes documentos técnicos listos para entregar y defender:

| Criterio Evaluado en Rúbrica | Documento Oficial | Ubicación en el Proyecto |
| :--- | :--- | :--- |
| **Especificación de Requisitos (ERS)** | Documento formal bajo norma IEEE 830 con 15 RF y 8 RNF | [`docs/ERS_Especificacion_Requisitos.md`](docs/ERS_Especificacion_Requisitos.md) |
| **Procedimientos Almacenados (MySQL)** | 3 Stored Procedures implementados (`sp_verificar_cupo`, `sp_registrar_asistencia`, `sp_resumen_carga`) | [`database/procedimientos.sql`](database/procedimientos.sql) |
| **Manual de Usuario** | Guía de uso autónomo paso a paso para Profesor, Inspectoría, UTP y Alumno | [`docs/Manual_de_Usuario.md`](docs/Manual_de_Usuario.md) |
| **Plan y Evidencia de Pruebas (QA)** | Matriz de 10 casos de prueba y bitácora de defectos corregidos | [`docs/Plan_y_Evidencia_de_Pruebas.md`](docs/Plan_y_Evidencia_de_Pruebas.md) |
| **Presentación y Defensa Oral** | Guión de 15 minutos con roles para el grupo y banco de preguntas de la comisión | [`docs/Guion_Presentacion_y_Defensa.md`](docs/Guion_Presentacion_y_Defensa.md) |

---

## 📁 Estructura del Proyecto Explicada en Español

```text
├── 🐍 BACKEND (Python)
│   ├── app.py                  # El cerebro del sistema: rutas, lógica de profesores, asistencia y notas
│   ├── config.py               # Configuración de conexión con tu base de datos MySQL (localhost)
│   └── requirements.txt        # Librerías de Python necesarias (Flask, PyMySQL, python-dotenv)
│
├── 🗄️ BASE DE DATOS (MySQL)
│   └── database/
│       ├── schema.sql          # Estructura SQL: tablas relacionales normalizadas (3FN)
│       ├── procedimientos.sql  # Procedimientos almacenados para validación de cupo y asistencia
│       ├── datos_iniciales.sql # Datos de prueba: profesores, cursos (1° a 4° medio) y alumnos con RUT
│       └── init_db.py          # Script en Python que crea y carga la base de datos automáticamente
│
├── 📑 DOCUMENTACIÓN (Rúbricas Parte 1 y 2)
│   └── docs/
│       ├── ERS_Especificacion_Requisitos.md # Requisitos Funcionales y No Funcionales IEEE 830
│       ├── Manual_de_Usuario.md            # Manual de uso para cada estamento
│       ├── Plan_y_Evidencia_de_Pruebas.md  # Matriz de QA y corrección de errores
│       └── Guion_Presentacion_y_Defensa.md # Guión para disertar y responder a la comisión
│
├── 🎨 FRONTEND (Vistas HTML de Python)
│   ├── templates/              # Todas las pantallas que ve el usuario (archivos .html estándar):
│   │   ├── base.html           # Menú lateral y barra superior
│   │   ├── dashboard.html      # Panel principal con métricas del colegio
│   │   ├── login.html          # Pantalla de inicio de sesión
│   │   ├── evaluaciones/       # Crear pruebas, listar y pasar asistencia
│   │   ├── recuperaciones/     # Fijar fechas para alumnos ausentes
│   │   ├── reportes/           # Informes académicos y estadísticas
│   │   └── alumnos/            # Fichas de estudiantes
│   └── public/                 # Archivos estáticos:
│       ├── css/style.css       # Colores institucionales y diseño
│       └── js/                 # Interactividad (validaciones y calendarios)
│
├── ⚡ LANZADORES RÁPIDOS EN WINDOWS
│   ├── setup.bat               # Instalador con 1 clic (instala librerías y crea la base de datos)
│   └── start.bat               # Ejecutor con 1 clic (abre el navegador en http://localhost:5000)
│
└── ☁️ ENTORNO DE PRUEBAS EN LA NUBE (Google AI Studio)
    ├── server.js               # Servidor de previsualización en Node.js
    ├── views/                  # Vistas auxiliares en .ejs para la vista previa
    └── package.json            # Configuración interna del contenedor en la nube
```

---

## 🚀 Cómo ejecutar la aplicación en el computador del Liceo

### Requisitos:
1. Tener **Python** instalado (marcando la casilla *"Add Python to PATH"* al instalar).
2. Tener **MySQL** encendido (por ejemplo abriendo **XAMPP** y dando clic a *"Start"* en MySQL).

### Pasos:
1. **Configurar la base de datos por primera vez:**  
   Haz doble clic en **`setup.bat`**.  
   *Creará la base de datos `agendex_db`, sus tablas, procedimientos almacenados y cargará todos los profesores y alumnos automáticamente.*
2. **Iniciar el sistema:**  
   Haz doble clic en **`start.bat`**.  
   *Se abrirá automáticamente tu navegador en **`http://localhost:5000`** listo para usar.*

---

## 👥 Cuentas de Acceso para Demostración

| Rol | Correo Institucional | Contraseña | ¿Qué puede hacer en la app? |
| :--- | :--- | :--- | :--- |
| **Profesor** | `antonio.velasquez@liceorbl.cl` | `profe123` | Calendarizar evaluaciones de Programación (tope 2/día), pasar lista presencial y cerrar asistencia. |
| **Inspectoría** | `inspe.diaz@liceorbl.cl` | `inspe123` | Acreditar certificados médicos y salidas pedagógicas a ausentes (ajusta exigencia 60% o 70%). |
| **UTP / Directivo** | `utp@liceorbl.cl` | `utp123` | Ver métricas globales, supervisar cursos y revisar el semáforo de sobrecarga académica. |
| **Alumno** | `joaquin.rivas@liceorbl.cl` | `alumno123` | Ver el calendario de pruebas de su curso y fechas de recuperación pendientes. |
