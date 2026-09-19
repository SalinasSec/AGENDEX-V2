// In-memory data store with realistic seed data matching AgendEx

export const ROLES = {
  utp: "UTP",
  profe: "Profesor",
  inspe: "Inspectoría",
  alumno: "Alumno",
};

export const EXIGENCIA_JUSTIFICADO = 60.00;
export const EXIGENCIA_NO_JUSTIFICADO = 70.00;

class Store {
  constructor() {
    this.init();
  }

  init() {
    // 26 Cursos del Liceo Industrial Bicentenario RBL
    // 2° Medios (2A - 2F) con sistema de Aprestos (Rotación técnica en Electricidad, Electrónica y Programación)
    // 3° y 4° Medios por especialidad técnica
    this.cursos = [
      { id: 1, nombre: '1A', nivel: 'Media', especialidad: 'Formación General' },
      { id: 2, nombre: '1B', nivel: 'Media', especialidad: 'Formación General' },
      { id: 3, nombre: '1C', nivel: 'Media', especialidad: 'Formación General' },
      { id: 4, nombre: '1D', nivel: 'Media', especialidad: 'Formación General' },
      { id: 5, nombre: '1E', nivel: 'Media', especialidad: 'Formación General' },
      { id: 6, nombre: '1F', nivel: 'Media', especialidad: 'Formación General' },
      { id: 7, nombre: '2A', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 8, nombre: '2B', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 9, nombre: '2C', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 10, nombre: '2D', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 11, nombre: '2E', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 12, nombre: '2F', nivel: 'Media', especialidad: 'Aprestos Técnicos (Rotación Electr./Electr./Prog.)' },
      { id: 13, nombre: '3A', nivel: 'Electricidad', especialidad: 'Electricidad' },
      { id: 14, nombre: '3B', nivel: 'Electricidad', especialidad: 'Electricidad' },
      { id: 15, nombre: '3C', nivel: 'Electronica', especialidad: 'Electrónica' },
      { id: 16, nombre: '3D', nivel: 'Electronica', especialidad: 'Electrónica' },
      { id: 17, nombre: '3E', nivel: 'Telecomunicación', especialidad: 'Telecomunicaciones' },
      { id: 18, nombre: '3F', nivel: 'Telecomunicación', especialidad: 'Telecomunicaciones' },
      { id: 19, nombre: '3G', nivel: 'Programacion', especialidad: 'Programación' },
      { id: 20, nombre: '4A', nivel: 'Electricidad', especialidad: 'Electricidad' },
      { id: 21, nombre: '4B', nivel: 'Electricidad', especialidad: 'Electricidad' },
      { id: 22, nombre: '4C', nivel: 'Electronica', especialidad: 'Electrónica' },
      { id: 23, nombre: '4D', nivel: 'Electronica', especialidad: 'Electrónica' },
      { id: 24, nombre: '4E', nivel: 'Telecomunicación', especialidad: 'Telecomunicaciones' },
      { id: 25, nombre: '4F', nivel: 'Telecomunicación', especialidad: 'Telecomunicaciones' },
      { id: 26, nombre: '4G', nivel: 'Programacion', especialidad: 'Programación' },
    ];
    this.cursoIdSeq = 27;

    // Asignaturas y Módulos de Especialidad Técnico Profesional
    this.asignaturas = [
      { id: 1, nombre: "Lenguaje y Comunicación", color: "#2F6F4E", tipo: "plan_comun" },
      { id: 2, nombre: "Matemática", color: "#14213D", tipo: "plan_comun" },
      { id: 3, nombre: "Historia", color: "#A87F2C", tipo: "plan_comun" },
      { id: 4, nombre: "Inglés", color: "#2C5F7A", tipo: "plan_comun" },
      { id: 5, nombre: "Educación Física", color: "#A5332A", tipo: "plan_comun" },
      { id: 6, nombre: "Ciencias Naturales", color: "#3B7A6B", tipo: "plan_comun" },
      // Módulos Técnico-Profesionales de la Especialidad de Programación
      { id: 7, nombre: "M8: Desarrollo de Aplicaciones Web", color: "#1E3157", tipo: "modulo_tp", codigo: "M8" },
      { id: 8, nombre: "M5: Diseño y Consulta de Base de Datos (DBD)", color: "#4A3B7A", tipo: "modulo_tp", codigo: "M5" },
      { id: 9, nombre: "M6: Programación Orientada a Objetos Java Escritorio (POO)", color: "#006699", tipo: "modulo_tp", codigo: "M6" },
      { id: 10, nombre: "M7: Programación en PL/SQL (ABD)", color: "#8E2800", tipo: "modulo_tp", codigo: "M7" },
      // Taller de Aprestos Técnicos para 2° Medio
      { id: 11, nombre: "Taller Aprestos Técnicos (Rotación Electricidad/Electrónica/Prog)", color: "#D97706", tipo: "aprestos", codigo: "APRESTOS" },
    ];
    this.asignaturaIdSeq = 12;

    // Profesores con asignación real por cursos y módulos
    this.profesores = [
      {
        id: 1,
        nombre: "Marcela",
        apellido: "Rubio",
        email: "marcela.rubio@liceorbl.cl",
        materia: "M8: Desarrollo de Aplicaciones Web",
        cargo_extra: "Profesora Jefe 4°G",
        es_jefatura: true,
        curso_jefatura_id: 26, // 4G
        cursos_asignados: [19, 26], // Solo 3G y 4G
        asignaturas_asignadas: [7], // M8
        nombre_completo: "Marcela Rubio"
      },
      {
        id: 2,
        nombre: "Antonio",
        apellido: "Velásquez",
        email: "antonio.velasquez@liceorbl.cl",
        materia: "M5 DBD / M6 POO / M7 ABD",
        cargo_extra: "Profesor Jefe 3°G",
        es_jefatura: true,
        curso_jefatura_id: 19, // 3G
        cursos_asignados: [19, 26], // Solo 3G y 4G
        asignaturas_asignadas: [8, 9, 10], // M5, M6, M7
        nombre_completo: "Antonio Velásquez"
      },
      {
        id: 3,
        nombre: "Carolina",
        apellido: "Reyes",
        email: "c.reyes@liceo.cl",
        materia: "Matemática",
        cargo_extra: "Docente Plan Común",
        cursos_asignados: [1, 2, 7, 12, 19, 26],
        asignaturas_asignadas: [2],
        nombre_completo: "Carolina Reyes"
      },
      {
        id: 4,
        nombre: "Patricio",
        apellido: "Muñoz",
        email: "p.munoz@liceo.cl",
        materia: "Lenguaje y Comunicación",
        cargo_extra: "Docente Plan Común",
        cursos_asignados: [1, 2, 7, 8, 19, 26],
        asignaturas_asignadas: [1],
        nombre_completo: "Patricio Muñoz"
      },
      {
        id: 5,
        nombre: "Valentina",
        apellido: "Soto",
        email: "v.soto@liceo.cl",
        materia: "Historia",
        cargo_extra: "Docente Plan Común",
        cursos_asignados: [1, 2, 7, 19],
        asignaturas_asignadas: [3],
        nombre_completo: "Valentina Soto"
      },
      {
        id: 6,
        nombre: "Diego",
        apellido: "Fuentes",
        email: "d.fuentes@liceo.cl",
        materia: "Inglés",
        cargo_extra: "Docente Plan Común",
        cursos_asignados: [1, 7, 19, 26],
        asignaturas_asignadas: [4],
        nombre_completo: "Diego Fuentes"
      },
      {
        id: 7,
        nombre: "Docente",
        apellido: "Aprestos",
        email: "aprestos@liceorbl.cl",
        materia: "Taller Aprestos Técnicos",
        cargo_extra: "Coordinación Rotación 2° Medios",
        cursos_asignados: [7, 8, 9, 10, 11, 12], // 2A a 2F
        asignaturas_asignadas: [11],
        nombre_completo: "Docente Aprestos"
      }
    ];
    this.profesorIdSeq = 8;

    // Alumnos (vinculados a cursos por id)
    // 1A = 1, 2F = 12 (en rotación Aprestos), 3G = 19 (Programación), 4G = 26 (Programación)
    this.alumnos = [
      { id: 1, rut: "20.123.456-1", nombre: "Joaquín", apellido: "Rivas", curso_id: 26 },
      { id: 2, rut: "20.234.567-2", nombre: "Camila", apellido: "Torres", curso_id: 26 },
      { id: 3, rut: "20.345.678-3", nombre: "Bastián", apellido: "Núñez", curso_id: 26 },
      { id: 4, rut: "21.111.222-3", nombre: "Francisca", apellido: "Lara", curso_id: 19 },
      { id: 5, rut: "20.555.666-7", nombre: "Matías", apellido: "González", curso_id: 1 },
      { id: 6, rut: "19.888.999-0", nombre: "Antonia", apellido: "Sepúlveda", curso_id: 12 },
    ];
    this.alumnos.forEach(a => {
      a.nombre_completo = `${a.nombre} ${a.apellido}`;
      a.curso = this.getCurso(a.curso_id);
    });
    this.alumnoIdSeq = 7;

    // Usuarios con credenciales institucionales
    this.usuarios = [
      {
        rut: "19.000.001-1",
        correo: "utp@liceorbl.cl",
        clave: "utp123",
        nombre: "Usuario UTP",
        rol: "utp",
        profesor_id: null,
        alumno_id: null,
        activo: true
      },
      // Profesores de Programación de 3°G y 4°G
      {
        rut: "14.222.333-4",
        correo: "marcela.rubio@liceorbl.cl",
        clave: "profe123",
        nombre: "Marcela Rubio",
        rol: "profe",
        profesor_id: 1,
        alumno_id: null,
        activo: true
      },
      {
        rut: "13.333.444-5",
        correo: "antonio.velasquez@liceorbl.cl",
        clave: "profe123",
        nombre: "Antonio Velásquez",
        rol: "profe",
        profesor_id: 2,
        alumno_id: null,
        activo: true
      },
      {
        rut: "15.111.222-3",
        correo: "carolina.reyes@liceosofofa.cl",
        clave: "profe123",
        nombre: "Carolina Reyes",
        rol: "profe",
        profesor_id: 3,
        alumno_id: null,
        activo: true
      },
      {
        rut: "19.000.002-2",
        correo: "profe@liceosofofa.cl",
        clave: "profe123",
        nombre: "Marcela Rubio (Acceso Rápido)",
        rol: "profe",
        profesor_id: 1,
        alumno_id: null,
        activo: true
      },
      {
        rut: "18.777.888-9",
        correo: "inspe.diaz@liceorbl.cl",
        clave: "inspe123",
        nombre: "Claudia Díaz",
        rol: "inspe",
        profesor_id: null,
        alumno_id: null,
        activo: true
      },
      {
        rut: "19.000.003-3",
        correo: "inspe@liceorbl.cl",
        clave: "inspe123",
        nombre: "Usuario Inspectoria",
        rol: "inspe",
        profesor_id: null,
        alumno_id: null,
        activo: true
      },
      {
        rut: "20.123.456-1",
        correo: "joaquin.rivas@liceorbl.cl",
        clave: "alumno123",
        nombre: "Joaquín Rivas (4°G)",
        rol: "alumno",
        profesor_id: null,
        alumno_id: 1,
        activo: true
      },
      {
        rut: "20.000.004-4",
        correo: "alumno@liceorbl.cl",
        clave: "alumno123",
        nombre: "Usuario Alumno",
        rol: "alumno",
        profesor_id: null,
        alumno_id: 1,
        activo: true
      }
    ];

    // Current date helpers to create dynamic dates around today
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;

    const dateOffset = (days) => {
      const d = new Date(now);
      d.setDate(d.getDate() + days);
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    };

    // Evaluaciones de ejemplo asociadas a la realidad de especialidad y plan común
    this.evaluaciones = [
      {
        id: 1,
        titulo: "Prueba Desarrollo Frontend Web (Vue/React)",
        fecha: todayStr,
        hora: "08:30",
        descripcion: "Construcción de componentes e integración de APIs en entorno frontend.",
        asignatura_id: 7, // M8 Desarrollo de Aplicaciones Web
        curso_id: 26, // 4G (Prof. Jefe Marcela Rubio)
        profesor_id: 1, // Marcela Rubio
        created_at: new Date()
      },
      {
        id: 2,
        titulo: "Prueba Consultas SQL y Normalización Relacional",
        fecha: todayStr,
        hora: "10:15",
        descripcion: "Consultas multi-tabla JOIN, agrupamientos y subconsultas en MySQL/PostgreSQL.",
        asignatura_id: 8, // M5 DBD
        curso_id: 19, // 3G (Prof. Jefe Antonio Velásquez)
        profesor_id: 2, // Antonio Velásquez
        created_at: new Date()
      },
      {
        id: 3,
        titulo: "Evaluación Práctica Java Desktop (POO y Swing)",
        fecha: dateOffset(2),
        hora: "09:45",
        descripcion: "Programación en Java con patrones de herencia, encapsulamiento y ventanas.",
        asignatura_id: 9, // M6 POO
        curso_id: 26, // 4G
        profesor_id: 2, // Antonio Velásquez
        created_at: new Date()
      },
      {
        id: 4,
        titulo: "Prueba Procedimientos y Triggers en PL/SQL",
        fecha: dateOffset(4),
        hora: "11:30",
        descripcion: "Estructuras de control, cursores explícitos y paquetes almacenados en base de datos.",
        asignatura_id: 10, // M7 ABD
        curso_id: 19, // 3G
        profesor_id: 2, // Antonio Velásquez
        created_at: new Date()
      },
      {
        id: 5,
        titulo: "Rotación Técnica: Introducción a Algoritmos y Circuitos",
        fecha: dateOffset(3),
        hora: "10:00",
        descripcion: "Módulo rotativo de aprestos técnicos explorando lógica de programación y electrónica básica.",
        asignatura_id: 11, // Aprestos Técnicos
        curso_id: 12, // 2F (Nivel Media - Rotación Aprestos)
        profesor_id: 7, // Docente Aprestos
        created_at: new Date()
      },
      {
        id: 6,
        titulo: "Control Álgebra y Funciones",
        fecha: dateOffset(5),
        hora: "08:15",
        descripcion: "Ecuaciones de segundo grado y modelamiento matemático.",
        asignatura_id: 2, // Matemática
        curso_id: 1, // 1A
        profesor_id: 3, // Carolina Reyes
        created_at: new Date()
      }
    ];
    this.evaluacionIdSeq = 7;

    // Asistencias iniciales
    this.asistencias = [
      // Para eval 1 (4G, alumnos 1, 2, 3)
      { id: 1, evaluacion_id: 1, alumno_id: 1, presente: true, estado_asistencia: 'presente', motivo: "", justificado: false },
      { id: 2, evaluacion_id: 1, alumno_id: 2, presente: false, estado_asistencia: 'injustificada', motivo: "Inasistencia sin justificar", justificado: false },
      { id: 3, evaluacion_id: 1, alumno_id: 3, presente: true, estado_asistencia: 'presente', motivo: "", justificado: false },
      // Para eval 2 (3G, alumna 4)
      { id: 4, evaluacion_id: 2, alumno_id: 4, presente: false, estado_asistencia: 'justificado', motivo: "Licencia médica acreditada", justificado: true },
    ];
    this.asistenciaIdSeq = 5;

    // Recuperaciones iniciales coherentes con alumnos y evaluaciones de los cursos
    this.recuperaciones = [
      {
        id: 1,
        evaluacion_id: 1, // Eval 1 en 4G
        alumno_id: 2, // Camila Torres (4G)
        fecha_recuperacion: dateOffset(3),
        motivo: "Inasistencia sin justificar a prueba M8",
        tipo_justificacion: "injustificada",
        porcentaje_exigencia: EXIGENCIA_NO_JUSTIFICADO, // 70%
        estado: "pendiente",
        created_at: new Date()
      },
      {
        id: 2,
        evaluacion_id: 2, // Eval 2 en 3G
        alumno_id: 4, // Francisca Lara (3G)
        fecha_recuperacion: dateOffset(4),
        motivo: "Licencia médica acreditada en Inspectoría",
        tipo_justificacion: "medico",
        porcentaje_exigencia: EXIGENCIA_JUSTIFICADO, // 60%
        estado: "pendiente",
        created_at: new Date()
      },
      {
        id: 3,
        evaluacion_id: 1, // Eval 1 en 4G
        alumno_id: 3, // Bastián Núñez (4G)
        fecha_recuperacion: dateOffset(5),
        motivo: "Salida pedagógica autorizada (Olimpiada SOFOFA TP)",
        tipo_justificacion: "salida_pedagogica",
        porcentaje_exigencia: EXIGENCIA_JUSTIFICADO, // 60% (misma exigencia regular)
        estado: "pendiente",
        created_at: new Date()
      }
    ];
    this.recuperacionIdSeq = 4;
  }

  // Helpers
  getCurso(id) {
    return this.cursos.find(c => c.id === Number(id));
  }

  getAsignatura(id) {
    return this.asignaturas.find(a => a.id === Number(id));
  }

  getProfesor(id) {
    const p = this.profesores.find(x => x.id === Number(id));
    if (p && !p.nombre_completo) {
      p.nombre_completo = `${p.nombre} ${p.apellido}`;
    }
    return p;
  }

  getEvaluacionesByProfesor(profesorId) {
    const prof = this.getProfesor(profesorId);
    if (!prof) return [];

    return this.evaluaciones.filter(e => {
      // Si la evaluación fue creada o asignada formalmente a este profesor
      if (e.profesor_id === prof.id) return true;

      // O si pertenece a uno de sus cursos asignados y una de sus asignaturas asignadas
      const tieneCurso = prof.cursos_asignados && prof.cursos_asignados.includes(e.curso_id);
      const tieneAsignatura = prof.asignaturas_asignadas && prof.asignaturas_asignadas.includes(e.asignatura_id);

      return Boolean(tieneCurso && tieneAsignatura);
    });
  }

  getRecuperacionesByProfesor(profesorId) {
    const profEvals = this.getEvaluacionesByProfesor(profesorId);
    const profEvalIds = new Set(profEvals.map(e => e.id));
    return this.recuperaciones.filter(r => profEvalIds.has(r.evaluacion_id));
  }

  getAlumno(id) {
    const a = this.alumnos.find(x => x.id === Number(id));
    if (a && !a.nombre_completo) {
      a.nombre_completo = `${a.nombre} ${a.apellido}`;
      a.curso = this.getCurso(a.curso_id);
    }
    return a;
  }

  getAlumnoById(id) {
    return this.getAlumno(id);
  }

  getAlumnoByRut(rut) {
    const a = this.alumnos.find(x => x.rut === rut);
    if (a && !a.nombre_completo) {
      a.nombre_completo = `${a.nombre} ${a.apellido}`;
      a.curso = this.getCurso(a.curso_id);
    }
    return a;
  }

  getAlumnosByCurso(cursoId) {
    return this.alumnos
      .filter(a => a.curso_id === Number(cursoId))
      .map(a => this.getAlumno(a.id));
  }

  getUsuarioByCorreo(correo) {
    if (!correo) return null;
    const norm = correo.trim().toLowerCase();
    const u = this.usuarios.find(x => x.correo.toLowerCase() === norm);
    if (u) {
      // Ensure password_hash is accessible whether stored as clave or password_hash
      if (!u.password_hash && u.clave) {
        u.password_hash = u.clave;
      }
    }
    return u;
  }

  getEvaluacion(id) {
    const ev = this.evaluaciones.find(x => x.id === Number(id));
    if (ev) {
      return this.enrichEvaluacion(ev);
    }
    return null;
  }

  getEvaluacionById(id) {
    return this.getEvaluacion(id);
  }

  enrichEvaluacion(ev) {
    return {
      ...ev,
      curso: this.getCurso(ev.curso_id) || { nombre: "N/A", nivel: "N/A" },
      asignatura: this.getAsignatura(ev.asignatura_id) || { nombre: "N/A", color: "#3498db" },
      profesor: this.getProfesor(ev.profesor_id) || { nombre_completo: "N/A" }
    };
  }

  enrichRecuperacion(r) {
    const ev = this.getEvaluacion(r.evaluacion_id);
    const alumno = this.getAlumno(r.alumno_id);
    return {
      ...r,
      evaluacion: ev,
      alumno: alumno
    };
  }

  contarEnFecha(curso_id, fecha, exclude_id = null) {
    return this.evaluaciones.filter(e =>
      e.curso_id === Number(curso_id) &&
      e.fecha === fecha &&
      (!exclude_id || e.id !== Number(exclude_id))
    ).length;
  }

  hayLugar(curso_id, fecha, exclude_id = null) {
    return this.contarEnFecha(curso_id, fecha, exclude_id) < 2;
  }

  crearEvaluacion(data) {
    const id = this.evaluacionIdSeq++;
    const ev = {
      id,
      titulo: data.titulo,
      fecha: data.fecha,
      hora: data.hora || null,
      curso_id: Number(data.curso_id),
      asignatura_id: Number(data.asignatura_id),
      profesor_id: Number(data.profesor_id),
      descripcion: data.descripcion || '',
      created_at: new Date()
    };
    this.evaluaciones.push(ev);
    return this.enrichEvaluacion(ev);
  }

  actualizarEvaluacion(id, data) {
    const idx = this.evaluaciones.findIndex(e => e.id === Number(id));
    if (idx !== -1) {
      this.evaluaciones[idx] = {
        ...this.evaluaciones[idx],
        ...data,
        id: Number(id)
      };
      return this.enrichEvaluacion(this.evaluaciones[idx]);
    }
    return null;
  }

  eliminarEvaluacion(id) {
    this.evaluaciones = this.evaluaciones.filter(e => e.id !== Number(id));
    this.asistencias = this.asistencias.filter(a => a.evaluacion_id !== Number(id));
    this.recuperaciones = this.recuperaciones.filter(r => r.evaluacion_id !== Number(id));
  }

  getAsistenciasByAlumno(alumnoId) {
    return this.asistencias.filter(a => a.alumno_id === Number(alumnoId));
  }

  getAsistenciasByEvaluacion(evalId) {
    return this.asistencias.filter(a => a.evaluacion_id === Number(evalId));
  }

  getAsistencia(alumnoId, evalId) {
    return this.asistencias.find(a => a.alumno_id === Number(alumnoId) && a.evaluacion_id === Number(evalId)) || null;
  }

  guardarAsistencia({ alumno_id, evaluacion_id, presente, motivo, justificado, estado_asistencia }) {
    const aId = Number(alumno_id);
    const eId = Number(evaluacion_id);
    const existingIdx = this.asistencias.findIndex(a => a.alumno_id === aId && a.evaluacion_id === eId);

    // Derive estado_asistencia if not provided
    let estado = estado_asistencia;
    if (!estado) {
      if (presente) estado = 'presente';
      else if (justificado) estado = 'justificado';
      else estado = 'injustificada';
    }

    const isPresente = estado === 'presente';
    const isJustificado = (estado === 'justificado' || estado === 'salida');

    if (existingIdx !== -1) {
      this.asistencias[existingIdx] = {
        ...this.asistencias[existingIdx],
        presente: isPresente,
        estado_asistencia: estado,
        motivo: isPresente ? '' : (motivo || ''),
        justificado: isPresente ? false : isJustificado
      };
      return this.asistencias[existingIdx];
    } else {
      const nueva = {
        id: this.asistenciaIdSeq++,
        alumno_id: aId,
        evaluacion_id: eId,
        presente: isPresente,
        estado_asistencia: estado,
        motivo: isPresente ? '' : (motivo || ''),
        justificado: isPresente ? false : isJustificado
      };
      this.asistencias.push(nueva);
      return nueva;
    }
  }

  getRecuperacionesByAlumno(alumnoId) {
    return this.recuperaciones
      .filter(r => r.alumno_id === Number(alumnoId))
      .map(r => this.enrichRecuperacion(r));
  }

  crearRecuperacion(data) {
    const id = this.recuperacionIdSeq++;
    const r = {
      id,
      evaluacion_id: Number(data.evaluacion_id),
      alumno_id: Number(data.alumno_id),
      fecha_recuperacion: data.fecha_recuperacion,
      porcentaje_exigencia: Number(data.porcentaje_exigencia),
      tipo_justificacion: data.tipo_justificacion || 'medico',
      motivo: data.motivo || '',
      estado: 'pendiente',
      created_at: new Date()
    };
    this.recuperaciones.push(r);
    return this.enrichRecuperacion(r);
  }

  actualizarEstadoRecuperacion(id, estado) {
    const r = this.recuperaciones.find(x => x.id === Number(id));
    if (r) {
      r.estado = estado;
      return this.enrichRecuperacion(r);
    }
    return null;
  }

  crearAlumno(data) {
    const id = this.alumnos.length ? Math.max(...this.alumnos.map(a => a.id)) + 1 : 1;
    const a = {
      id,
      rut: data.rut,
      nombre: data.nombre,
      apellido: data.apellido,
      curso_id: Number(data.curso_id),
      nombre_completo: `${data.nombre} ${data.apellido}`
    };
    this.alumnos.push(a);
    return this.getAlumno(id);
  }

  crearCurso(data) {
    const id = this.cursos.length ? Math.max(...this.cursos.map(c => c.id)) + 1 : 1;
    const c = { id, nombre: data.nombre, nivel: data.nivel };
    this.cursos.push(c);
    return c;
  }

  eliminarCurso(id) {
    this.cursos = this.cursos.filter(c => c.id !== Number(id));
  }

  crearAsignatura(data) {
    const id = this.asignaturas.length ? Math.max(...this.asignaturas.map(a => a.id)) + 1 : 1;
    const a = { id, nombre: data.nombre, color: data.color || '#3498db' };
    this.asignaturas.push(a);
    return a;
  }

  eliminarAsignatura(id) {
    this.asignaturas = this.asignaturas.filter(a => a.id !== Number(id));
  }

  crearProfesor(data) {
    const id = this.profesores.length ? Math.max(...this.profesores.map(p => p.id)) + 1 : 1;
    const p = {
      id,
      nombre: data.nombre,
      apellido: data.apellido,
      email: data.email || '',
      nombre_completo: `${data.nombre} ${data.apellido}`
    };
    this.profesores.push(p);
    return p;
  }

  eliminarProfesor(id) {
    this.profesores = this.profesores.filter(p => p.id !== Number(id));
  }

  crearUsuario(data) {
    const u = {
      rut: data.rut,
      correo: data.correo,
      clave: data.password_hash || data.clave,
      password_hash: data.password_hash || data.clave,
      nombre: data.nombre,
      rol: data.rol,
      profesor_id: data.profesor_id || null,
      alumno_id: data.alumno_id || null,
      activo: true
    };
    this.usuarios.push(u);
    return u;
  }

  eliminarUsuario(rut) {
    this.usuarios = this.usuarios.filter(u => u.rut !== rut);
  }
}

export const store = new Store();
export default store;
