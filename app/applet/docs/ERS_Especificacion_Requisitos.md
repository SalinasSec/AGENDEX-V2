# 📄 Especificación de Requisitos de Software (ERS)
## AgendEx · Sistema de Calendarización y Control de Evaluaciones Escolares
### Liceos SOFOFA · Liceo Industrial Bicentenario RBL
**Proyecto Final de Desarrollo de Software (Proyecto Yuyito)**  
*Documento estructurado conforme al estándar IEEE 830 para Especificación de Requisitos de Software.*

---

## 1. Introducción

### 1.1 Propósito
El presente documento tiene como objetivo definir y detallar los requisitos funcionales y no funcionales para el desarrollo e implementación del software **AgendEx**, una solución web diseñada para la planificación, calendarización, supervisión de cupos diarios y gestión de asistencia y recuperaciones de evaluaciones en el **Liceo Industrial Bicentenario RBL**.

### 1.2 Alcance del Sistema
AgendEx automatiza y transparenta el ciclo completo de las evaluaciones escolares:
- Calendarización ordenada por docentes titulares de especialidad y formación general.
- Validación estricta y automática de la **Regla Institucional de Oro**: máximo 2 evaluaciones por curso en un mismo día.
- Pase de lista en sala exclusivo del docente titular y cierre oficial de nómina.
- Acreditación de justificaciones médicas y salidas pedagógicas exclusiva de Inspectoría General.
- Sincronización automática de pruebas recuperativas con cálculo reglamentario de exigencia (60% regular justificado vs 70% injustificado).
- Supervisión global para la Unidad Técnico Pedagógica (UTP) con semáforo de carga académica mensual.
- Consulta transparente y oportuna para estudiantes y apoderados.

### 1.3 Definiciones, Acrónimos y Abreviaturas
- **UTP**: Unidad Técnico Pedagógica.
- **RBL**: Liceo Industrial Bicentenario Hermenegildo (RBL).
- **SOFOFA**: Red de Liceos Técnicos de la Sociedad de Fomento Fabril.
- **PK / FK**: Primary Key (Clave Primaria) / Foreign Key (Clave Foránea).
- **CRUD**: Crear, Leer, Actualizar y Eliminar (Create, Read, Update, Delete).
- **ERS**: Especificación de Requisitos de Software.

---

## 2. Descripción General del Producto

### 2.1 Perspectiva del Producto
AgendEx opera como una aplicación web modular conectada a un motor relacional MySQL. Permite el acceso simultáneo a través de computadores de escritorio institucionales, notebooks de sala y dispositivos móviles de los estudiantes.

### 2.2 Actores y Perfiles de Usuario
1. **Unidad Técnico Pedagógica (UTP / Directivo)**:
   - Supervisa el calendario global del establecimiento.
   - Monitorea cursos en sobrecarga académica (6 o más evaluaciones mensuales).
   - Crea, edita y supervisa todas las asignaturas, profesores y nóminas.
2. **Profesor / Docente Titular**:
   - Calendariza pruebas de sus asignaturas y cursos asignados.
   - Pasa lista presencial en sala y cierra el registro oficial de asistencia.
   - Visualiza la nómina de citados a pruebas recuperativas de su asignatura.
3. **Inspectoría General**:
   - Acredita certificados médicos y autorizaciones de salida pedagógica de alumnos ausentes.
   - Ajusta y reduce la exigencia reglamentaria del 70% al 60% regular.
4. **Estudiante / Apoderado**:
   - Consulta el calendario de evaluaciones de su curso sin solapamientos.
   - Revisa el estado de sus evaluaciones rendidas y fechas de pruebas recuperativas asignadas.

---

## 3. Requisitos Funcionales (RF)

| ID | Nombre | Descripción | Actor |
| :--- | :--- | :--- | :--- |
| **RF-01** | Autenticación y Control de Acceso | El sistema debe autenticar a los usuarios mediante correo/RUT y contraseña, redirigiendo a la interfaz correspondiente según su rol (UTP, Profe, Inspe, Alumno). | Todos |
| **RF-02** | Calendarización de Evaluación | El profesor o UTP debe poder agendar una evaluación indicando título, descripción, fecha, hora, curso y asignatura asignada. | Profesor, UTP |
| **RF-03** | Control de Cupo Diario (Regla de Oro) | El sistema debe validar que ningún curso tenga más de **2 evaluaciones programadas en una misma fecha**. Si ya existen 2 pruebas, el formulario debe rechazar la creación e informar al usuario. | Sistema |
| **RF-04** | Filtrado Docente por Especialidad | Al crear o editar una evaluación, el sistema debe mostrar únicamente las asignaturas y cursos que el docente tiene formalmente asignados (ej. M5, M6, M7 para Antonio Velásquez). | Profesor |
| **RF-05** | Pase de Lista en Sala | El profesor titular debe registrar para cada estudiante convocado si estuvo **Asistente (Presente)**, **No Asiste (Injustificada)** o **Salida Pedagógica**. | Profesor Titular |
| **RF-06** | Cierre de Lista Oficial | Una vez que el docente guarda la asistencia, la lista queda bloqueada y cerrada para evitar alteraciones posteriores en sala. | Profesor Titular |
| **RF-07** | Acreditación Médica por Inspectoría | Inspectoría General debe poder visualizar los estudiantes que faltaron a una evaluación y acreditar certificados médicos o licencias, actualizando el estado a **Justificado**. | Inspectoría |
| **RF-08** | Citación a Recuperativa Automática | Si un alumno resulta ausente (injustificado o salida pedagógica), el sistema debe crear de forma automática un registro de prueba recuperativa programada a 7 días plazo. | Sistema |
| **RF-09** | Cálculo de Exigencia Diferenciada | El sistema debe asignar una exigencia del **60.00%** a estudiantes justificados o en salida pedagógica, y del **70.00%** a inasistencias injustificadas. | Sistema |
| **RF-10** | Calendario Escolar Mensual | Vista de cuadrícula mensual interactiva con navegación mes a mes, indicando días con cupos libres, 1 prueba (óptimo) o 2 pruebas (tope alcanzado). | Todos |
| **RF-11** | Semáforo de Carga Académica | Reporte de cursos con conteo mensual de pruebas totales: Normal (< 6 pruebas) o Alta Carga (>= 6 pruebas mensuales acumuladas). | UTP, Docente |
| **RF-12** | Gestión de Alumnos y Cursos | La administración debe listar estudiantes agrupados por curso, con RUT, nombre completo y estado académico. | UTP, Inspectoría |
| **RF-13** | Panel de Alumno | El estudiante debe visualizar sus próximas pruebas calendarizadas y las recuperativas pendientes con su porcentaje de exigencia (60% o 70%). | Alumno |
| **RF-14** | Edición y Cancelación de Evaluaciones | El profesor titular o UTP puede editar fecha/hora o eliminar una prueba siempre que no haya cerrado la lista de asistencia oficial. | Profesor, UTP |
| **RF-15** | Integridad mediante Procedimientos | Las operaciones críticas (verificación de cupo, registro atómico de asistencia y cálculo de carga) deben estar respaldadas por procedimientos almacenados en la base de datos. | Sistema / BD |

---

## 4. Requisitos No Funcionales (RNF)

| ID | Categoría | Requisito |
| :--- | :--- | :--- |
| **RNF-01** | **Rendimiento** | El tiempo de respuesta para verificar disponibilidad de cupo mediante API no debe superar los 300 ms en red local. |
| **RNF-02** | **Seguridad** | Las contraseñas y sesiones deben estar firmadas con `SECRET_KEY`. No se permite acceso a rutas protegidas sin inicio de sesión verificado. |
| **RNF-03** | **Integridad de Datos** | La base de datos MySQL debe aplicar restricciones de integridad referencial (`FOREIGN KEY`, `ON DELETE RESTRICT/CASCADE`) y claves únicas (`UNIQUE KEY`). |
| **RNF-04** | **Usabilidad** | Diseño responsivo compatible con dispositivos móviles, tablets y escritorios, utilizando la paleta institucional (azul marino `#14213D`, verde esmeralda `#2F6F4E` y gris institucional). |
| **RNF-05** | **Disponibilidad** | Operación local autónoma en servidores de laboratorio o computadores portátiles mediante entorno Python Flask + MySQL sin dependencia de conexión a Internet externa. |
| **RNF-06** | **Mantenibilidad** | Código fuente modular, estructurado bajo el patrón MVC (Model-View-Controller) / Microframework, debidamente documentado en español. |
| **RNF-07** | **Compatibilidad** | Compatible con navegadores modernos (Chrome, Firefox, Edge, Safari) mediante estándares web HTML5, CSS3 y JavaScript ES6. |
| **RNF-08** | **Trazabilidad** | Cada evaluación registra profesor responsable, fecha, hora, estado de asistencia y bitácora de recuperaciones. |

---

## 5. Diagramas de Casos de Uso y Modelo Relacional

### 5.1 Actores Principales
- `ACT-01`: UTP / Administrador
- `ACT-02`: Docente Titular
- `ACT-03`: Inspector General
- `ACT-04`: Alumno / Apoderado

### 5.2 Resumen de Tablas de la Base de Datos
1. `cursos`: Identificador, nombre del curso (ej. 4°G), nivel.
2. `asignaturas`: Nombre (ej. Programación Java POO), código y color distintivo.
3. `profesores`: Nombre, apellido, email institucional, especialidad.
4. `alumnos`: RUT, nombres, apellidos, ID del curso perteneciente.
5. `usuarios`: Credenciales de acceso, rol del sistema (`utp`, `profe`, `inspe`, `alumno`), vínculos foráneos.
6. `evaluaciones`: Título, contenidos, fecha, hora, curso_id, asignatura_id, profesor_id, asistencia_guardada.
7. `asistencia_evaluaciones`: evaluacion_id, alumno_id, estado_asistencia (presente, injustificada, justificado, salida), motivo.
8. `recuperaciones`: evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia (60.00 o 70.00), estado (pendiente, rendida).
