# -*- coding: utf-8 -*-
"""
AgendEx - Sistema de Gestión de Evaluaciones Escolares
Backend en Flask con Base de Datos MySQL (Liceo Industrial Bicentenario RBL)
Código simplificado y limpio.
"""

import os
import calendar
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from config import Config, get_db_connection

app = Flask(__name__, template_folder='templates', static_folder='public', static_url_path='')
app.config.from_object(Config)

ROLES = {
    'utp': 'UTP / Directivo',
    'profe': 'Profesor',
    'inspe': 'Inspectoría',
    'alumno': 'Alumno'
}

# -------------------------------------------------------------
# HELPERS Y FORMATEADORES
# -------------------------------------------------------------
def format_date(val):
    if not val:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val)

def format_time(val):
    if not val:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%H:%M')
    s = str(val)
    return s[:5] if ':' in s else s

def enrich_eval(e):
    if not e:
        return e
    e['fecha'] = format_date(e.get('fecha'))
    e['hora'] = format_time(e.get('hora'))
    e['asignatura'] = {
        'nombre': e.get('asignatura_nombre') or 'General',
        'color': e.get('asignatura_color') or '#14213D'
    }
    e['profesor'] = {
        'nombre_completo': f"{e.get('profe_nombre') or ''} {e.get('profe_apellido') or ''}".strip() or 'Docente'
    }
    e['curso'] = {
        'nombre': e.get('curso_nombre') or 'Curso',
        'nivel': e.get('curso_nivel') or ''
    }
    return e

def enrich_recup(r):
    if not r:
        return r
    r['fecha_recuperacion'] = format_date(r.get('fecha_recuperacion'))
    r['eval_fecha'] = format_date(r.get('eval_fecha'))
    r['evaluacion'] = {
        'id': r.get('evaluacion_id'),
        'titulo': r.get('eval_titulo') or 'Evaluación',
        'fecha': r['eval_fecha']
    }
    r['alumno'] = {
        'id': r.get('alumno_id'),
        'nombre_completo': f"{r.get('alumno_nombre') or ''} {r.get('alumno_apellido') or ''}".strip() or 'Alumno',
        'rut': r.get('alumno_rut') or ''
    }
    return r

# -------------------------------------------------------------
# DECORADORES DE ACCESO
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if session['user'].get('rol') not in roles:
                flash('No tienes permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.context_processor
def inject_context():
    user = session.get('user')
    t = date.today()
    dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    hoy_fmt = f"{dias[t.weekday()]}, {t.day} de {meses[t.month - 1]} de {t.year}"

    alumno_recups_count = 0
    if user and user.get('rol') == 'alumno' and user.get('alumno_id'):
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM recuperaciones WHERE alumno_id = %s AND estado = 'pendiente'", (user['alumno_id'],))
                r = cur.fetchone()
                if r:
                    alumno_recups_count = r['cnt']
            conn.close()
        except Exception:
            pass

    return dict(
        current_user=user,
        ROLES=ROLES,
        hoy=t.strftime('%Y-%m-%d'),
        today=t.strftime('%Y-%m-%d'),
        today_formatted=hoy_fmt,
        alumno_recups_count=alumno_recups_count,
        format_date=format_date
    )

# -------------------------------------------------------------
# AUTENTICACIÓN
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE LOWER(correo) = %s", (correo,))
                user = cur.fetchone()
            conn.close()
        except Exception as e:
            return render_template('login.html', error=f"Error al conectar a la base de datos: {e}", correo=correo)

        if not user or user.get('clave') != password:
            return render_template('login.html', error='Credenciales incorrectas.', correo=correo)
        if not user.get('activo', 1):
            return render_template('login.html', error='Cuenta inactiva por administración.', correo=correo)

        session['user'] = user
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))

# -------------------------------------------------------------
# DASHBOARD (INICIO)
# -------------------------------------------------------------
@app.route('/')
@login_required
def index():
    user = session['user']
    conn = get_db_connection()
    hoy = date.today().strftime('%Y-%m-%d')
    en_7 = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')

    with conn.cursor() as cur:
        if user['rol'] == 'alumno':
            alumno_id = user.get('alumno_id') or 1
            cur.execute("SELECT * FROM alumnos WHERE id = %s", (alumno_id,))
            alumno = cur.fetchone()
            curso_id = alumno['curso_id'] if alumno else 1

            cur.execute("""
                SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                       p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
                FROM evaluaciones e
                LEFT JOIN asignaturas a ON e.asignatura_id = a.id
                LEFT JOIN profesores p ON e.profesor_id = p.id
                LEFT JOIN cursos c ON e.curso_id = c.id
                WHERE e.curso_id = %s
                ORDER BY e.fecha ASC
            """, (curso_id,))
            evals = [enrich_eval(e) for e in cur.fetchall()]

            cur.execute("""
                SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                       a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                       p.nombre AS profe_nombre, p.apellido AS profe_apellido
                FROM recuperaciones r
                JOIN evaluaciones e ON r.evaluacion_id = e.id
                LEFT JOIN asignaturas a ON e.asignatura_id = a.id
                LEFT JOIN profesores p ON e.profesor_id = p.id
                WHERE r.alumno_id = %s
                ORDER BY (r.estado = 'pendiente') DESC, r.fecha_recuperacion ASC
            """, (alumno_id,))
            recuperaciones = [enrich_recup(r) for r in cur.fetchall()]
            recs_pendientes = [r for r in recuperaciones if r['estado'] == 'pendiente']

            cur.execute("""
                SELECT ae.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                       a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                       p.nombre AS profe_nombre, p.apellido AS profe_apellido
                FROM asistencia_evaluaciones ae
                JOIN evaluaciones e ON ae.evaluacion_id = e.id
                LEFT JOIN asignaturas a ON e.asignatura_id = a.id
                LEFT JOIN profesores p ON e.profesor_id = p.id
                WHERE ae.alumno_id = %s AND ae.estado_asistencia != 'presente'
                ORDER BY e.fecha DESC
            """, (alumno_id,))
            inasistencias = cur.fetchall()
            for inas in inasistencias:
                inas['eval_fecha'] = format_date(inas.get('eval_fecha'))
                inas['asignatura'] = {'nombre': inas.get('asignatura_nombre') or 'General', 'color': inas.get('asignatura_color') or '#14213D'}
                inas['profesor_nombre'] = f"{inas.get('profe_nombre') or ''} {inas.get('profe_apellido') or ''}".strip() or 'Docente'

            stats = {
                'total_evaluaciones': len(evals),
                'evals_semana': len([e for e in evals if hoy <= str(e['fecha']) <= en_7]),
                'recuperaciones_pendientes': len(recs_pendientes)
            }
            conn.close()
            return render_template(
                'index_alumno.html',
                title='Mi Panel de Alumno',
                active='dashboard',
                mis_evals=evals,
                mis_recuperaciones=recuperaciones,
                recuperaciones_pendientes=recs_pendientes,
                inasistencias=inasistencias,
                stats=stats,
                alumno=alumno
            )

        # UTP / Profesor / Inspectoría
        query_evals = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
        """
        params = []
        if user['rol'] == 'profe' and user.get('profesor_id'):
            query_evals += " WHERE e.profesor_id = %s"
            params.append(user['profesor_id'])
        query_evals += " ORDER BY e.fecha ASC, e.hora ASC"
        cur.execute(query_evals, params)
        todas_evals = [enrich_eval(e) for e in cur.fetchall()]

        cur.execute("SELECT COUNT(*) AS total FROM alumnos")
        total_alumnos = cur.fetchone()['total']

        cur.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut,
                   c.nombre AS curso_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            WHERE r.estado = 'pendiente'
            ORDER BY r.fecha_recuperacion ASC
        """)
        recups_pendientes = [enrich_recup(r) for r in cur.fetchall()]

    conn.close()

    evals_proximas = [e for e in todas_evals if str(e['fecha']) >= hoy]
    evals_semana = [e for e in todas_evals if hoy <= str(e['fecha']) <= en_7]

    stats = {
        'total_evaluaciones': len(todas_evals),
        'evals_semana': len(evals_semana),
        'total_alumnos': total_alumnos,
        'recuperaciones_pendientes': len(recups_pendientes)
    }

    return render_template(
        'dashboard.html',
        title='Panel de Control',
        active='dashboard',
        stats=stats,
        proximas_evaluaciones=evals_proximas[:6],
        recuperaciones_pendientes=recups_pendientes[:5]
    )

# -------------------------------------------------------------
# EVALUACIONES
# -------------------------------------------------------------
@app.route('/evaluaciones')
@login_required
def evaluaciones():
    user = session['user']
    curso_id = request.args.get('curso_id', type=int)
    asignatura_id = request.args.get('asignatura_id', type=int)
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    conn = get_db_connection()
    with conn.cursor() as cur:
        query = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE 1=1
        """
        params = []
        if user['rol'] == 'profe' and user.get('profesor_id'):
            query += " AND e.profesor_id = %s"
            params.append(user['profesor_id'])
        if curso_id:
            query += " AND e.curso_id = %s"
            params.append(curso_id)
        if asignatura_id:
            query += " AND e.asignatura_id = %s"
            params.append(asignatura_id)
        if fecha_desde:
            query += " AND e.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND e.fecha <= %s"
            params.append(fecha_hasta)

        query += " ORDER BY e.fecha DESC, e.hora ASC"
        cur.execute(query, params)
        evals = [enrich_eval(e) for e in cur.fetchall()]

        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()

        cur.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cur.fetchall()

    conn.close()
    return render_template(
        'evaluaciones/listar.html',
        title='Evaluaciones Calendarizadas',
        active='evaluaciones',
        evaluaciones=evals,
        cursos=cursos,
        asignaturas=asignaturas,
        filtros={'curso_id': curso_id, 'asignatura_id': asignatura_id, 'fecha_desde': fecha_desde, 'fecha_hasta': fecha_hasta}
    )

@app.route('/evaluaciones/crear', methods=['GET', 'POST'])
@login_required
@role_required('profe', 'utp')
def crear_evaluacion():
    user = session['user']
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip() or None
        curso_id = request.form.get('curso_id', type=int)
        asignatura_id = request.form.get('asignatura_id', type=int)

        if not titulo or not fecha or not curso_id or not asignatura_id:
            flash('Por favor completa todos los campos requeridos.', 'warning')
            conn.close()
            return redirect(url_for('crear_evaluacion'))

        # Regla de oro: Máximo 2 evaluaciones por curso al día
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM evaluaciones WHERE curso_id = %s AND fecha = %s", (curso_id, fecha))
            if cur.fetchone()['total'] >= 2:
                flash('El curso ya tiene 2 evaluaciones asignadas para esa fecha (límite máximo diario alcanzado).', 'danger')
                conn.close()
                return redirect(url_for('crear_evaluacion'))

            prof_id = user.get('profesor_id') or 1
            cur.execute("""
                INSERT INTO evaluaciones (titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (titulo, descripcion, fecha, hora, asignatura_id, curso_id, prof_id))
            nuevo_id = cur.lastrowid
        conn.close()

        flash(f'Evaluación "{titulo}" creada exitosamente.', 'success')
        return redirect(url_for('detalle_evaluacion', eval_id=nuevo_id))

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()
        cur.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cur.fetchall()
    conn.close()

    return render_template(
        'evaluaciones/crear.html',
        title='Nueva Evaluación',
        active='evaluaciones',
        cursos=cursos,
        asignaturas=asignaturas,
        hoy=date.today().strftime('%Y-%m-%d')
    )

@app.route('/evaluaciones/<int:eval_id>')
@login_required
def detalle_evaluacion(eval_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE e.id = %s
        """, (eval_id,))
        ev = enrich_eval(cur.fetchone())

        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('evaluaciones'))

        # Estudiantes del curso
        cur.execute("SELECT * FROM alumnos WHERE curso_id = %s ORDER BY apellido ASC, nombre ASC", (ev['curso_id'],))
        alumnos_raw = cur.fetchall()
        alumnos = []
        for al in alumnos_raw:
            al['nombre_completo'] = f"{al['nombre']} {al['apellido']}"
            alumnos.append(al)

        # Asistencias registradas
        cur.execute("SELECT * FROM asistencia_evaluaciones WHERE evaluacion_id = %s", (eval_id,))
        asist_list = cur.fetchall()
        asistencias = {a['alumno_id']: a for a in asist_list}

    conn.close()
    return render_template(
        'evaluaciones/detalle.html',
        title=ev['titulo'],
        active='evaluaciones',
        ev=ev,
        alumnos=alumnos,
        asistencias=asistencias
    )

@app.route('/evaluaciones/<int:eval_id>/asistencia', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def asistencia_evaluacion(eval_id):
    conn = get_db_connection()
    user = session['user']

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM evaluaciones WHERE id = %s", (eval_id,))
        ev = cur.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('evaluaciones'))

        cur.execute("SELECT id FROM alumnos WHERE curso_id = %s", (ev['curso_id'],))
        alumnos_ids = [a['id'] for a in cur.fetchall()]

        for a_id in alumnos_ids:
            if user['rol'] == 'inspe':
                estado = request.form.get(f'estado_{a_id}')
                motivo = request.form.get(f'motivo_{a_id}', '').strip()
                if estado:
                    presente = 1 if estado == 'presente' else 0
                    justificado = 1 if estado in ['justificado', 'salida'] else 0
                    cur.execute("""
                        INSERT INTO asistencia_evaluaciones (evaluacion_id, alumno_id, estado_asistencia, presente, justificado, motivo_inasistencia)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE estado_asistencia = VALUES(estado_asistencia), presente = VALUES(presente),
                                                justificado = VALUES(justificado), motivo_inasistencia = VALUES(motivo_inasistencia)
                    """, (eval_id, a_id, estado, presente, justificado, motivo))

                    # Si fue inasistencia, registrar o actualizar recuperación
                    if not presente:
                        exigencia = 60.00 if justificado else 70.00
                        cur.execute("""
                            INSERT INTO recuperaciones (evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado)
                            VALUES (%s, %s, DATE_ADD(CURDATE(), INTERVAL 7 DAY), %s, %s, 'pendiente')
                            ON DUPLICATE KEY UPDATE exigencia = VALUES(exigencia), motivo = VALUES(motivo)
                        """, (eval_id, a_id, motivo or 'Inasistencia a evaluación', exigencia))
            else:
                asist_val = request.form.get(f'asist_{a_id}')
                if asist_val:
                    presente = 1 if asist_val == 'presente' else 0
                    cur.execute("""
                        INSERT INTO asistencia_evaluaciones (evaluacion_id, alumno_id, estado_asistencia, presente, justificado)
                        VALUES (%s, %s, %s, %s, 0)
                        ON DUPLICATE KEY UPDATE estado_asistencia = VALUES(estado_asistencia), presente = VALUES(presente)
                    """, (eval_id, a_id, asist_val, presente))
                    if not presente:
                        cur.execute("""
                            INSERT INTO recuperaciones (evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado)
                            VALUES (%s, %s, DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'Inasistencia sin justificar', 70.00, 'pendiente')
                            ON DUPLICATE KEY UPDATE estado = VALUES(estado)
                        """, (eval_id, a_id))

        if user['rol'] != 'inspe':
            cur.execute("UPDATE evaluaciones SET asistencia_guardada = 1 WHERE id = %s", (eval_id,))
            flash('Lista de asistencia del curso guardada y cerrada exitosamente.', 'success')
        else:
            flash('Justificaciones médicas acreditadas exitosamente por Inspectoría General.', 'success')
    return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

@app.route('/evaluaciones/api/disponibilidad')
@login_required
def api_disponibilidad():
    curso_id = request.args.get('curso_id', type=int)
    fecha = request.args.get('fecha', '')
    if not curso_id or not fecha:
        return jsonify({'error': 'Parámetros inválidos'}), 400

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM evaluaciones WHERE curso_id = %s AND fecha = %s", (curso_id, fecha))
        existentes = cur.fetchone()['total']
    conn.close()

    return jsonify({
        'curso_id': curso_id,
        'fecha': fecha,
        'existentes': existentes,
        'disponibles': max(0, 2 - existentes)
    })

@app.route('/evaluaciones/<int:eval_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('profe', 'utp')
def editar_evaluacion(eval_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM evaluaciones WHERE id = %s", (eval_id,))
        ev = cur.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('evaluaciones'))

        if request.method == 'POST':
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            fecha = request.form.get('fecha', '').strip()
            hora = request.form.get('hora', '').strip() or None
            curso_id = request.form.get('curso_id', type=int)
            asignatura_id = request.form.get('asignatura_id', type=int)

            cur.execute("""
                UPDATE evaluaciones
                SET titulo = %s, descripcion = %s, fecha = %s, hora = %s, curso_id = %s, asignatura_id = %s
                WHERE id = %s
            """, (titulo, descripcion, fecha, hora, curso_id, asignatura_id, eval_id))
            conn.close()
            flash('Evaluación actualizada correctamente.', 'success')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()
        cur.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cur.fetchall()

    conn.close()
    ev['fecha'] = format_date(ev.get('fecha'))
    ev['hora'] = format_time(ev.get('hora'))
    return render_template(
        'evaluaciones/editar.html',
        title='Editar Evaluación',
        active='evaluaciones',
        ev=ev,
        cursos=cursos,
        asignaturas=asignaturas
    )

@app.route('/evaluaciones/<int:eval_id>/eliminar', methods=['POST'])
@login_required
@role_required('profe', 'utp')
def eliminar_evaluacion(eval_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM evaluaciones WHERE id = %s", (eval_id,))
    conn.close()
    flash('Evaluación eliminada correctamente.', 'info')
    return redirect(url_for('evaluaciones'))

# -------------------------------------------------------------
# RECUPERACIONES
# -------------------------------------------------------------
@app.route('/recuperaciones')
@login_required
def recuperaciones():
    user = session['user']
    conn = get_db_connection()
    with conn.cursor() as cur:
        query = """
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut,
                   c.nombre AS curso_nombre, a.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            WHERE 1=1
        """
        params = []
        if user['rol'] == 'alumno':
            query += " AND r.alumno_id = %s"
            params.append(user.get('alumno_id') or 1)
        elif user['rol'] == 'profe' and user.get('profesor_id'):
            query += " AND e.profesor_id = %s"
            params.append(user['profesor_id'])

        query += " ORDER BY (r.estado = 'pendiente') DESC, r.fecha_recuperacion ASC"
        cur.execute(query, params)
        recs = [enrich_recup(r) for r in cur.fetchall()]
    conn.close()

    return render_template(
        'recuperaciones/listar.html',
        title='Evaluaciones de Recuperación',
        active='recuperaciones',
        recuperaciones=recs
    )

@app.route('/recuperaciones/crear', methods=['GET', 'POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def crear_recuperacion():
    conn = get_db_connection()
    if request.method == 'POST':
        evaluacion_id = request.form.get('evaluacion_id', type=int)
        alumno_id = request.form.get('alumno_id', type=int)
        fecha_recup = request.form.get('fecha_recuperacion', '').strip()
        motivo = request.form.get('motivo', '').strip()
        tipo_just = request.form.get('tipo_justificacion', 'injustificada')
        exigencia = 60.00 if tipo_just in ['medica', 'salida_pedagogica', 'justificado'] else 70.00

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recuperaciones (evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado)
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """, (evaluacion_id, alumno_id, fecha_recup, motivo, exigencia))
        conn.close()
        flash('Recuperación programada exitosamente.', 'success')
        return redirect(url_for('recuperaciones'))

    with conn.cursor() as cur:
        cur.execute("SELECT id, titulo, fecha FROM evaluaciones ORDER BY fecha DESC LIMIT 50")
        evaluaciones_list = cur.fetchall()
        cur.execute("SELECT a.id, a.nombre, a.apellido, a.rut, c.nombre AS curso_nombre FROM alumnos a JOIN cursos c ON a.curso_id = c.id ORDER BY c.nombre, a.apellido")
        alumnos_list = cur.fetchall()
        for a in alumnos_list:
            a['nombre_completo'] = f"{a['nombre']} {a['apellido']}"
    conn.close()

    return render_template(
        'recuperaciones/crear.html',
        title='Agendar Recuperación',
        active='recuperaciones',
        evaluaciones=evaluaciones_list,
        alumnos=alumnos_list
    )

@app.route('/recuperaciones/<int:recup_id>/estado', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def cambiar_estado_recuperacion(recup_id):
    nuevo_estado = request.form.get('estado', 'completada')
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE recuperaciones SET estado = %s WHERE id = %s", (nuevo_estado, recup_id))
    conn.close()
    flash(f'Recuperación marcada como {nuevo_estado}.', 'success')
    return redirect(url_for('recuperaciones'))

# -------------------------------------------------------------
# ALUMNOS
# -------------------------------------------------------------
@app.route('/alumnos')
@login_required
def alumnos():
    curso_id = request.args.get('curso_id', type=int)
    conn = get_db_connection()
    with conn.cursor() as cur:
        query = "SELECT a.*, c.nombre AS curso_nombre, c.nivel AS curso_nivel FROM alumnos a JOIN cursos c ON a.curso_id = c.id"
        params = []
        if curso_id:
            query += " WHERE a.curso_id = %s"
            params.append(curso_id)
        query += " ORDER BY c.nombre, a.apellido, a.nombre"
        cur.execute(query, params)
        alumnos_list = cur.fetchall()
        for a in alumnos_list:
            a['nombre_completo'] = f"{a['nombre']} {a['apellido']}"

        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()
    conn.close()

    return render_template('alumnos/listar.html', title='Estudiantes', active='alumnos', alumnos=alumnos_list, cursos=cursos, filtro_curso=curso_id)

@app.route('/alumnos/<int:alumno_id>')
@login_required
def perfil_alumno(alumno_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT a.*, c.nombre AS curso_nombre, c.nivel AS curso_nivel FROM alumnos a JOIN cursos c ON a.curso_id = c.id WHERE a.id = %s", (alumno_id,))
        alumno = cur.fetchone()
        if not alumno:
            conn.close()
            flash('Estudiante no encontrado.', 'danger')
            return redirect(url_for('alumnos'))
        alumno['nombre_completo'] = f"{alumno['nombre']} {alumno['apellido']}"

        cur.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha, a.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            WHERE r.alumno_id = %s
            ORDER BY r.fecha_recuperacion DESC
        """, (alumno_id,))
        recups = [enrich_recup(r) for r in cur.fetchall()]
    conn.close()

    return render_template('alumnos/perfil.html', title=alumno['nombre_completo'], active='alumnos', alumno=alumno, recuperaciones=recups)

# -------------------------------------------------------------
# CALENDARIO Y REPORTES
# -------------------------------------------------------------
@app.route('/reportes/calendario')
@login_required
def reporte_calendario():
    today = date.today()
    mes = request.args.get('mes', type=int) or today.month
    anio = request.args.get('anio', type=int) or today.year
    curso_id = request.args.get('curso_id', type=int)

    meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    meses_list = [{'num': i + 1, 'nombre': m} for i, m in enumerate(meses_nombres)]

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()

        query = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE YEAR(e.fecha) = %s AND MONTH(e.fecha) = %s
        """
        params = [anio, mes]
        if curso_id:
            query += " AND e.curso_id = %s"
            params.append(curso_id)
        query += " ORDER BY e.fecha ASC, e.hora ASC"
        cur.execute(query, params)
        evals = cur.fetchall()
    conn.close()

    evals_por_dia = {}
    for ev in evals:
        ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
        ev['curso'] = {'nombre': ev['curso_nombre']}
        dia_num = ev['fecha'].day if hasattr(ev['fecha'], 'day') else int(str(ev['fecha']).split('-')[2])
        if dia_num not in evals_por_dia:
            evals_por_dia[dia_num] = []
        evals_por_dia[dia_num].append(ev)

    semanas = calendar.monthcalendar(anio, mes)
    prev_mes = mes - 1 if mes > 1 else 12
    prev_anio = anio if mes > 1 else anio - 1
    next_mes = mes + 1 if mes < 12 else 1
    next_anio = anio if mes < 12 else anio + 1

    return render_template(
        'reportes/calendario.html',
        title='Calendario de Evaluaciones',
        active='calendario',
        mes=mes,
        anio=anio,
        mes_nombre=meses_nombres[mes - 1],
        meses=meses_list,
        semanas=semanas,
        evals_por_dia=evals_por_dia,
        cursos=cursos,
        filtros={'curso_id': curso_id},
        prevMes=prev_mes,
        prevAnio=prev_anio,
        nextMes=next_mes,
        nextAnio=next_anio,
        today_day=today.day,
        today_month=today.month,
        today_year=today.year
    )

@app.route('/reportes/pendientes')
@login_required
def reporte_pendientes():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut,
                   c.nombre AS curso_nombre, a.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            WHERE r.estado = 'pendiente'
            ORDER BY e.fecha ASC
        """)
        recs = [enrich_recup(r) for r in cur.fetchall()]
    conn.close()

    agrupadas = {}
    for r in recs:
        ev_id = r['evaluacion_id']
        if ev_id not in agrupadas:
            agrupadas[ev_id] = []
        agrupadas[ev_id].append(r)

    return render_template(
        'reportes/pendientes.html',
        title='Alumnos Pendientes de Recuperación',
        active='pendientes',
        alumnos_por_eval=agrupadas
    )

@app.route('/reportes/carga')
@login_required
def reporte_carga():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()

        cur.execute("""
            SELECT fecha, curso_id, COUNT(*) AS total
            FROM evaluaciones
            GROUP BY fecha, curso_id
            HAVING total >= 2
            ORDER BY fecha DESC
        """)
        dias_saturados = cur.fetchall()
    conn.close()

    return render_template(
        'reportes/carga.html',
        title='Carga Académica y Límites Diarios',
        active='carga',
        cursos=cursos,
        dias_saturados=dias_saturados
    )

# -------------------------------------------------------------
# ADMINISTRACIÓN
# -------------------------------------------------------------
@app.route('/admin')
@login_required
@role_required('utp')
def admin_panel():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM cursos")
        total_cursos = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM asignaturas")
        total_asig = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM profesores")
        total_prof = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS total FROM usuarios")
        total_users = cur.fetchone()['total']
    conn.close()

    stats = {
        'cursos': total_cursos,
        'asignaturas': total_asig,
        'profesores': total_prof,
        'usuarios': total_users
    }
    return render_template('admin/index.html', title='Administración', active='admin', stats=stats)

@app.route('/admin/cursos', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_cursos():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        nivel = request.form.get('nivel', '').strip()
        if nombre and nivel:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO cursos (nombre, nivel) VALUES (%s, %s)", (nombre, nivel))
            flash(f'Curso {nombre} agregado.', 'success')
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cur.fetchall()
    conn.close()
    return render_template('admin/cursos.html', title='Gestión de Cursos', active='admin', cursos=cursos)

@app.route('/admin/asignaturas', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_asignaturas():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        color = request.form.get('color', '#14213D').strip()
        if nombre:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO asignaturas (nombre, color) VALUES (%s, %s)", (nombre, color))
            flash(f'Asignatura {nombre} creada.', 'success')
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cur.fetchall()
    conn.close()
    return render_template('admin/asignaturas.html', title='Gestión de Asignaturas', active='admin', asignaturas=asignaturas)

@app.route('/admin/profesores', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_profesores():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip().lower()
        materia = request.form.get('materia', '').strip()
        if nombre and apellido and email:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO profesores (nombre, apellido, email, materia) VALUES (%s, %s, %s, %s)", (nombre, apellido, email, materia))
            flash(f'Profesor {nombre} {apellido} registrado.', 'success')
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM profesores ORDER BY apellido ASC, nombre ASC")
        profesores = cur.fetchall()
    conn.close()
    return render_template('admin/profesores.html', title='Gestión de Profesores', active='admin', profesores=profesores)

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_usuarios():
    conn = get_db_connection()
    if request.method == 'POST':
        rut = request.form.get('rut', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        nombre = request.form.get('nombre', '').strip()
        clave = request.form.get('clave', '').strip()
        rol = request.form.get('rol', 'profe')
        if rut and correo and nombre and clave:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO usuarios (rut, correo, clave, nombre, rol)
                    VALUES (%s, %s, %s, %s, %s)
                """, (rut, correo, clave, nombre, rol))
            flash(f'Usuario {nombre} creado.', 'success')
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM usuarios ORDER BY nombre ASC")
        usuarios = cur.fetchall()
    conn.close()
    return render_template('admin/usuarios.html', title='Gestión de Usuarios', active='admin', usuarios=usuarios)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
