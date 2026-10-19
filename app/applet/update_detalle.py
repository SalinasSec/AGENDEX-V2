import sys

with open('views/evaluaciones/detalle.ejs', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "<% } else if (current_user.rol === 'inspe') { %>"
idx1 = text.find(start_marker, 2000)
end_marker = "<% } else if (esProfeObservador) { %>"
idx2 = text.find(end_marker, idx1)

if idx1 == -1 or idx2 == -1:
    print(f"Error finding markers: idx1={idx1}, idx2={idx2}")
    sys.exit(1)

inspector_block = """<% } else if (current_user.rol === 'inspe') { %>
                    <!-- ========================================== -->
                    <!-- VISTA ESPECÍFICA PARA INSPECTORÍA GENERAL  -->
                    <!-- ========================================== -->
                    <div class="alert alert-light border border-warning-subtle small mb-3 py-2">
                        <i class="bi bi-shield-check text-warning me-1"></i>
                        <strong>Atribución de Inspectoría General:</strong> La asistencia del curso la pasa el profesor titular. Inspectoría acredita justificativos médicos o salidas pedagógicas a los estudiantes ausentes para rebajar la exigencia de su prueba recuperativa (<strong>70% sin justificar &rarr; 60% justificado</strong>).
                    </div>

                    <% if (!ev.asistencia_guardada) { %>
                    <div class="text-center py-5 bg-light rounded border border-dashed my-3">
                        <i class="bi bi-clock-history text-warning fs-1 d-block mb-2"></i>
                        <h6 class="fw-bold mb-1">Pase de lista pendiente por el docente</h6>
                        <p class="text-muted small mb-0 px-3" style="max-width: 500px; margin: 0 auto;">
                            El profesor titular (<strong><%= ev.profesor ? ev.profesor.nombre_completo : 'Docente' %></strong>) aún no ha guardado la lista de asistencia en sala. Una vez que el docente registre la asistencia, los estudiantes ausentes aparecerán aquí para que puedas acreditar sus certificados médicos.
                        </p>
                    </div>

                    <h6 class="fw-bold small text-muted text-uppercase mt-4 mb-2">Nómina del curso (<%= alumnos.length %> alumnos)</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th style="width: 50px;">#</th>
                                    <th>Estudiante</th>
                                    <th>RUT</th>
                                    <th>Estado Asistencia</th>
                                </tr>
                            </thead>
                            <tbody>
                                <% alumnos.forEach((alumno, idx) => { %>
                                <tr>
                                    <td class="text-muted small"><%= idx + 1 %></td>
                                    <td><strong><%= alumno.nombre_completo %></strong></td>
                                    <td class="text-muted small font-monospace"><%= alumno.rut %></td>
                                    <td><span class="badge bg-light text-muted border"><i class="bi bi-clock me-1"></i>Pendiente por docente</span></td>
                                </tr>
                                <% }) %>
                            </tbody>
                        </table>
                    </div>

                    <% } else if (alumnosAfectados.length === 0) { %>
                    <div class="text-center py-5 bg-light rounded border border-dashed my-3">
                        <i class="bi bi-check-circle-fill text-success fs-1 d-block mb-2"></i>
                        <h6 class="fw-bold mb-1 text-success">¡Asistencia Completa en Sala!</h6>
                        <p class="text-muted small mb-0 px-3" style="max-width: 500px; margin: 0 auto;">
                            Todos los estudiantes convocados del curso (<%= alumnos.length %> alumnos) asistieron a la evaluación. No hay ausencias que requieran justificación médica en Inspectoría.
                        </p>
                    </div>

                    <% } else { %>
                    <!-- Formulario de Acreditación de Justificaciones Médicas para Alumnos Ausentes -->
                    <form method="POST" action="/evaluaciones/<%= ev.id %>/asistencia">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th style="width: 28%;">Estudiante Ausente</th>
                                        <th style="width: 34%;">Condición de Inasistencia</th>
                                        <th style="width: 26%;">Folio / Certificado Médico</th>
                                        <th class="text-center" style="width: 12%;">Exigencia</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <% alumnosAfectados.forEach(alumno => { %>
                                    <% 
                                        const asist = asistencias[alumno.id]; 
                                        let estadoActual = 'injustificada';
                                        if (asist) {
                                            let st = asist.estado_asistencia;
                                            if (Array.isArray(st)) st = st[0];
                                            if (st) estadoActual = st;
                                            else if (asist.justificado) estadoActual = 'justificado';
                                            else estadoActual = 'injustificada';
                                        }
                                        let mot = asist ? asist.motivo : '';
                                        if (Array.isArray(mot)) mot = mot[0];
                                    %>
                                    <tr>
                                        <td>
                                            <div class="fw-semibold text-dark"><%= alumno.nombre_completo %></div>
                                            <div class="text-muted small font-monospace"><%= alumno.rut %></div>
                                        </td>
                                        <td>
                                            <select name="estado_<%= alumno.id %>" class="form-select form-select-sm select-estado" data-alumno-id="<%= alumno.id %>">
                                                <option value="injustificada" <%= estadoActual === 'injustificada' ? 'selected' : '' %>>❌ Inasistencia Injustificada (70%)</option>
                                                <option value="justificado" <%= (estadoActual === 'justificado' || estadoActual === 'licencia') ? 'selected' : '' %>>🏥 Justificado Médico / Licencia (60%)</option>
                                                <option value="salida" <%= estadoActual === 'salida' ? 'selected' : '' %>>🚌 Salida Pedagógica Oficial (60%)</option>
                                            </select>
                                        </td>
                                        <td>
                                            <input type="text" name="motivo_<%= alumno.id %>" class="form-control form-control-sm"
                                                   placeholder="N° Folio o documento médico..."
                                                   value="<%= mot || '' %>"
                                                   id="motivo_<%= alumno.id %>">
                                        </td>
                                        <td class="text-center" id="badge_exigencia_<%= alumno.id %>">
                                            <% if (estadoActual === 'injustificada') { %>
                                            <span class="badge bg-danger" title="70% de exigencia">70%</span>
                                            <% } else { %>
                                            <span class="badge bg-success" title="60% regular">60%</span>
                                            <% } %>
                                        </td>
                                    </tr>
                                    <% }) %>
                                </tbody>
                            </table>
                        </div>

                        <div class="d-flex flex-wrap justify-content-between align-items-center mt-3 pt-3 border-top gap-2">
                            <small class="text-muted"><i class="bi bi-shield-check me-1"></i>Al guardar, las pruebas recuperativas se actualizan automáticamente al 60% o 70%.</small>
                            <button type="submit" class="btn btn-warning px-4 fw-semibold shadow-xs">
                                <i class="bi bi-check-lg me-1"></i>Guardar Justificaciones
                            </button>
                        </div>
                    </form>
                    <% } %>
"""

text = text[:idx1] + inspector_block + text[idx2:]

with open('views/evaluaciones/detalle.ejs', 'w', encoding='utf-8') as f:
    f.write(text)

print("views/evaluaciones/detalle.ejs updated successfully.")
