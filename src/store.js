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
    this.cursos = [
      { id: 1, nombre: '1A', nivel: 'Media' },
      { id: 2, nombre: '1B', nivel: 'Media' },
      { id: 3, nombre: '1C', nivel: 'Media' },
      { id: 4, nombre: '1D', nivel: 'Media' },
      { id: 5, nombre: '1E', nivel: 'Media' },
      { id: 6, nombre: '1F', nivel: 'Media' },
      { id: 7, nombre: '2A', nivel: 'Media' },
      { id: 8, nombre: '2B', nivel: 'Media' },
      { id: 9, nombre: '2C', nivel: 'Media' },
      { id: 10, nombre: '2D', nivel: 'Media' },
      { id: 11, nombre: '2E', nivel: 'Media' },
      { id: 12, nombre: '2F', nivel: 'Media' },
      { id: 13, nombre: '3A', nivel: 'Electricidad' },
      { id: 14, nombre: '3B', nivel: 'Electricidad' },
      { id: 15, nombre: '3C', nivel: 'Electronica' },
      { id: 16, nombre: '3D', nivel: 'Electronica' },
      { id: 17, nombre: '3E', nivel: 'Telecomunicación' },
      { id: 18, nombre: '3F', nivel: 'Telecomunicación' },
      { id: 19, nombre: '3G', nivel: 'Programacion' },
      { id: 20, nombre: '4A', nivel: 'Electricidad' },
      { id: 21, nombre: '4B', nivel: 'Electricidad' },
      { id: 22, nombre: '4C', nivel: 'Electronica' },
      { id: 23, nombre: '4D', nivel: 'Electronica' },
      { id: 24, nombre: '4E', nivel: 'Telecomunicación' },
      { id: 25, nombre: '4F', nivel: 'Telecomunicación' },
      { id: 26, nombre: '4G', nivel: 'Programacion' },
    ];
    this.cursoIdSeq = 27;

    // Asignaturas
    this.asignaturas = [
      { id: 1, nombre: "Lenguaje y Comunicación", color: "#2F6F4E" },
      { id: 2, nombre: "Matemática", color: "#14213D" },
      { id: 3, nombre: "Historia", color: "#A87F2C" },
      { id: 4, nombre: "Inglés", color: "#2C5F7A" },
      { id: 5, nombre: "Educación Física", color: "#A5332A" },
      { id: 6, nombre: "Ciencias Naturales", color: "#3B7A6B" },
      { id: 7, nombre: "Programación", color: "#1E3157" },
      { id: 8, nombre: "Bases de Datos", color: "#4A3B7A" },
    ];
    this.asignaturaIdSeq = 9;

    // Profesores
    this.profesores = [
      { id: 1, nombre: "Carolina", apellido: "Reyes", email: "c.reyes@liceo.cl", materia: "Matemática" },
      { id: 2, nombre: "Patricio", apellido: "Muñoz", email: "p.munoz@liceo.cl", materia: "Lenguaje y Comunicación" },
      { id: 3, nombre: "Valentina", apellido: "Soto", email: "v.soto@liceo.cl", materia: "Historia" },
      { id: 4, nombre: "Diego", apellido: "Fuentes", email: "d.fuentes@liceo.cl", materia: "Inglés" },
      { id: 5, nombre: "Marcela", apellido: "Vargas", email: "m.vargas@liceo.cl", materia: "Ciencias Naturales" },
      { id: 6, nombre: "Rodrigo", apellido: "Araya", email: "r.araya@liceo.cl", materia: "Programación" },
      { id: 7, nombre: "Andrea", apellido: "Pizarro", email: "a.pizarro@liceo.cl", materia: "Bases de Datos" },
    ];
    this.profesorIdSeq = 8;

    // Alumnos (vinculados a cursos por id)
    // 1A = 1, 2F = 12, 3G = 19, 4G = 26
    this.alumnos = [
      { id: 1, rut: "20.123.456-1", nombre: "Joaquín", apellido: "Rivas", curso_id: 26 },
      { id: 2, rut: "20.234.567-2", nombre: "Camila", apellido: "Torres", curso_id: 26 },
      { id: 3, rut: "20.345.678-3", nombre: "Bastián", apellido: "Núñez", curso_id: 26 },
      { id: 4, rut: "21.111.222-3", nombre: "Francisca", apellido: "Lara", curso_id: 19 },
      { id: 5, rut: "20.555.666-7", nombre: "Matías", apellido: "González", curso_id: 1 },
      { id: 6, rut: "19.888.999-0", nombre: "Antonia", apellido: "Sepúlveda", curso_id: 12 },
    ];
    this.alumnoIdSeq = 7;

    // Usuarios con passwords en texto plano/check simple
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
      {
        rut: "15.111.222-3",
        correo: "carolina.reyes@liceosofofa.cl",
        clave: "profe123",
        nombre: "Carolina Reyes",
        rol: "profe",
        profesor_id: 1,
        alumno_id: null,
        activo: true
      },
      {
        rut: "13.444.555-6",
        correo: "rodrigo.araya@liceosofofa.cl",
        clave: "profe123",
        nombre: "Rodrigo Araya",
        rol: "profe",
        profesor_id: 6,
        alumno_id: null,
        activo: true
      },
      {
        rut: "19.000.002-2",
        correo: "profe@liceosofofa.cl",
        clave: "profe123",
        nombre: "Usuario Profesor",
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
        nombre: "Joaquín Rivas",
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

    // Evaluaciones de ejemplo
    this.evaluaciones = [
      {
        id: 1,
        titulo: "Prueba números enteros",
        fecha: dateOffset(-2),
        hora: "10:00",
        descripcion: "Operaciones básicas y resolución de problemas con números enteros.",
        asignatura_id: 2, // Matemática
        curso_id: 1, // 1A
        profesor_id: 1,
        created_at: new Date()
      },
      {
        id: 2,
        titulo: "Ensayo narrativo",
        fecha: todayStr,
        hora: "08:30",
        descripcion: "Redacción individual sobre literatura contemporánea.",
        asignatura_id: 1, // Lenguaje
        curso_id: 1, // 1A
        profesor_id: 2,
        created_at: new Date()
      },
      {
        id: 3,
        titulo: "Prueba POO en TypeScript/Python",
        fecha: todayStr,
        hora: "10:00",
        descripcion: "Clases, herencia y polimorfismo con ejercicios prácticos.",
        asignatura_id: 7, // Programación
        curso_id: 26, // 4G
        profesor_id: 6,
        created_at: new Date()
      },
      {
        id: 4,
        titulo: "Taller modelo entidad-relación",
        fecha: dateOffset(2),
        hora: "11:00",
        descripcion: "Normalización y diagramas relacionales.",
        asignatura_id: 8, // Bases de Datos
        curso_id: 26, // 4G
        profesor_id: 7,
        created_at: new Date()
      },
      {
        id: 5,
        titulo: "Prueba verbos en inglés",
        fecha: dateOffset(4),
        hora: "10:30",
        descripcion: "Tiempos verbales pasados y participios.",
        asignatura_id: 4, // Inglés
        curso_id: 19, // 3G
        profesor_id: 4,
        created_at: new Date()
      },
      {
        id: 6,
        titulo: "Parcial funciones y trigonometría",
        fecha: dateOffset(6),
        hora: "09:00",
        descripcion: "Funciones cuadráticas y razones trigonométricas.",
        asignatura_id: 2, // Matemática
        curso_id: 12, // 2F
        profesor_id: 1,
        created_at: new Date()
      }
    ];
    this.evaluacionIdSeq = 7;

    // Asistencias iniciales
    this.asistencias = [
      // Para eval 1 (1A, alumno 5)
      { id: 1, evaluacion_id: 1, alumno_id: 5, presente: false, motivo: "Licencia médica", justificado: true },
      // Para eval 3 (4G, alumnos 1, 2, 3)
      { id: 2, evaluacion_id: 3, alumno_id: 1, presente: true, motivo: "", justificado: false },
      { id: 3, evaluacion_id: 3, alumno_id: 2, presente: false, motivo: "Inasistencia sin aviso", justificado: false },
      { id: 4, evaluacion_id: 3, alumno_id: 3, presente: true, motivo: "", justificado: false },
    ];
    this.asistenciaIdSeq = 5;

    // Recuperaciones iniciales
    this.recuperaciones = [
      {
        id: 1,
        evaluacion_id: 1,
        alumno_id: 5,
        fecha_recuperacion: dateOffset(3),
        motivo: "Licencia médica acreditada en Inspectoría",
        porcentaje_exigencia: EXIGENCIA_JUSTIFICADO, // 60%
        estado: "pendiente",
        created_at: new Date()
      },
      {
        id: 2,
        evaluacion_id: 3,
        alumno_id: 2,
        fecha_recuperacion: dateOffset(5),
        motivo: "Falta injustificada",
        porcentaje_exigencia: EXIGENCIA_NO_JUSTIFICADO, // 70%
        estado: "pendiente",
        created_at: new Date()
      }
    ];
    this.recuperacionIdSeq = 3;
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

  guardarAsistencia({ alumno_id, evaluacion_id, presente, motivo, justificado }) {
    const aId = Number(alumno_id);
    const eId = Number(evaluacion_id);
    const existingIdx = this.asistencias.findIndex(a => a.alumno_id === aId && a.evaluacion_id === eId);

    if (existingIdx !== -1) {
      this.asistencias[existingIdx] = {
        ...this.asistencias[existingIdx],
        presente,
        motivo: presente ? '' : (motivo || ''),
        justificado: presente ? false : !!justificado
      };
      return this.asistencias[existingIdx];
    } else {
      const nueva = {
        id: this.asistenciaIdSeq++,
        alumno_id: aId,
        evaluacion_id: eId,
        presente,
        motivo: presente ? '' : (motivo || ''),
        justificado: presente ? false : !!justificado
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
