import express from 'express';
import session from 'express-session';
import path from 'path';
import { fileURLToPath } from 'url';
import store from './src/store.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

// Trust reverse proxy (Google Cloud Run / Nginx / AI Studio)
app.set('trust proxy', 1);

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Intercept Set-Cookie header to append ; Partitioned on HTTPS (CHIPS standard for iframes)
app.use((req, res, next) => {
  const prevSetHeader = res.setHeader;
  res.setHeader = function (name, value) {
    if (typeof name === 'string' && name.toLowerCase() === 'set-cookie') {
      const isHttps = req.secure || req.headers['x-forwarded-proto'] === 'https';
      if (isHttps) {
        if (Array.isArray(value)) {
          value = value.map(cookie => {
            if (typeof cookie === 'string' && cookie.includes('SameSite=None') && !cookie.includes('Partitioned')) {
              return `${cookie}; Partitioned`;
            }
            return cookie;
          });
        } else if (typeof value === 'string' && value.includes('SameSite=None') && !value.includes('Partitioned')) {
          value = `${value}; Partitioned`;
        }
      }
    }
    return prevSetHeader.apply(this, arguments);
  };
  next();
});

// Configure session with explicit MemoryStore to persist across requests
const sessionStore = new session.MemoryStore();

const sessionMiddleware = session({
  store: sessionStore,
  secret: process.env.SESSION_SECRET || 'agendex-liceo-secret-2024',
  resave: false,
  saveUninitialized: false,
  proxy: true,
  cookie: {
    maxAge: 24 * 60 * 60 * 1000,
    httpOnly: true
  }
});

app.use(sessionMiddleware);

// Dynamically adjust cookie security for HTTPS / iframes vs localhost HTTP
app.use((req, res, next) => {
  if (req.session && req.session.cookie) {
    const isHttps = req.secure || req.headers['x-forwarded-proto'] === 'https';
    if (isHttps) {
      req.session.cookie.secure = true;
      req.session.cookie.sameSite = 'none';
    } else {
      req.session.cookie.secure = false;
      req.session.cookie.sameSite = 'lax';
    }
  }
  next();
});

// View engine
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Custom flash & user context middleware
app.use((req, res, next) => {
  if (!req.session.flash) {
    req.session.flash = [];
  }
  
  const flashList = (req.session.flash || []).map(f => ({
    category: f.categoria || f.category || 'info',
    categoria: f.categoria || f.category || 'info',
    message: f.texto || f.message || '',
    texto: f.texto || f.message || ''
  }));
  res.locals.current_user = req.session.user || null;
  res.locals.messages = flashList;
  res.locals.mensajes = flashList;
  res.locals.ROLES = {
    utp: 'UTP / Directivo',
    profe: 'Profesor',
    inspe: 'Inspectoría',
    alumno: 'Alumno'
  };
  req.session.flash = []; // clear after reading

  const d = new Date();
  const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
  res.locals.today_formatted = d.toLocaleDateString('es-CL', options);

  req.flash = (categoria, texto) => {
    if (!req.session.flash) req.session.flash = [];
    req.session.flash.push({
      categoria,
      texto,
      category: categoria,
      message: texto
    });
  };

  next();
});

// Auth Guard
function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  next();
}

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.session.user) {
      return res.redirect('/login');
    }
    if (!roles.includes(req.session.user.rol)) {
      req.flash('danger', 'No tienes permisos para acceder a esta sección.');
      return res.redirect('/');
    }
    next();
  };
}

// -------------------------------------------------------------
// AUTH ROUTES
// -------------------------------------------------------------
const renderLogin = (req, res) => {
  if (req.session.user) {
    return res.redirect('/');
  }
  res.render('login', { title: 'Iniciar Sesión', error: null, correo: '' });
};

const handleLogin = (req, res) => {
  const { correo, password } = req.body;
  const user = store.getUsuarioByCorreo(correo);

  if (!user || (user.password_hash !== password && user.clave !== password)) {
    return res.render('login', {
      title: 'Iniciar Sesión',
      error: 'Correo o contraseña incorrectos.',
      correo: correo || ''
    });
  }

  if (!user.activo) {
    return res.render('login', {
      title: 'Iniciar Sesión',
      error: 'Esta cuenta está desactivada por administración.',
      correo: correo || ''
    });
  }

  req.session.user = {
    rut: user.rut,
    correo: user.correo,
    nombre: user.nombre,
    rol: user.rol,
    profesor_id: user.profesor_id || null,
    alumno_id: user.alumno_id || null
  };

  req.flash('success', `¡Bienvenido(a) de nuevo, ${user.nombre}!`);
  req.session.save((err) => {
    if (err) {
      console.error('Error guardando sesión:', err);
    }
    res.redirect('/');
  });
};

const handleLogout = (req, res) => {
  req.session.destroy((err) => {
    res.clearCookie('connect.sid');
    res.redirect('/login');
  });
};

const handleDemoLogin = (req, res) => {
  const { rol } = req.params;
  let correo = 'inspe.diaz@liceorbl.cl';
  if (rol === 'utp') correo = 'utp@liceorbl.cl';
  else if (rol === 'profe' || rol === 'profesor') correo = 'carolina.reyes@liceosofofa.cl';
  else if (rol === 'inspe' || rol === 'inspectoria') correo = 'inspe.diaz@liceorbl.cl';
  else if (rol === 'alumno') correo = 'joaquin.rivas@liceorbl.cl';

  const user = store.getUsuarioByCorreo(correo);
  if (!user) {
    return res.redirect('/login');
  }

  req.session.user = {
    rut: user.rut,
    correo: user.correo,
    nombre: user.nombre,
    rol: user.rol,
    profesor_id: user.profesor_id || null,
    alumno_id: user.alumno_id || null
  };

  req.flash('success', `Acceso rápido de prueba iniciado como ${user.nombre} (${user.rol.toUpperCase()})`);
  req.session.save((err) => {
    res.redirect('/');
  });
};

app.get('/login', renderLogin);
app.get('/auth/login', renderLogin);
app.post('/login', handleLogin);
app.post('/auth/login', handleLogin);
app.get('/auth/demo/:rol', handleDemoLogin);
app.all('/logout', handleLogout);
app.all('/auth/logout', handleLogout);

// -------------------------------------------------------------
// DASHBOARD (INICIO)
// -------------------------------------------------------------
app.get('/', requireAuth, (req, res) => {
  const user = req.session.user;
  const hoy = new Date().toISOString().split('T')[0];

  if (user.rol === 'alumno') {
    // Alumno dashboard
    let alumno = null;
    if (user.alumno_id) {
      alumno = store.getAlumnoById(user.alumno_id);
    }
    if (!alumno) {
      alumno = store.getAlumnoByRut(user.rut) || store.alumnos[0];
    }

    const evalsCurso = alumno ? store.evaluaciones.filter(e => e.curso_id === alumno.curso_id) : [];
    const misEvals = evalsCurso
      .map(e => store.getEvaluacion(e.id))
      .sort((a, b) => a.fecha.localeCompare(b.fecha));

    const evalsSemana = misEvals.filter(e => {
      if (e.fecha < hoy) return false;
      const diff = (new Date(e.fecha) - new Date(hoy)) / (1000 * 60 * 60 * 24);
      return diff <= 7;
    });

    const misAsistencias = alumno ? store.getAsistenciasByAlumno(alumno.id) : [];
    const recsAl = alumno ? store.getRecuperacionesByAlumno(alumno.id) : [];
    const recsPendientes = recsAl.filter(r => r.estado === 'pendiente');

    return res.render('index_alumno', {
      title: 'Inicio - Alumno',
      active: 'dashboard',
      alumno,
      stats: {
        total_evaluaciones: misEvals.length,
        evals_semana: evalsSemana.length,
        recuperaciones_pendientes: recsPendientes.length
      },
      mis_evals: misEvals,
      today: hoy,
      mis_recuperaciones: recsAl,
      mis_asistencias: misAsistencias
    });
  }

  // Non-alumno dashboard (UTP, Profesor, Inspectoría)
  const evalsHoy = store.evaluaciones
    .filter(e => e.fecha === hoy)
    .map(e => store.getEvaluacion(e.id));

  const evalsSemana = store.evaluaciones
    .filter(e => {
      if (e.fecha < hoy) return false;
      const diff = (new Date(e.fecha) - new Date(hoy)) / (1000 * 60 * 60 * 24);
      return diff <= 7;
    })
    .map(e => store.getEvaluacion(e.id));

  const recsPendientes = store.recuperaciones
    .filter(r => r.estado === 'pendiente')
    .map(r => store.enrichRecuperacion(r));

  // Count by course
  const evalsPorCurso = store.cursos.map(c => {
    const count = store.evaluaciones.filter(e => e.curso_id === c.id).length;
    return {
      curso_nombre: c.nombre,
      count
    };
  }).filter(x => x.count > 0).sort((a, b) => b.count - a.count);

  res.render('dashboard', {
    title: 'Panel de Control',
    active: 'dashboard',
    evals_hoy: evalsHoy,
    evals_semana: evalsSemana,
    recuperaciones_pendientes: recsPendientes,
    total_cursos: store.cursos.length,
    evals_por_curso: evalsPorCurso,
    total_evaluaciones_activas: store.evaluaciones.length,
    total_alumnos: store.alumnos.length,
    hoy
  });
});

// -------------------------------------------------------------
// EVALUACIONES
// -------------------------------------------------------------
app.get('/evaluaciones', requireAuth, (req, res) => {
  const { fecha_desde, fecha_hasta, curso_id, asignatura_id } = req.query;
  let list = store.evaluaciones.map(e => store.getEvaluacion(e.id));

  if (fecha_desde) list = list.filter(e => e.fecha >= fecha_desde);
  if (fecha_hasta) list = list.filter(e => e.fecha <= fecha_hasta);
  if (curso_id) list = list.filter(e => e.curso_id === Number(curso_id));
  if (asignatura_id) list = list.filter(e => e.asignatura_id === Number(asignatura_id));

  // Sort descending by date
  list.sort((a, b) => b.fecha.localeCompare(a.fecha));

  res.render('evaluaciones/listar', {
    title: 'Evaluaciones',
    active: 'evaluaciones',
    evaluaciones: list,
    cursos: store.cursos,
    asignaturas: store.asignaturas,
    filtros: { fecha_desde, fecha_hasta, curso_id, asignatura_id }
  });
});

// API Check availability (Enforces max 2 evaluations per course per day)
app.get('/evaluaciones/api/disponibilidad', requireAuth, (req, res) => {
  const curso_id = Number(req.query.curso_id);
  const fecha = req.query.fecha;

  if (!curso_id || !fecha) {
    return res.status(400).json({ error: 'curso_id y fecha requeridos' });
  }

  const existentes = store.contarEnFecha(curso_id, fecha);
  const evals = store.evaluaciones.filter(e => e.curso_id === curso_id && e.fecha === fecha);

  res.json({
    curso_id,
    fecha,
    existentes,
    disponibles: Math.max(0, 2 - existentes),
    evaluaciones: evals
  });
});

app.get('/evaluaciones/crear', requireAuth, requireRole('profe', 'utp'), (req, res) => {
  const user = req.session.user;
  let miProfesor = store.profesores.find(p => p.id === user.profesor_id);
  if (!miProfesor) {
    miProfesor = store.profesores[0] || { nombre_completo: user.nombre, id: 1 };
  }

  const hoy = new Date().toISOString().split('T')[0];

  res.render('evaluaciones/crear', {
    title: 'Nueva Evaluación',
    active: 'evaluaciones',
    cursos: store.cursos,
    asignaturas: store.asignaturas,
    mi_profesor: miProfesor,
    hoy
  });
});

app.post('/evaluaciones/crear', requireAuth, requireRole('profe', 'utp'), (req, res) => {
  const user = req.session.user;
  const { titulo, fecha, hora, curso_id, asignatura_id, descripcion } = req.body;
  const cid = Number(curso_id);
  const aid = Number(asignatura_id);

  // Business Rule: Validate availability (Max 2 evaluations per course per day)
  if (!store.hayLugar(cid, fecha)) {
    req.flash('danger', 'No se puede crear la evaluación: El curso seleccionado ya tiene 2 evaluaciones asignadas para esa fecha (límite máximo diario alcanzado).');
    return res.redirect('/evaluaciones/crear');
  }

  let profId = user.profesor_id;
  if (!profId) {
    profId = store.profesores[0]?.id || 1;
  }

  const ev = store.crearEvaluacion({
    titulo,
    fecha,
    hora: hora || null,
    curso_id: cid,
    asignatura_id: aid,
    profesor_id: profId,
    descripcion: descripcion || ''
  });

  req.flash('success', `Evaluación "${ev.titulo}" agendada exitosamente.`);
  res.redirect(`/evaluaciones/${ev.id}`);
});

app.get('/evaluaciones/:id', requireAuth, (req, res) => {
  const id = Number(req.params.id);
  const ev = store.getEvaluacionById(id);

  if (!ev) {
    req.flash('danger', 'Evaluación no encontrada.');
    return res.redirect('/evaluaciones');
  }

  const alumnos = store.getAlumnosByCurso(ev.curso_id);
  const asistenciasMap = {};
  const asistList = store.getAsistenciasByEvaluacion(ev.id);
  asistList.forEach(a => {
    asistenciasMap[a.alumno_id] = a;
  });

  res.render('evaluaciones/detalle', {
    title: ev.titulo,
    active: 'evaluaciones',
    ev,
    alumnos,
    asistencias: asistenciasMap
  });
});

app.get('/evaluaciones/:id/editar', requireAuth, (req, res) => {
  const id = Number(req.params.id);
  const ev = store.getEvaluacionById(id);

  if (!ev) {
    req.flash('danger', 'Evaluación no encontrada.');
    return res.redirect('/evaluaciones');
  }

  // Check permission
  const user = req.session.user;
  if (user.rol !== 'utp' && !(user.rol === 'profe' && user.profesor_id === ev.profesor_id)) {
    req.flash('danger', 'No tienes permisos para editar esta evaluación.');
    return res.redirect(`/evaluaciones/${id}`);
  }

  res.render('evaluaciones/editar', {
    title: `Editar - ${ev.titulo}`,
    active: 'evaluaciones',
    ev,
    cursos: store.cursos,
    asignaturas: store.asignaturas
  });
});

app.post('/evaluaciones/:id/editar', requireAuth, (req, res) => {
  const id = Number(req.params.id);
  const ev = store.getEvaluacionById(id);

  if (!ev) {
    req.flash('danger', 'Evaluación no encontrada.');
    return res.redirect('/evaluaciones');
  }

  const user = req.session.user;
  if (user.rol !== 'utp' && !(user.rol === 'profe' && user.profesor_id === ev.profesor_id)) {
    req.flash('danger', 'No tienes permisos para editar esta evaluación.');
    return res.redirect(`/evaluaciones/${id}`);
  }

  const { titulo, fecha, hora, curso_id, asignatura_id, descripcion } = req.body;
  const cid = Number(curso_id);
  const aid = Number(asignatura_id);

  // If date or course changed, verify limit
  if (ev.fecha !== fecha || ev.curso_id !== cid) {
    const existingOther = store.evaluaciones.filter(e => e.id !== id && e.curso_id === cid && e.fecha === fecha).length;
    if (existingOther >= 2) {
      req.flash('danger', 'No hay cupos disponibles en esa fecha para el curso (máximo 2 evaluaciones por día).');
      return res.redirect(`/evaluaciones/${id}/editar`);
    }
  }

  store.actualizarEvaluacion(id, {
    titulo,
    fecha,
    hora: hora || null,
    curso_id: cid,
    asignatura_id: aid,
    descripcion: descripcion || ''
  });

  req.flash('success', 'Evaluación actualizada correctamente.');
  res.redirect(`/evaluaciones/${id}`);
});

app.post('/evaluaciones/:id/eliminar', requireAuth, (req, res) => {
  const id = Number(req.params.id);
  const ev = store.getEvaluacionById(id);

  if (ev) {
    const user = req.session.user;
    if (user.rol === 'utp' || (user.rol === 'profe' && user.profesor_id === ev.profesor_id)) {
      store.eliminarEvaluacion(id);
      req.flash('success', 'Evaluación eliminada correctamente.');
    } else {
      req.flash('danger', 'No tienes permiso para eliminar esta evaluación.');
    }
  }

  res.redirect('/evaluaciones');
});

// Guardar Asistencia
app.post('/evaluaciones/:id/asistencia', requireAuth, requireRole('profe', 'utp', 'inspe'), (req, res) => {
  const evalId = Number(req.params.id);
  const ev = store.getEvaluacionById(evalId);

  if (!ev) {
    req.flash('danger', 'Evaluación no encontrada.');
    return res.redirect('/evaluaciones');
  }

  const user = req.session.user;
  const canJustify = ['utp', 'inspe'].includes(user.rol);
  const alumnos = store.getAlumnosByCurso(ev.curso_id);

  alumnos.forEach(alumno => {
    // If checkbox 'alumno_{id}' is checked -> presente
    const presente = req.body[`alumno_${alumno.id}`] !== undefined;
    const motivo = req.body[`motivo_${alumno.id}`] || '';
    
    // Check justification permission
    let justificado = false;
    if (canJustify) {
      justificado = req.body[`justificado_${alumno.id}`] !== undefined;
    } else {
      // Preserve existing justification if profesor is updating attendance
      const existing = store.getAsistencia(alumno.id, evalId);
      justificado = existing ? existing.justificado : false;
    }

    store.guardarAsistencia({
      alumno_id: alumno.id,
      evaluacion_id: evalId,
      presente,
      motivo: presente ? '' : motivo,
      justificado: presente ? false : justificado
    });
  });

  req.flash('success', 'Registro de asistencia actualizado.');
  res.redirect(`/evaluaciones/${evalId}`);
});

// -------------------------------------------------------------
// ALUMNOS
// -------------------------------------------------------------
app.get('/alumnos', requireAuth, (req, res) => {
  const { busqueda, curso_id } = req.query;
  let list = [...store.alumnos];

  if (curso_id) {
    list = list.filter(a => a.curso_id === Number(curso_id));
  }

  if (busqueda) {
    const q = busqueda.toLowerCase().trim();
    list = list.filter(a => 
      a.nombre.toLowerCase().includes(q) ||
      a.apellido.toLowerCase().includes(q) ||
      a.rut.toLowerCase().includes(q)
    );
  }

  res.render('alumnos/listar', {
    title: 'Alumnos',
    active: 'alumnos',
    alumnos: list,
    cursos: store.cursos,
    filtros: { busqueda, curso_id }
  });
});

app.get('/alumnos/crear', requireAuth, requireRole('utp'), (req, res) => {
  res.render('alumnos/crear', {
    title: 'Nuevo Alumno',
    active: 'alumnos',
    cursos: store.cursos
  });
});

app.post('/alumnos/crear', requireAuth, requireRole('utp'), (req, res) => {
  const { rut, nombre, apellido, curso_id } = req.body;
  
  const alumno = store.crearAlumno({
    rut,
    nombre,
    apellido,
    curso_id: Number(curso_id)
  });

  req.flash('success', `Alumno ${alumno.nombre} ${alumno.apellido} registrado exitosamente.`);
  res.redirect(`/alumnos/${alumno.id}`);
});

app.get('/alumnos/:id', requireAuth, (req, res) => {
  const id = Number(req.params.id);
  const alumno = store.getAlumnoById(id);

  if (!alumno) {
    req.flash('danger', 'Alumno no encontrado.');
    return res.redirect('/alumnos');
  }

  const evalsCurso = store.evaluaciones.filter(e => e.curso_id === alumno.curso_id);
  const asistenciasList = store.getAsistenciasByAlumno(alumno.id);
  
  // Format items
  const asistenciasConEval = asistenciasList.map(a => ({
    asistencia: a,
    evaluacion: store.getEvaluacionById(a.evaluacion_id) || {}
  })).filter(item => item.evaluacion.id);

  const ausencias = asistenciasList.filter(a => !a.presente);
  const recuperaciones = store.getRecuperacionesByAlumno(alumno.id);

  res.render('alumnos/perfil', {
    title: alumno.nombre_completo,
    active: 'alumnos',
    alumno,
    total_evals: evalsCurso.length,
    total_ausencias: ausencias.length,
    asistencias: asistenciasConEval,
    recuperaciones
  });
});

// -------------------------------------------------------------
// RECUPERACIONES
// -------------------------------------------------------------
app.get('/recuperaciones', requireAuth, (req, res) => {
  const { estado } = req.query;
  let list = [...store.recuperaciones];

  if (estado) {
    list = list.filter(r => r.estado === estado);
  }

  // Enrich with full objects
  list = list.map(r => ({
    ...r,
    alumno: store.getAlumnoById(r.alumno_id),
    evaluacion: store.getEvaluacionById(r.evaluacion_id)
  }));

  res.render('recuperaciones/listar', {
    title: 'Recuperaciones',
    active: 'recuperaciones',
    recuperaciones: list,
    filtros: { estado }
  });
});

app.get('/recuperaciones/crear', requireAuth, requireRole('utp', 'profe', 'inspe'), (req, res) => {
  const hoy = new Date().toISOString().split('T')[0];
  const alumnoId = req.query.alumno_id ? Number(req.query.alumno_id) : null;

  res.render('recuperaciones/crear', {
    title: 'Nueva Recuperación',
    active: 'recuperaciones',
    evaluaciones: store.evaluaciones,
    alumnos: store.alumnos,
    alumno_id_preselect: alumnoId,
    hoy
  });
});

app.post('/recuperaciones/crear', requireAuth, requireRole('utp', 'profe', 'inspe'), (req, res) => {
  const { evaluacion_id, alumno_id, fecha_recuperacion, motivo } = req.body;
  const aId = Number(alumno_id);
  const eId = Number(evaluacion_id);

  // Determine requirement percentage (60% if justified, 70% if unjustified)
  const asist = store.getAsistencia(aId, eId);
  const porcentaje = (asist && asist.justificado) ? 60.0 : 70.0;

  store.crearRecuperacion({
    evaluacion_id: eId,
    alumno_id: aId,
    fecha_recuperacion,
    porcentaje_exigencia: porcentaje,
    motivo: motivo || ''
  });

  req.flash('success', `Recuperación asignada al ${porcentaje}% de exigencia.`);
  res.redirect('/recuperaciones');
});

app.post('/recuperaciones/:id/completar', requireAuth, requireRole('utp', 'profe', 'inspe'), (req, res) => {
  const id = Number(req.params.id);
  store.actualizarEstadoRecuperacion(id, 'completada');
  req.flash('success', 'Recuperación marcada como completada.');
  res.redirect(req.get('Referrer') || '/recuperaciones');
});

app.post('/recuperaciones/:id/cancelar', requireAuth, requireRole('utp', 'profe', 'inspe'), (req, res) => {
  const id = Number(req.params.id);
  store.actualizarEstadoRecuperacion(id, 'cancelada');
  req.flash('info', 'Recuperación cancelada.');
  res.redirect(req.get('Referrer') || '/recuperaciones');
});

// -------------------------------------------------------------
// REPORTES
// -------------------------------------------------------------
app.get('/reportes/calendario', requireAuth, (req, res) => {
  const now = new Date();
  const anio = req.query.anio ? parseInt(req.query.anio) : now.getFullYear();
  const mes = req.query.mes ? parseInt(req.query.mes) : now.getMonth() + 1;
  const curso_id = req.query.curso_id ? Number(req.query.curso_id) : null;

  const mesesNombres = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const mesesList = mesesNombres.map((m, i) => ({ num: i + 1, nombre: m }));

  // Filter evaluations in this month and year
  let evals = store.evaluaciones.filter(e => {
    const parts = e.fecha.split('-');
    return parseInt(parts[0]) === anio && parseInt(parts[1]) === mes;
  });

  if (curso_id) {
    evals = evals.filter(e => e.curso_id === curso_id);
  }

  // Group by day
  const evalsPorDia = {};
  evals.forEach(e => {
    const dia = parseInt(e.fecha.split('-')[2]);
    if (!evalsPorDia[dia]) evalsPorDia[dia] = [];
    evalsPorDia[dia].push(e);
  });

  // Generate calendar weeks matrix (Monday to Sunday)
  const primerDia = new Date(anio, mes - 1, 1);
  const ultimoDia = new Date(anio, mes, 0);
  const diasEnMes = ultimoDia.getDate();

  // JavaScript: 0 is Sunday, 1 is Monday. Convert so 0 is Monday, 6 is Sunday
  let diaSemanaInicio = (primerDia.getDay() + 6) % 7;

  const semanas = [];
  let semanaActual = new Array(diaSemanaInicio).fill(0);

  for (let d = 1; d <= diasEnMes; d++) {
    semanaActual.push(d);
    if (semanaActual.length === 7) {
      semanas.push(semanaActual);
      semanaActual = [];
    }
  }

  if (semanaActual.length > 0) {
    while (semanaActual.length < 7) {
      semanaActual.push(0);
    }
    semanas.push(semanaActual);
  }

  res.render('reportes/calendario', {
    title: 'Calendario de Evaluaciones',
    active: 'calendario',
    mes,
    anio,
    mes_nombre: mesesNombres[mes - 1],
    meses: mesesList,
    semanas,
    evals_por_dia: evalsPorDia,
    cursos: store.cursos,
    filtros: { curso_id },
    today_day: now.getDate(),
    today_month: now.getMonth() + 1,
    today_year: now.getFullYear()
  });
});

app.get('/reportes/pendientes', requireAuth, (req, res) => {
  const pendientes = store.recuperaciones.filter(r => r.estado === 'pendiente');

  // Group by evaluation id
  const agrupadas = {};
  pendientes.forEach(r => {
    if (!agrupadas[r.evaluacion_id]) agrupadas[r.evaluacion_id] = [];
    agrupadas[r.evaluacion_id].push({
      ...r,
      alumno: store.getAlumnoById(r.alumno_id),
      evaluacion: store.getEvaluacionById(r.evaluacion_id)
    });
  });

  res.render('reportes/pendientes', {
    title: 'Alumnos Pendientes de Recuperación',
    active: 'pendientes',
    alumnos_por_eval: agrupadas
  });
});

app.get('/reportes/carga', requireAuth, (req, res) => {
  const now = new Date();
  const anio = now.getFullYear();
  const mes = now.getMonth() + 1;
  const mesesNombres = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const datosCurso = store.cursos.map(c => {
    const evalsMes = store.evaluaciones.filter(e => {
      if (e.curso_id !== c.id) return false;
      const parts = e.fecha.split('-');
      return parseInt(parts[0]) === anio && parseInt(parts[1]) === mes;
    }).length;

    const alumnosCount = store.getAlumnosByCurso(c.id).length;

    return {
      curso: c,
      evals_mes: evalsMes,
      alumnos: alumnosCount
    };
  });

  res.render('reportes/carga', {
    title: 'Carga Académica',
    active: 'carga',
    mes_nombre: mesesNombres[mes - 1],
    anio,
    datos_curso: datosCurso
  });
});

// -------------------------------------------------------------
// ADMIN (UTP ONLY)
// -------------------------------------------------------------
app.get('/admin', requireAuth, requireRole('utp'), (req, res) => {
  res.render('admin/index', {
    title: 'Configuración',
    active: 'admin',
    cursos: store.cursos,
    asignaturas: store.asignaturas,
    profesores: store.profesores,
    usuarios: store.usuarios
  });
});

// Admin: Cursos
app.get('/admin/cursos', requireAuth, requireRole('utp'), (req, res) => {
  res.render('admin/cursos', {
    title: 'Cursos',
    active: 'admin',
    data: store.cursos
  });
});

app.post('/admin/cursos', requireAuth, requireRole('utp'), (req, res) => {
  const { nombre, nivel } = req.body;
  store.crearCurso({ nombre, nivel });
  req.flash('success', `Curso ${nombre} registrado.`);
  res.redirect('/admin/cursos');
});

app.post('/admin/cursos/:id/eliminar', requireAuth, requireRole('utp'), (req, res) => {
  store.eliminarCurso(Number(req.params.id));
  req.flash('info', 'Curso eliminado.');
  res.redirect('/admin/cursos');
});

// Admin: Asignaturas
app.get('/admin/asignaturas', requireAuth, requireRole('utp'), (req, res) => {
  res.render('admin/asignaturas', {
    title: 'Asignaturas',
    active: 'admin',
    data: store.asignaturas
  });
});

app.post('/admin/asignaturas', requireAuth, requireRole('utp'), (req, res) => {
  const { nombre, color } = req.body;
  store.crearAsignatura({ nombre, color });
  req.flash('success', `Asignatura ${nombre} registrada.`);
  res.redirect('/admin/asignaturas');
});

app.post('/admin/asignaturas/:id/eliminar', requireAuth, requireRole('utp'), (req, res) => {
  store.eliminarAsignatura(Number(req.params.id));
  req.flash('info', 'Asignatura eliminada.');
  res.redirect('/admin/asignaturas');
});

// Admin: Profesores
app.get('/admin/profesores', requireAuth, requireRole('utp'), (req, res) => {
  res.render('admin/profesores', {
    title: 'Profesores',
    active: 'admin',
    data: store.profesores
  });
});

app.post('/admin/profesores', requireAuth, requireRole('utp'), (req, res) => {
  const { nombre, apellido, email } = req.body;
  store.crearProfesor({ nombre, apellido, email });
  req.flash('success', `Profesor ${nombre} ${apellido} registrado.`);
  res.redirect('/admin/profesores');
});

app.post('/admin/profesores/:id/eliminar', requireAuth, requireRole('utp'), (req, res) => {
  store.eliminarProfesor(Number(req.params.id));
  req.flash('info', 'Profesor eliminado.');
  res.redirect('/admin/profesores');
});

// Admin: Usuarios
app.get('/admin/usuarios', requireAuth, requireRole('utp'), (req, res) => {
  res.render('admin/usuarios', {
    title: 'Usuarios',
    active: 'admin',
    data: store.usuarios,
    roles: {
      utp: 'UTP / Directivo',
      profe: 'Profesor',
      inspe: 'Inspectoría',
      alumno: 'Alumno'
    }
  });
});

app.post('/admin/usuarios', requireAuth, requireRole('utp'), (req, res) => {
  const { rut, correo, password, nombre, rol } = req.body;
  store.crearUsuario({
    rut,
    correo,
    password_hash: password,
    nombre,
    rol
  });
  req.flash('success', `Usuario ${correo} creado.`);
  res.redirect('/admin/usuarios');
});

app.post('/admin/usuarios/:rut/toggle', requireAuth, requireRole('utp'), (req, res) => {
  const rut = decodeURIComponent(req.params.rut);
  const u = store.usuarios.find(user => user.rut === rut);
  if (u) {
    u.activo = !u.activo;
    req.flash('info', `Estado de usuario actualizado: ${u.activo ? 'Activo' : 'Inactivo'}`);
  }
  res.redirect('/admin/usuarios');
});

app.post('/admin/usuarios/:rut/eliminar', requireAuth, requireRole('utp'), (req, res) => {
  const rut = decodeURIComponent(req.params.rut);
  store.eliminarUsuario(rut);
  req.flash('info', 'Usuario eliminado.');
  res.redirect('/admin/usuarios');
});

// 404 handler
app.use((req, res) => {
  res.status(404).send('Página no encontrada en AgendEx');
});

// Start Server on 0.0.0.0:3000
app.listen(PORT, '0.0.0.0', () => {
  console.log(`AgendEx servidor iniciado en http://0.0.0.0:${PORT}`);
});
