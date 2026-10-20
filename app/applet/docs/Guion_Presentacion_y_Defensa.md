# 🎤 Guión Oficial de Presentación y Defensa del Proyecto
## AgendEx · Sistema de Calendarización y Control de Evaluaciones Escolares
### Liceos SOFOFA · Liceo Industrial Bicentenario RBL
**Proyecto Final de Desarrollo de Software (Proyecto Yuyito)**  
*Estructurado para obtener el 100% (Excelente - 12 puntos) en todos los criterios de la Rúbrica Parte 1 y Parte 2.*

---

## 📋 Estructura General de la Exposición (15 a 20 minutos)

| Bloque | Tema | Responsable Sugerido | Duración Estimada |
| :---: | :--- | :---: | :---: |
| **1** | Introducción, Contexto y Definición del Problema | Integrante 1 | 3 min |
| **2** | Objetivos del Proyecto y Solución Tecnológica | Integrante 2 | 3 min |
| **3** | Casos de Uso, Actores y Demostración en Vivo | Integrante 3 | 5 min |
| **4** | Modelo Relacional y Procedimientos Almacenados | Integrante 4 (o rotativo) | 4 min |
| **5** | Calidad, Evidencia de Pruebas y Uso Responsable de IA | Todos | 2 min |
| **6** | Ronda de Preguntas Técnicas de la Comisión | Defensa Individual | 5 min |

---

## 🎙️ Bloque 1: Introducción, Contexto y Problema

### Diálogo para el Integrante 1:
> *"Buenos días, estimados profesores de la comisión evaluadora. Hoy tenemos el agrado de presentar nuestro proyecto final de desarrollo de software: **AgendEx**, un sistema diseñado a la medida de la realidad académica y formativa de nuestro establecimiento, el **Liceo Industrial Bicentenario RBL**, perteneciente a la red de **Liceos SOFOFA**.*
>
> *Para comprender la relevancia de este software, es fundamental entender el **contexto**: en un liceo técnico-profesional con especialidades como Programación, Electricidad y Mecánica, los estudiantes cursan simultáneamente módulos de especialidad técnica y asignaturas de formación general. Esto genera un alto volumen de instrumentos de evaluación.*
>
> *¿Cuál fue la **problemática detectada**?*
> 1. *La falta de visibilidad centralizada entre los distintos departamentos provocaba que un mismo curso llegara a tener 3 o 4 evaluaciones en un mismo día.*
> 2. *La sobrecarga cognitiva y estrés en los estudiantes, perjudicando su rendimiento académico y aumentando la deserción o inasistencia.*
> 3. *Descontrol en la toma de asistencia a pruebas y desajuste en las evaluaciones recuperativas: no existía un mecanismo automático que diferenciara entre quien faltó injustificadamente (quien reglamentariamente debe rendir al **70% de exigencia**) versus quien faltó con certificado médico o salida pedagógica oficial (quien debe rendir con el **60% regular**).*
>
> *Los usuarios directamente afectados eran los estudiantes, los profesores titulares, Inspectoría General y la Unidad Técnico Pedagógica (UTP)."*

---

## 🎯 Bloque 2: Objetivos y Solución Tecnológica

### Diálogo para el Integrante 2:
> *"Frente a esta problemática, nos trazamos **objetivos claros y medibles**:*
> - *Garantizar el cumplimiento automatizado del **100% de la Regla Institucional de Oro**: ningún curso puede tener más de **2 evaluaciones programadas en un mismo día**.*
> - *Establecer trazabilidad total de asistencia a evaluaciones con cierre oficial en sala por parte del docente.*
> - *Centralizar la potestad de Inspectoría General para acreditar licencias médicas y salidas pedagógicas, sincronizando automáticamente las pruebas recuperativas.*
> - *Proporcionar un semáforo de carga académica mensual para que UTP pueda prevenir sobrecargas antes de que ocurran.*
>
> *Nuestra **Solución Tecnológica (AgendEx)** fue desarrollada utilizando una arquitectura cliente-servidor robusta y ligera:*
> - * **Backend**: Desarrollado en **Python con el framework Flask**, aplicando un patrón modular limpio y eficiente.*
> - * **Base de Datos**: Motor relacional **MySQL**, normalizado en Tercera Forma Normal (3FN), con restricciones de integridad referencial y procedimientos almacenados para las reglas de negocio críticas.*
> - * **Frontend**: Diseñado con **HTML5 semántico, Bootstrap 5 y JavaScript ES6**, garantizando una interfaz intuitiva, moderna y responsiva compatible con computadores y celulares.*
>
> *¿Por qué resuelve el problema? Porque digitaliza las reglas del colegio en el código: ningún profesor puede agendar una 3° prueba aunque quiera, y ningún docente puede alterar una lista una vez cerrada, devolviendo la confianza y el orden al proceso escolar."*

---

## 🖥️ Bloque 3: Casos de Uso y Demostración en Vivo

### Diálogo para el Integrante 3 (Acompañado de la pantalla del software):
> *"A continuación, demostraremos los principales **Casos de Uso e interacciones entre los 4 actores del sistema**:*
>
> 1. ***Demostración Profesor (Calendarización con Regla de Oro)***:
>    *Iniciamos sesión como el profesor Antonio Velásquez. Como pueden observar, el formulario solo le muestra sus módulos asignados (Programación Java, Base de Datos). Vamos a intentar agendar una prueba en una fecha donde ya hay 2 pruebas registradas. Como ven, el sistema inmediatamente bloquea la solicitud y avisa que el cupo diario está completo.*
>
> 2. ***Demostración Pase de Lista Oficial***:
>    *Entramos a una evaluación del día de hoy. El profesor pasa lista: un alumno presente, uno con inasistencia injustificada y otro con salida pedagógica. Al presionar 'Guardar Asistencia', la lista queda **cerrada y sellada con candado**. El profesor ya no puede manipularla, garantizando la inmutabilidad de la información.*
>
> 3. ***Demostración Inspectoría General***:
>    *Cambiamos a la sesión de Inspectoría con Claudia Díaz. Inspectoría accede a la evaluación y el sistema le muestra **exclusivamente a los alumnos ausentes**. El apoderado presenta la licencia médica: Inspectoría ingresa el folio médico y guarda. Automáticamente, el sistema reclasifica al estudiante y rebaja la exigencia de su prueba recuperativa del 70% al 60%.*
>
> 4. ***Demostración UTP y Alumno***:
>    *En el panel de UTP observamos el mapa de calor y el informe de carga mensual. Y finalmente, desde el perfil del estudiante, este puede consultar con total transparencia sus fechas de rendición y la exigencia exacta de sus pruebas."*

---

## 🗄️ Bloque 4: Modelo Relacional y Procedimientos Almacenados

### Diálogo para el Integrante 4 (Explicación Técnica para la Comisión):
> *"Para garantizar la integridad y escalabilidad del sistema, diseñamos un **Modelo Relacional normalizado en Tercera Forma Normal (3FN)**:*
>
> - * **Cursos y Asignaturas**: Tablas maestras independientes, evitando redundancias en los nombres y códigos de las especialidades.*
> - * **Profesores y Usuarios**: Separación de las credenciales de autenticación (`usuarios`) de los datos académicos del docente (`profesores`), implementando control de acceso basado en roles (RBAC).*
> - * **Evaluaciones**: Tabla central vinculada mediante claves foráneas con `cursos`, `asignaturas` y `profesores`. Cuenta con índices compuestos en `(curso_id, fecha)` para optimizar las consultas de disponibilidad en tiempo récord.*
> - * **Asistencia y Recuperaciones**: La tabla `asistencia_evaluaciones` cuenta con una restricción única `UNIQUE KEY (evaluacion_id, alumno_id)`, impidiendo duplicados lógicos, y claves foráneas con eliminación en cascada (`ON DELETE CASCADE`).*
>
> *Asimismo, para dar estricto cumplimiento a la rúbrica de software, implementamos **Procedimientos Almacenados en MySQL**:*
> 1. *`sp_verificar_cupo_evaluacion`: Procedimiento que recibe el ID del curso y la fecha, retornando el total de pruebas y un flag de disponibilidad (`0` o `1`). Al ejecutarse directamente en el motor de base de datos, reduce el tráfico de red y garantiza una respuesta inmediata.*
> 2. *`sp_registrar_asistencia_estudiante`: Procedimiento que gestiona la transacción atómica: actualiza la asistencia y, si el alumno faltó, inserta o actualiza la citación en la tabla `recuperaciones`, calculando en el servidor si corresponde 60% (justificado/salida) o 70% (injustificada).*
> 3. *`sp_resumen_carga_curso`: Calcula el acumulado mensual de evaluaciones de un curso para activar el semáforo pedagógico de sobrecarga académica.*
>
> *Estos procedimientos aseguran que la lógica de negocio crítica resida protegida dentro del propio motor relacional."*

---

## 🛡️ Bloque 5: Calidad, Pruebas y Uso Responsable de IA

### Diálogo para el cierre grupal:
> *"En materia de **Calidad del Código y Aseguramiento (QA)**:*
> - *Diseñamos y ejecutamos una matriz de **10 casos de prueba formales**, cubriendo desde la prevención de inyección SQL mediante consultas parametrizadas, hasta pruebas de estrés en la navegación de calendarios y persistencia de estados de asistencia.*
> - *Cada defecto detectado durante el desarrollo (como la normalización de estados de inasistencias) fue documentado y corregido rigurosamente.*
>
> *Respecto al **Uso Responsable de Inteligencia Artificial**:*
> - *Como equipo técnico, utilizamos herramientas de Inteligencia Artificial (Google AI Studio) como un entorno asistido de arquitectura, optimización y diseño.*
> - *Lejos de ser una caja negra, demostramos **dominio total de cada componente**: entendemos la arquitectura relacional, el flujo de solicitudes HTTP en Flask, la manipulación del DOM en JavaScript y las sentencias SQL de nuestros procedimientos almacenados.*
>
> *Con esto damos por concluida nuestra presentación y quedamos a disposición de la comisión para responder cualquier consulta técnica. Muchas gracias."*

---

## 💡 Bloque 6: Banco de Preguntas Técnicas de la Comisión (Defensa Individual)

Aquí tienen las respuestas exactas y profesionales ante las preguntas más probables de los profesores evaluadores:

### Pregunta 1: *"¿Por qué utilizaron MySQL y no una base de datos NoSQL como MongoDB?"*
- **Respuesta modelo**: *"Elegimos MySQL porque el dominio del problema es estrictamente relacional. Necesitamos garantizar **integridad referencial** (un alumno no puede tener asistencia a una evaluación que no existe) y **cumplimiento de propiedades ACID** (atomicidad, consistencia, aislamiento y durabilidad). Las relaciones entre profesores, asignaturas, cursos y evaluaciones exigen claves foráneas y restricciones únicas que los motores relacionales manejan con máxima fiabilidad."*

### Pregunta 2: *"¿Cómo garantizan que dos profesores no agenden una prueba al mismo tiempo superando el tope de 2?"*
- **Respuesta modelo**: *"La validación se realiza en dos capas: primero en el frontend con una llamada asíncrona a la API de disponibilidad (`/evaluaciones/api/disponibilidad`), y segundo, de forma autoritativa en el backend antes de realizar el `INSERT`, apoyado por el procedimiento almacenado `sp_verificar_cupo_evaluacion`. Si ya existen 2 pruebas, la transacción es rechazada inmediatamente."*

### Pregunta 3: *"¿Por qué los inspectores no pasan la lista de asistencia inicial?"*
- **Respuesta modelo**: *"Por diseño pedagógico e institucional: en el aula, quien tiene el contacto directo y visual con los estudiantes durante la rendición es el profesor titular. La labor de Inspectoría General no es pasar lista de sala, sino ejercer el rol de ministro de fe administrativa para recepcionar certificados médicos oficiales o autorizaciones de salida pedagógica, acreditándolos en el sistema para rebajar la exigencia de la prueba recuperativa del 70% al 60%."*

### Pregunta 4: *"¿Cómo previenen ataques de inyección SQL en el sistema?"*
- **Respuesta modelo**: *"En todo el código de Python Flask utilizamos **consultas parametrizadas (Prepared Statements)** mediante la librería PyMySQL, pasando los valores como tuplas `%s` separadas de la estructura de la consulta. Esto asegura que el motor de base de datos trate los datos del usuario como literales puros y no como código ejecutable, neutralizando completamente la inyección SQL."*

### Pregunta 5: *"¿Qué diferencia existe entre un DELETE RESTRICT y un DELETE CASCADE en su modelo?"*
- **Respuesta modelo**: *"Aplicamos `RESTRICT` en tablas estructurales: por ejemplo, no se puede eliminar un curso si aún contiene alumnos registrados. En cambio, aplicamos `CASCADE` en tablas transaccionales: si una evaluación en borrador es eliminada por UTP, sus registros de asistencia y citaciones asociadas se eliminan en cascada para evitar datos huérfanos que corrompan los reportes."*
