# 📖 Manual de Usuario
## AgendEx · Sistema de Evaluaciones Escolares
### Liceo Industrial Bicentenario RBL · Liceos SOFOFA
*Guía completa y ordenada para la operación autónoma del sistema por cada estamento educativo.*

---

## 1. Introducción y Acceso al Sistema

### 1.1 ¿Qué es AgendEx?
**AgendEx** es la plataforma digital oficial creada para transparentar, ordenar y optimizar la toma de evaluaciones en el Liceo Industrial Bicentenario RBL. Asegura que los estudiantes no se vean sobrecargados con más de **2 pruebas al día** y gestiona de manera transparente las asistencias, justificaciones médicas y evaluaciones recuperativas.

### 1.2 Inicio de Sesión
1. Abra su navegador web (Google Chrome, Mozilla Firefox, Microsoft Edge) e ingrese a la dirección:  
   `http://localhost:5000` (o `http://localhost:3000` en entorno de prueba).
2. En la pantalla de bienvenida, ingrese su **Correo Institucional** y su **Contraseña**.
3. Haga clic en el botón **Ingresar al Sistema**.

---

## 2. Guía por Rol de Usuario

---

### 👨‍🏫 A. Módulo del Profesor

#### 1. Ver evaluaciones calendarizadas
- Al iniciar sesión, el docente accede a su **Dashboard**, donde visualiza un resumen de sus próximas evaluaciones y pruebas del día.
- En el menú lateral izquierdo, seleccione **Evaluaciones**. Podrá filtrar por curso, asignatura y rango de fechas.

#### 2. Calendarizar una nueva evaluación (Control de 2 pruebas/día)
1. Ingrese a **Evaluaciones** y presione el botón azul **+ Nueva Evaluación**.
2. Complete los datos requeridos:
   - **Título de la Evaluación**: Ej. *Prueba 1: Programación Orientada a Objetos en Java*.
   - **Asignatura**: Seleccione una de las materias asignadas a su perfil (solo verá las que usted imparte).
   - **Curso**: Seleccione el curso correspondiente (ej. *4°G Programación*).
   - **Fecha**: Escoja el día en el calendario.
   - **Hora**: Indique el bloque horario (ej. *08:30*).
   - **Contenidos / Temario**: Detalle los aprendizajes que serán evaluados.
3. **Verificación en tiempo real de cupos**: El sistema consultará automáticamente si la fecha elegida cuenta con cupos. Si el curso ya tiene 2 evaluaciones programadas por otros profesores, el sistema impedirá el guardado y le sugerirá una fecha disponible para no sobrecargar a los alumnos.
4. Presione **Guardar Evaluación**.

#### 3. Pasar asistencia en sala (Día de la evaluación)
1. El día de la prueba, ingrese a la evaluación desde la lista o el calendario.
2. En la columna derecha verá la tabla de **Control de Asistencia** con todos los alumnos del curso.
3. Para cada estudiante, seleccione su condición:
   - **✅ Asistente**: El estudiante se presentó a rendir la evaluación.
   - **❌ No Asiste**: El estudiante faltó sin previo aviso. Automáticamente se generará una citación a prueba recuperativa con el **70% de exigencia**.
   - **🚌 Salida Pedagógica**: El estudiante participa en una actividad oficial fuera del establecimiento. Se le cita a recuperación con el **60% de exigencia regular**.
4. Agregue una observación si corresponde (ej. *Participa en feria científica*).
5. Presione **Guardar Asistencia**.
6. **Importante**: Una vez guardada, la lista queda **cerrada oficialmente** para el docente. Cualquier modificación posterior por certificados médicos corresponde exclusivamente a Inspectoría General.

---

### 🛡️ B. Módulo de Inspectoría General

#### 1. Acreditación de Justificaciones Médicas
1. Inicie sesión con perfil de Inspectoría (`inspe.diaz@liceorbl.cl`).
2. Diríjase a **Evaluaciones** y seleccione la prueba que ya fue pasada por el profesor.
3. El panel mostrará únicamente a los **estudiantes que faltaron a la prueba**.
4. Si el apoderado presenta certificado médico o licencia válida:
   - Cambie el estado de **❌ Inasistencia Injustificada** a **🏥 Justificado (Médico / Licencia)**.
   - En la casilla de observación, ingrese el **Folio del Certificado o nombre del médico**.
   - Presione **Guardar Justificaciones**.
5. **Efecto automático**: La prueba recuperativa del alumno rebajará su nivel de exigencia inmediatamente del **70% al 60% reglamentario**.

#### 2. Revisión de Casos Pendientes
- En el menú lateral, seleccione **Pendientes** o **Recuperaciones** para monitorear qué estudiantes aún no justifican sus ausencias.

---

### 🏛️ C. Módulo de UTP / Equipo Directivo

#### 1. Supervisión del Calendario Escolar General
- Acceda a **Calendario Escolar** para inspeccionar las pruebas de todos los niveles del liceo (1° a 4° medio).
- Los días con 2 evaluaciones aparecen en color distintivo indicando que el cupo diario está completo.

#### 2. Semáforo de Carga Académica Mensual
- En el menú lateral, seleccione **Carga Académica**.
- Podrá ver cuántas evaluaciones acumula cada curso en el mes:
  - **Carga Normal (< 6 evaluaciones al mes)**: Distribución pedagógica adecuada.
  - **Alta Carga (>= 6 evaluaciones al mes)**: Alerta pedagógica para redistribuir fechas y evitar la fatiga escolar en los estudiantes.

#### 3. Reportes y Descargas
- UTP puede exportar reportes en PDF/Impresión de evaluaciones y nóminas de inasistencias por curso.

---

### 🎓 D. Módulo del Alumno / Apoderado

#### 1. Mi Panel de Alumno
- Al ingresar con cuenta de alumno (`joaquin.rivas@liceorbl.cl`):
  - Visualiza sus **próximas evaluaciones** ordenadas cronológicamente para organizar su estudio.
  - Revisa su sección **Mis Recuperaciones**: si faltó a una prueba, podrá ver qué día debe rendir la recuperativa, qué profesor la tomará y si su exigencia es del **60% (justificada)** o del **70% (injustificada)**.

---

## 3. Preguntas Frecuentes y Solución de Problemas

1. **¿Por qué el sistema no me deja agendar una prueba en cierta fecha?**  
   Porque el curso ya tiene 2 pruebas registradas ese día. El reglamento del Liceo RBL prohíbe una tercera prueba para proteger el descanso y rendimiento del estudiante. Elija otro día hábil disponible.

2. **Un alumno llegó tarde y ya cerré la lista de asistencia, ¿qué hago?**  
   El profesor no puede reabrir la lista para mantener la fidelidad del libro de clases. Debe acudir a Inspectoría General para que la inspectora acredite la situación en el sistema.

3. **¿Cómo se determina la exigencia del 60% vs 70%?**  
   - Si la ausencia es injustificada: **70% de exigencia**.  
   - Si la ausencia cuenta con certificado médico validado por Inspectoría o salida pedagógica: **60% de exigencia regular**.
