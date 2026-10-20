# 🧪 Plan y Evidencia de Pruebas de Software (QA)
## AgendEx · Sistema de Evaluaciones Escolares
### Liceo Industrial Bicentenario RBL · Liceos SOFOFA
*Documentación técnica del proceso de control de calidad, matriz de pruebas ejecutadas, resultados y corrección de errores.*

---

## 1. Estrategia y Alcance de Pruebas

Para garantizar la estabilidad, seguridad y coherencia del sistema desarrollado, se aplicó una estrategia de pruebas que abarca:
1. **Pruebas Funcionales (Caja Negra)**: Verificación de las reglas de negocio institucionales (límite de 2 pruebas diarias, cálculo de exigencias 60%/70%, control de acceso por roles).
2. **Pruebas de Integración Aplicación-BD**: Validación de integridad referencial, disparadores de procedimientos almacenados (`sp_verificar_cupo_evaluacion`, `sp_registrar_asistencia_estudiante`) y transacciones en MySQL.
3. **Pruebas de Seguridad y Validaciones**: Bloqueo de rutas no autorizadas por perfil, escape de parámetros contra SQL Injection y sanitización de formularios.
4. **Pruebas de Regresión**: Verificación de funcionalidades previas tras corregir defectos reportados.

---

## 2. Matriz de Casos de Prueba (Test Cases)

| ID | Módulo / Función | Datos de Entrada | Resultado Esperado | Resultado Obtenido | Estado |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **CP-01** | **Autenticación por Rol** | Login con credenciales válidas de Profesor, UTP, Inspector y Alumno. | Redirección al panel correspondiente con permisos específicos de cada rol. | Acceso concedido según perfil. El profesor ve sus materias, inspectoría ve justificaciones y el alumno su calendario personal. | **APROBADO** |
| **CP-02** | **Regla de Oro (Límite 2 pruebas/día)** | Intentar registrar una 3° evaluación para el curso 4°G en una fecha que ya cuenta con 2 pruebas. | El sistema rechaza la inserción, emite alerta de "Límite máximo alcanzado (2 evaluaciones diarias)" e impide el guardado. | Alerta visual activada en servidor y cliente. La evaluación no se crea en la base de datos. | **APROBADO** |
| **CP-03** | **Filtro Docente de Asignaturas** | Profesor Antonio Velásquez ingresa a formulario de creación de evaluación. | El selector de asignaturas despliega únicamente sus módulos asignados (M5, M6, M7) y cursos 3°G y 4°G. | Se listan exclusivamente las materias del profesor sin mostrar módulos de otros colegas. | **APROBADO** |
| **CP-04** | **Pase de Lista con Salida Pedagógica y Ausencia** | En curso 4°G con 3 alumnos: 1 asistente (✅), 1 con salida pedagógica (🚌) y 1 inasistencia (❌). | Se guarda el registro de asistencia sin transformar todos a presentes. Se cierra la lista para el docente. | Asistencia guardada correctamente con cada estado independiente. La lista cambia a estado [Cerrada]. | **APROBADO** |
| **CP-05** | **Generación Automática de Recuperativas** | Tras pasar lista con 1 salida y 1 inasistencia injustificada. | Se crean 2 citaciones a prueba recuperativa: una con **60% de exigencia** (salida pedagógica) y otra con **70% de exigencia** (injustificada). | Citaciones creadas automáticamente a 7 días plazo con exigencia del 60% y 70% respectivamente. | **APROBADO** |
| **CP-06** | **Acreditación Médica por Inspectoría** | Inspectoría acredita certificado médico a alumno con inasistencia injustificada previa. | El estado del alumno cambia a "Justificado" y la exigencia de su prueba recuperativa baja del **70% al 60%**. | Estado actualizado a "Justificado (Inspectoría)" y exigencia ajustada automáticamente al 60%. | **APROBADO** |
| **CP-07** | **Inmutabilidad de Lista Cerrada** | Profesor titular intenta volver a pasar lista o editar una evaluación que ya tiene asistencia guardada. | El sistema bloquea el formulario de asistencia e informa que la nómina está cerrada y bajo potestad de Inspectoría. | Controles de edición bloqueados en modo solo lectura con candado de seguridad. | **APROBADO** |
| **CP-08** | **Navegación del Calendario Escolar** | Cambiar entre meses anteriores y posteriores (ej. Septiembre, Octubre, Noviembre 2026). | Los botones `← Mes Anterior` y `Mes Siguiente →` calculan correctamente los parámetros de año y mes sin errores 404 ni 500. | Navegación fluida y cálculo exacto de días del mes. | **APROBADO** |
| **CP-09** | **Cálculo de Carga Académica Mensual** | Consulta de cursos con 6 o más evaluaciones mensuales. | Se marca con insignia de "Alta Carga" (badge rojo) cuando el acumulado mensual es >= 6 pruebas. | Cálculo exacto mediante consulta SQL y procedimiento almacenado `sp_resumen_carga_curso`. | **APROBADO** |
| **CP-10** | **Integridad Referencial en BD** | Eliminación en cascada de asistencias y recuperaciones si UTP elimina una prueba no cerrada. | Las tablas secundarias limpian los registros dependientes sin dejar registros huérfanos. | Integridad referencial preservada mediante claves foráneas con `ON DELETE CASCADE`. | **APROBADO** |

---

## 3. Registro Histórico de Defectos y Correcciones (Bug Tracking)

| ID Defecto | Descripción del Problema | Causa Raíz Detectada | Solución Implementada | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **BUG-01** | Todos los alumnos aparecían como "Presentes" al guardar asistencia en modo local, aun habiendo marcado inasistencias o salidas pedagógicas. | En la plantilla HTML y en el controlador de Python, si la clave del formulario o la columna en MySQL no venía normalizada, el código aplicaba un `fallback` ciego a `'presente'`. | 1. Se normalizó la lectura de `request.form` con soporte para prefijos `estado_X`.<br>2. Se corrigió el mapeo de asistencias para asociar tanto enteros como cadenas (`int(id)` y `str(id)`).<br>3. Se aseguró que si el estado es `'salida'` o `'injustificada'`, se mantenga fielmente tanto en BD como en la vista. | **CORREGIDO Y VERIFICADO** |
| **BUG-02** | Botón no solicitado "Ver en Calendario" aparecía dentro del detalle de evaluación causando confusión. | Elemento visual extra agregado fuera del alcance del requerimiento. | Se eliminó el botón redundante en `templates/evaluaciones/detalle.html`, dejando únicamente los botones esenciales (Volver, Editar si corresponde). | **CORREGIDO Y VERIFICADO** |
| **BUG-03** | Error en navegación del reporte de calendario mensual en Python Flask (`prevMes`, `nextMes` no definidos). | Las variables de navegación entre meses no eran calculadas ni enviadas a `render_template` en `app.py`. | Se implementó el cálculo de meses y años de transición (ej. Diciembre → Enero) y se enviaron formalmente al template Jinja2. | **CORREGIDO Y VERIFICADO** |
| **BUG-04** | En el formulario de nueva evaluación aparecían todas las asignaturas del liceo para cualquier profesor. | Faltaba la vinculación del ID del docente con su mapa oficial de especialidad en el liceo. | Se implementó el filtrado oficial por docente (`PROFESORES_ASIGNACIONES`), de modo que cada profesor solo puede seleccionar sus materias y cursos asignados. | **CORREGIDO Y VERIFICADO** |
| **BUG-05** | Alumnos con salida pedagógica quedaban citados al 70% de exigencia en lugar del 60% reglamentario. | En la lógica de inserción de recuperaciones se clasificaba cualquier ausencia no médica bajo la categoría genérica de "injustificada". | Se diferenció el estado `salida` pedagógica, asignándole el **60.00% de exigencia regular** tanto en la tabla de recuperaciones como en el procedimiento almacenado. | **CORREGIDO Y VERIFICADO** |

---

## 4. Conclusión del Proceso de Pruebas
El software AgendEx ha superado el 100% de los casos de prueba establecidos en la matriz. Se evidencia una arquitectura sólida, con validaciones robustas tanto a nivel de frontend, backend y base de datos relacional MySQL, cumpliendo satisfactoriamente los estándares de calidad para la presentación final.
