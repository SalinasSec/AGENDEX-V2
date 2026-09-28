# -*- coding: utf-8 -*-
"""
AgendEx - Sistema de Gestión de Evaluaciones Escolares
Backend en Flask con Base de Datos MySQL
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
# DECORADORES Y CONTEXTO
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if session['user']['rol'] not in roles:
                flash('No tienes permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.context_processor
def inject_context():
    user = session.get('user')
    hoy = date.today().strftime('%Y-%m-%d')
    hoy_fmt = date.today().strftime('%d/%m/%Y')
    return dict(
        current_user=user,
        ROLES=ROLES,
        today=hoy,
        today_formatted=hoy_fmt
    )

# -------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN
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
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE LOWER(correo) = %s",
                    (correo,)
                )
                user = cursor.fetchone()
            conn.close()
        except Exception as e:
            return render_template('login.html', error=f"Error al conectar con la base de datos: {e}", correo=correo)

        if not user or user['clave'] != password:
            return render_template('login.html', error='Correo o contraseña incorrectos.', correo=correo)

        if not user.get('activo', 1):
            return render_template('login.html', error='Esta cuenta está desactivada por administración.', correo=correo)

        session['user'] = {
            'id': user['id'],
            'rut': user['rut'],
            'correo': user['correo'],
            'nombre': user['nombre'],
            'rol': user['rol'],
            'profesor_id': user.get('profesor_id'),
            'alumno_id': user.get('alumno_id')
        }

        flash(f'¡Bienvenido(a), {user["nombre"]}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', error=None, correo='')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

# -------------------------------------------------------------
# DASHBOARD
# -------------------------------------------------------------
@app.route('/')
@login_required
def index():
    user = session['user']
    conn = get_db_connection()
    hoy = date.today().strftime('%Y-%m-%d')
    hace_7 = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    en_7 = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')

    with conn.cursor() as cursor:
        if user['rol'] == 'alumno':
            # Vista del alumno
            alumno_id = user['alumno_id'] or 1
            cursor.execute("SELECT * FROM alumnos WHERE id = %s", (alumno_id,))
            alumno = cursor.fetchone()
            curso_id = alumno['curso_id'] if alumno else 1

            cursor.execute("""
                SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                       p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
                FROM evaluaciones e
                JOIN asignaturas a ON e.asignatura_id = a.id
                JOIN profesores p ON e.profesor_id = p.id
                JOIN cursos c ON e.curso_id = c.id
                WHERE e.curso_id = %s
                ORDER BY e.fecha ASC
            """, (curso_id,))
            evals = cursor.fetchall()

            for ev in evals:
                ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
                ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
                ev['curso'] = {'nombre': ev['curso_nombre']}

            cursor.execute("""
                SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha
                FROM recuperaciones r
                JOIN evaluaciones e ON r.evaluacion_id = e.id
                WHERE r.alumno_id = %s AND r.estado = 'pendiente'
                ORDER BY r.fecha_recuperacion ASC
            """, (alumno_id,))
            recuperaciones = cursor.fetchall()

            stats = {
                'total_evaluaciones': len(evals),
                'evals_semana': len([e for e in evals if hoy <= str(e['fecha']) <= en_7]),
                'recuperaciones_pendientes': len(recuperaciones)
            }
            conn.close()
            return render_template(
                'index_alumno.html',
                title='Mi Panel de Alumno',
                active='dashboard',
                mis_evals=evals,
                mis_recuperaciones=recuperaciones,
                stats=stats,
                alumno=alumno
            )

        # Vista de UTP / Profesor / Inspectoría
        query_evals = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            ORDER BY e.fecha ASC, e.hora ASC
        """
        cursor.execute(query_evals)
        todas_evals = cursor.fetchall()

        for ev in todas_evals:
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
            ev['curso'] = {'nombre': ev['curso_nombre']}

        cursor.execute("SELECT COUNT(*) AS total FROM cursos")
        total_cursos = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM alumnos")
        total_alumnos = cursor.fetchone()['total']

        cursor.execute("""
            SELECT r.*, e.titulo AS eval_titulo, a.nombre AS alumno_nombre, a.apellido AS alumno_apellido, c.nombre AS curso_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos a ON r.alumno_id = a.id
            JOIN cursos c ON a.curso_id = c.id
            WHERE r.estado = 'pendiente'
        """)
        recuperaciones_pendientes = cursor.fetchall()
        for r in recuperaciones_pendientes:
            r['alumno'] = {'nombre': r['alumno_nombre'], 'apellido': r['alumno_apellido'], 'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}"}
            r['curso'] = {'nombre': r['curso_nombre']}

        cursor.execute("""
            SELECT c.nombre AS curso_nombre, COUNT(e.id) AS count
            FROM cursos c
            LEFT JOIN evaluaciones e ON c.id = e.curso_id
            GROUP BY c.id, c.nombre
            ORDER BY count DESC
        """)
        evals_por_curso = cursor.fetchall()

    conn.close()

    evals_hoy = [e for e in todas_evals if str(e['fecha']) == hoy]
    evals_semana = [e for e in todas_evals if hoy <= str(e['fecha']) <= en_7]

    return render_template(
        'dashboard.html',
        title='Dashboard',
        active='dashboard',
        evals_hoy=evals_hoy,
        evals_semana=evals_semana,
        recuperaciones_pendientes=recuperaciones_pendientes,
        total_cursos=total_cursos,
        total_alumnos=total_alumnos,
        evals_por_curso=evals_por_curso
    )

# -------------------------------------------------------------
# EVALUACIONES
# -------------------------------------------------------------
@app.route('/evaluaciones')
@login_required
def listar_evaluaciones():
    conn = get_db_connection()
    curso_id = request.args.get('curso_id', '').strip()
    asignatura_id = request.args.get('asignatura_id', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()
        cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cursor.fetchall()

        query = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE 1=1
        """
        params = []
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
        cursor.execute(query, params)
        evaluaciones = cursor.fetchall()

        # Si el usuario es Inspectoría, filtrar únicamente evaluaciones con inasistencias registradas
        if session['user']['rol'] == 'inspe':
            cursor.execute("""
                SELECT DISTINCT evaluacion_id 
                FROM asistencia_evaluaciones 
                WHERE (estado_asistencia != 'presente' AND estado_asistencia IS NOT NULL) OR presente = 0
            """)
            eval_ids_con_inasistencias = {row['evaluacion_id'] for row in cursor.fetchall()}
            evaluaciones = [e for e in evaluaciones if e['id'] in eval_ids_con_inasistencias]

        for ev in evaluaciones:
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
            ev['curso'] = {'nombre': ev['curso_nombre']}

    conn.close()
    return render_template(
        'evaluaciones/listar.html',
        title='Evaluaciones con Inasistencias' if session['user']['rol'] == 'inspe' else 'Gestión de Evaluaciones',
        active='evaluaciones',
        evaluaciones=evaluaciones,
        cursos=cursos,
        asignaturas=asignaturas,
        filtros={
            'curso_id': int(curso_id) if curso_id.isdigit() else curso_id,
            'asignatura_id': int(asignatura_id) if asignatura_id.isdigit() else asignatura_id,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta
        }
    )

@app.route('/evaluaciones/crear', methods=['GET', 'POST'])
@login_required
@role_required('profe', 'utp')
def crear_evaluacion():
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip() or None
        asignatura_id = request.form.get('asignatura_id')
        curso_id = request.form.get('curso_id')
        profesor_id = session['user'].get('profesor_id') or 1

        with conn.cursor() as cursor:
            # 1. Validación estricta de 2 evaluaciones diarias por curso (MySQL SP o query)
            cursor.execute(
                "SELECT COUNT(*) AS total FROM evaluaciones WHERE curso_id = %s AND fecha = %s",
                (curso_id, fecha)
            )
            total = cursor.fetchone()['total']

            if total >= 2:
                flash('No se puede crear la evaluación: límite máximo diario alcanzado (máximo 2 evaluaciones por día para este curso).', 'danger')
                conn.close()
                return redirect(url_for('crear_evaluacion'))

            # Inserción
            cursor.execute("""
                INSERT INTO evaluaciones (titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id))

        conn.close()
        flash('Evaluación calendarizada exitosamente.', 'success')
        return redirect(url_for('listar_evaluaciones'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()
        cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cursor.fetchall()
    conn.close()

    return render_template(
        'evaluaciones/crear.html',
        title='Calendarizar Evaluación',
        active='evaluaciones',
        cursos=cursos,
        asignaturas=asignaturas
    )

@app.route('/evaluaciones/<int:eval_id>')
@login_required
def detalle_evaluacion(eval_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE e.id = %s
        """, (eval_id,))
        ev = cursor.fetchone()

        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
        ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
        ev['curso'] = {'nombre': ev['curso_nombre'], 'nivel': ev.get('curso_nivel', 'Media')}

        # Alumnos del curso
        cursor.execute("""
            SELECT id, rut, nombre, apellido, CONCAT(nombre, ' ', apellido) as nombre_completo
            FROM alumnos
            WHERE curso_id = %s
            ORDER BY apellido ASC, nombre ASC
        """, (ev['curso_id'],))
        alumnos = cursor.fetchall()

        # Asistencia registrada
        cursor.execute("""
            SELECT * FROM asistencia_evaluaciones
            WHERE evaluacion_id = %s
        """, (eval_id,))
        asistencias_raw = cursor.fetchall()
        asistencias_map = {}
        for a in asistencias_raw:
            asistencias_map[a['alumno_id']] = {
                'presente': a.get('presente', 1),
                'justificado': a.get('justificado', 0),
                'estado_asistencia': a.get('estado_asistencia') or ('justificado' if a.get('justificado') else ('presente' if a.get('presente') else 'injustificada')),
                'motivo': a.get('motivo_inasistencia') or ''
            }

        # Para Inspectoría: filtrar solo los alumnos con inasistencia
        alumnos_afectados = alumnos
        if session['user']['rol'] == 'inspe':
            alumnos_afectados = [
                a for a in alumnos
                if a['id'] in asistencias_map and asistencias_map[a['id']]['estado_asistencia'] != 'presente'
            ]

    conn.close()
    return render_template(
        'evaluaciones/detalle.html',
        title=ev['titulo'],
        active='evaluaciones',
        ev=ev,
        evaluacion=ev,
        alumnos=alumnos,
        alumnos_afectados=alumnos_afectados,
        asistencias=asistencias_map
    )

@app.route('/evaluaciones/<int:eval_id>/asistencia', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def asistencia_evaluacion(eval_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM evaluaciones WHERE id = %s", (eval_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        user_rol = session['user']['rol']

        # Si el profesor intenta modificar una lista ya guardada, se bloquea
        if user_rol == 'profe' and ev.get('asistencia_guardada'):
            conn.close()
            flash('La asistencia ya fue registrada y cerrada oficialmente. Las modificaciones corresponden a Inspectoría.', 'warning')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        cursor.execute("SELECT id FROM alumnos WHERE curso_id = %s", (ev['curso_id'],))
        alumnos = cursor.fetchall()

        for a in alumnos:
            aid = a['id']
            estado_enviado = request.form.get(f'estado_{aid}')
            motivo_enviado = request.form.get(f'motivo_{aid}', '').strip()

            cursor.execute("SELECT * FROM asistencia_evaluaciones WHERE evaluacion_id = %s AND alumno_id = %s", (eval_id, aid))
            existing = cursor.fetchone()

            estado_final = 'presente'
            if user_rol == 'inspe':
                if estado_enviado:
                    estado_final = estado_enviado
                elif existing and existing.get('estado_asistencia'):
                    estado_final = existing['estado_asistencia']
                else:
                    estado_final = 'injustificada'
            else:
                # Profesor
                if estado_enviado == 'presente':
                    estado_final = 'presente'
                elif estado_enviado == 'salida':
                    estado_final = 'salida'
                else:
                    if existing and existing.get('estado_asistencia') == 'justificado':
                        estado_final = 'justificado'
                    else:
                        estado_final = 'injustificada'

            presente = 1 if estado_final == 'presente' else 0
            justificado = 1 if estado_final in ('justificado', 'salida') else 0
            motivo = motivo_enviado if estado_final != 'presente' else None

            cursor.execute("""
                INSERT INTO asistencia_evaluaciones (evaluacion_id, alumno_id, estado_asistencia, presente, justificado, motivo_inasistencia)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                estado_asistencia=VALUES(estado_asistencia),
                presente=VALUES(presente),
                justificado=VALUES(justificado),
                motivo_inasistencia=VALUES(motivo_inasistencia)
            """, (eval_id, aid, estado_final, presente, justificado, motivo))

        # Si el profesor guarda, se marca la evaluación como asistencia cerrada
        if user_rol == 'profe':
            cursor.execute("UPDATE evaluaciones SET asistencia_guardada = 1 WHERE id = %s", (eval_id,))

        conn.commit()

    conn.close()
    flash('Asistencia actualizada correctamente.', 'success')
    return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

@app.route('/evaluaciones/api/disponibilidad')
@login_required
def api_disponibilidad():
    curso_id = request.args.get('curso_id')
    fecha = request.args.get('fecha')
    if not curso_id or not fecha:
        return jsonify({'error': 'Parámetros faltantes'}), 400

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM evaluaciones WHERE curso_id = %s AND fecha = %s",
            (curso_id, fecha)
        )
        total = cursor.fetchone()['total']
    conn.close()

    return jsonify({
        'curso_id': int(curso_id),
        'fecha': fecha,
        'total': total,
        'hay_lugar': total < 2
    })

@app.route('/evaluaciones/<int:eval_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('profe', 'utp')
def editar_evaluacion(eval_id):
    conn = get_db_connection()
    user = session['user']
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE e.id = %s
        """, (eval_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        if user['rol'] == 'profe' and user.get('profesor_id') and ev['profesor_id'] != user['profesor_id']:
            conn.close()
            flash('No tienes permiso para editar evaluaciones de otros profesores.', 'danger')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        if request.method == 'POST':
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            fecha = request.form.get('fecha', '').strip()
            hora = request.form.get('hora', '').strip() or None
            curso_id = request.form.get('curso_id')
            asignatura_id = request.form.get('asignatura_id')

            # Validar límite de 2 evaluaciones si cambia fecha o curso
            if str(ev['fecha']) != fecha or str(ev['curso_id']) != str(curso_id):
                cursor.execute(
                    "SELECT COUNT(*) AS total FROM evaluaciones WHERE curso_id = %s AND fecha = %s AND id != %s",
                    (curso_id, fecha, eval_id)
                )
                if cursor.fetchone()['total'] >= 2:
                    conn.close()
                    flash('No se puede cambiar la fecha: ese curso ya tiene 2 evaluaciones ese día.', 'danger')
                    return redirect(url_for('editar_evaluacion', eval_id=eval_id))

            cursor.execute("""
                UPDATE evaluaciones
                SET titulo = %s, descripcion = %s, fecha = %s, hora = %s, curso_id = %s, asignatura_id = %s
                WHERE id = %s
            """, (titulo, descripcion, fecha, hora, curso_id, asignatura_id, eval_id))
            conn.commit()
            conn.close()
            flash('Evaluación actualizada correctamente.', 'success')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()
        cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cursor.fetchall()

    conn.close()
    ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
    ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
    ev['curso'] = {'nombre': ev['curso_nombre'], 'nivel': ev.get('curso_nivel', 'Media')}
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
    user = session['user']
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM evaluaciones WHERE id = %s", (eval_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        if user['rol'] == 'profe' and user.get('profesor_id') and ev['profesor_id'] != user['profesor_id']:
            conn.close()
            flash('No tienes permiso para eliminar evaluaciones de otros profesores.', 'danger')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        cursor.execute("DELETE FROM recuperaciones WHERE evaluacion_id = %s", (eval_id,))
        cursor.execute("DELETE FROM asistencia_evaluaciones WHERE evaluacion_id = %s", (eval_id,))
        cursor.execute("DELETE FROM evaluaciones WHERE id = %s", (eval_id,))
        conn.commit()
    conn.close()
    flash('Evaluación eliminada correctamente.', 'info')
    return redirect(url_for('listar_evaluaciones'))

# -------------------------------------------------------------
# RECUPERACIONES
# -------------------------------------------------------------
@app.route('/recuperaciones')
@login_required
def listar_recuperaciones():
    conn = get_db_connection()
    estado = request.args.get('estado', '').strip()
    user = session.get('user', {})

    with conn.cursor() as cursor:
        query = """
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut,
                   c.nombre AS curso_nombre, asig.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            JOIN asignaturas asig ON e.asignatura_id = asig.id
            WHERE 1=1
        """
        params = []
        if user.get('rol') == 'profe' and user.get('profesor_id'):
            query += " AND e.profesor_id = %s"
            params.append(user['profesor_id'])
        elif user.get('rol') == 'alumno' and user.get('alumno_id'):
            query += " AND r.alumno_id = %s"
            params.append(user['alumno_id'])

        if estado:
            if estado in ['completada', 'rendida']:
                query += " AND r.estado IN ('completada', 'rendida')"
            else:
                query += " AND r.estado = %s"
                params.append(estado)

        query += " ORDER BY r.fecha_recuperacion DESC"
        cursor.execute(query, params)
        recuperaciones = cursor.fetchall()

        for r in recuperaciones:
            r['alumno'] = {'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}", 'rut': r['alumno_rut'], 'curso': {'nombre': r['curso_nombre']}}
            r['evaluacion'] = {'titulo': r['eval_titulo'], 'fecha': r['eval_fecha'], 'asignatura': {'nombre': r['asignatura_nombre']}}
            r['porcentaje_exigencia'] = float(r.get('exigencia') or r.get('porcentaje_exigencia') or 60)

    conn.close()
    return render_template(
        'recuperaciones/listar.html',
        title='Evaluaciones de Recuperación',
        active='recuperaciones',
        recuperaciones=recuperaciones,
        filtros={'estado': estado}
    )

@app.route('/recuperaciones/crear', methods=['GET', 'POST'])
@login_required
@role_required('inspe', 'utp', 'profe')
def crear_recuperacion():
    conn = get_db_connection()

    if request.method == 'POST':
        evaluacion_id = request.form.get('evaluacion_id')
        alumno_id = request.form.get('alumno_id')
        fecha_recup = request.form.get('fecha_recuperacion')
        motivo = request.form.get('motivo', '').strip()

        # Revisar si la inasistencia estaba justificada
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT justificado FROM asistencia_evaluaciones
                WHERE evaluacion_id = %s AND alumno_id = %s
            """, (evaluacion_id, alumno_id))
            asist = cursor.fetchone()

            # Regla de exigencia: 60% justificado, 70% injustificado
            exigencia = 60.00 if (asist and asist['justificado']) else 70.00

            cursor.execute("""
                INSERT INTO recuperaciones (evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado)
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """, (evaluacion_id, alumno_id, fecha_recup, motivo, exigencia))
            conn.commit()

        conn.close()
        flash(f'Recuperación agendada con éxito ({int(exigencia)}% de exigencia).', 'success')
        return redirect(url_for('listar_recuperaciones'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM evaluaciones ORDER BY fecha DESC")
        evaluaciones = cursor.fetchall()
        cursor.execute("SELECT * FROM alumnos ORDER BY apellido ASC")
        alumnos = cursor.fetchall()
    conn.close()

    return render_template(
        'recuperaciones/crear.html',
        title='Agendar Recuperación',
        active='recuperaciones',
        evaluaciones=evaluaciones,
        alumnos=alumnos
    )

@app.route('/recuperaciones/<int:recup_id>/completar', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def completar_recuperacion(recup_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE recuperaciones SET estado = 'completada' WHERE id = %s", (recup_id,))
        conn.commit()
    conn.close()
    flash('Recuperación marcada como completada.', 'success')
    return redirect(url_for('listar_recuperaciones'))

@app.route('/recuperaciones/<int:recup_id>/cancelar', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def cancelar_recuperacion(recup_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE recuperaciones SET estado = 'cancelada' WHERE id = %s", (recup_id,))
        conn.commit()
    conn.close()
    flash('Recuperación cancelada.', 'info')
    return redirect(url_for('listar_recuperaciones'))

@app.route('/recuperaciones/<int:recup_id>/estado', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def cambiar_estado_recuperacion(recup_id):
    nuevo_estado = request.form.get('estado')
    if nuevo_estado in ['pendiente', 'completada', 'rendida', 'cancelada']:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE recuperaciones SET estado = %s WHERE id = %s", (nuevo_estado, recup_id))
            conn.commit()
        conn.close()
        flash('Estado de recuperación actualizado.', 'success')
    return redirect(url_for('listar_recuperaciones'))

# -------------------------------------------------------------
# ALUMNOS
# -------------------------------------------------------------
@app.route('/alumnos')
@login_required
def listar_alumnos():
    conn = get_db_connection()
    busqueda = request.args.get('busqueda', '').strip()
    curso_id = request.args.get('curso_id', '').strip()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()

        query = """
            SELECT al.*, c.nombre AS curso_nombre
            FROM alumnos al
            JOIN cursos c ON al.curso_id = c.id
            WHERE 1=1
        """
        params = []
        if busqueda:
            query += " AND (al.nombre LIKE %s OR al.apellido LIKE %s OR al.rut LIKE %s)"
            term = f"%{busqueda}%"
            params.extend([term, term, term])
        if curso_id:
            query += " AND al.curso_id = %s"
            params.append(curso_id)

        query += " ORDER BY c.nombre ASC, al.apellido ASC, al.nombre ASC"
        cursor.execute(query, params)
        alumnos = cursor.fetchall()
        for a in alumnos:
            a['curso'] = {'nombre': a['curso_nombre']}
            a['nombre_completo'] = f"{a['nombre']} {a['apellido']}"
    conn.close()

    return render_template(
        'alumnos/listar.html',
        title='Nómina de Alumnos',
        active='alumnos',
        alumnos=alumnos,
        cursos=cursos,
        filtros={'busqueda': busqueda, 'curso_id': curso_id}
    )

@app.route('/alumnos/crear', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def crear_alumno():
    conn = get_db_connection()
    if request.method == 'POST':
        rut = request.form.get('rut', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        curso_id = request.form.get('curso_id')

        if not (rut and nombre and apellido and curso_id):
            conn.close()
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('crear_alumno'))

        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM alumnos WHERE rut = %s", (rut,))
            if cursor.fetchone():
                conn.close()
                flash('Ya existe un alumno registrado con ese RUT.', 'warning')
                return redirect(url_for('crear_alumno'))

            cursor.execute("""
                INSERT INTO alumnos (rut, nombre, apellido, curso_id)
                VALUES (%s, %s, %s, %s)
            """, (rut, nombre, apellido, curso_id))
            alumno_id = cursor.lastrowid

            # Crear usuario para acceso del alumno
            correo_alumno = f"{nombre.lower().replace(' ', '')}.{apellido.lower().replace(' ', '')}@liceorbl.cl"
            cursor.execute("""
                INSERT INTO usuarios (rut, correo, clave, nombre, rol, alumno_id, activo)
                VALUES (%s, %s, %s, %s, 'alumno', %s, 1)
                ON DUPLICATE KEY UPDATE alumno_id = VALUES(alumno_id)
            """, (rut, correo_alumno, 'alumno123', f"{nombre} {apellido}", alumno_id))
            conn.commit()

        conn.close()
        flash(f'Alumno {nombre} {apellido} registrado con éxito.', 'success')
        return redirect(url_for('listar_alumnos'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()
    conn.close()

    return render_template(
        'alumnos/crear.html',
        title='Registrar Nuevo Alumno',
        active='alumnos',
        cursos=cursos
    )

@app.route('/alumnos/<int:alumno_id>')
@login_required
def perfil_alumno(alumno_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT al.*, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM alumnos al
            JOIN cursos c ON al.curso_id = c.id
            WHERE al.id = %s
        """, (alumno_id,))
        alumno = cursor.fetchone()

        if not alumno:
            conn.close()
            flash('Alumno no encontrado.', 'danger')
            return redirect(url_for('listar_alumnos'))

        alumno['curso'] = {'nombre': alumno['curso_nombre'], 'nivel': alumno['curso_nivel']}
        alumno['nombre_completo'] = f"{alumno['nombre']} {alumno['apellido']}"

        # Inasistencias y recuperaciones
        cursor.execute("""
            SELECT ae.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha, asig.nombre AS asignatura_nombre
            FROM asistencia_evaluaciones ae
            JOIN evaluaciones e ON ae.evaluacion_id = e.id
            JOIN asignaturas asig ON e.asignatura_id = asig.id
            WHERE ae.alumno_id = %s AND ae.presente = 0
            ORDER BY e.fecha DESC
        """, (alumno_id,))
        inasistencias = cursor.fetchall()

        cursor.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            WHERE r.alumno_id = %s
            ORDER BY r.fecha_recuperacion DESC
        """, (alumno_id,))
        recuperaciones = cursor.fetchall()

    conn.close()
    return render_template(
        'alumnos/perfil.html',
        title=alumno['nombre_completo'],
        active='alumnos',
        alumno=alumno,
        inasistencias=inasistencias,
        recuperaciones=recuperaciones
    )

# -------------------------------------------------------------
# REPORTES Y CALENDARIO
# -------------------------------------------------------------
@app.route('/reportes/calendario')
@login_required
def reporte_calendario():
    today = date.today()
    mes = request.args.get('mes', type=int) or today.month
    anio = request.args.get('anio', type=int) or today.year
    curso_id = request.args.get('curso_id', type=int)

    user = session.get('user', {})
    if user.get('rol') == 'alumno' and not curso_id and user.get('alumno_id'):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT curso_id FROM alumnos WHERE id = %s", (user['alumno_id'],))
            row = cursor.fetchone()
            if row:
                curso_id = row['curso_id']
        conn.close()

    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    meses_list = [{'num': i + 1, 'nombre': m} for i, m in enumerate(meses_nombres)]

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()

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
        cursor.execute(query, params)
        evals = cursor.fetchall()
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
        today_day=today.day,
        today_month=today.month,
        today_year=today.year
    )

@app.route('/reportes/pendientes')
@login_required
def reporte_pendientes():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.*, e.titulo AS eval_titulo, al.nombre AS alumno_nombre, al.apellido AS alumno_apellido,
                   al.rut AS alumno_rut, c.nombre AS curso_nombre, asig.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            JOIN asignaturas asig ON e.asignatura_id = asig.id
            WHERE r.estado = 'pendiente'
            ORDER BY r.fecha_recuperacion ASC
        """)
        pendientes = cursor.fetchall()
        for r in pendientes:
            r['alumno'] = {'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}", 'rut': r['alumno_rut'], 'curso': {'nombre': r['curso_nombre']}}
            r['evaluacion'] = {'titulo': r['eval_titulo'], 'asignatura': {'nombre': r['asignatura_nombre']}}
    conn.close()

    return render_template(
        'reportes/pendientes.html',
        title='Alumnos con Evaluaciones Pendientes',
        active='pendientes',
        pendientes=pendientes
    )

@app.route('/reportes/carga')
@login_required
def reporte_carga():
    today = date.today()
    anio = today.year
    mes = today.month
    meses_nombres = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()

        cursor.execute("""
            SELECT curso_id, COUNT(*) AS count
            FROM evaluaciones
            WHERE YEAR(fecha) = %s AND MONTH(fecha) = %s
            GROUP BY curso_id
        """, (anio, mes))
        evals_map = {row['curso_id']: row['count'] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT curso_id, COUNT(*) AS count
            FROM alumnos
            GROUP BY curso_id
        """)
        alumnos_map = {row['curso_id']: row['count'] for row in cursor.fetchall()}
    conn.close()

    datos_curso = []
    for c in cursos:
        datos_curso.append({
            'curso': c,
            'evals_mes': evals_map.get(c['id'], 0),
            'alumnos': alumnos_map.get(c['id'], 0)
        })

    total_evals = sum(d['evals_mes'] for d in datos_curso)
    max_evals = max([d['evals_mes'] for d in datos_curso] + [1])

    return render_template(
        'reportes/carga.html',
        title='Carga Académica',
        active='carga',
        mes_nombre=meses_nombres[mes - 1],
        anio=anio,
        datos_curso=datos_curso,
        total_evals=total_evals,
        max_evals=max_evals
    )

# -------------------------------------------------------------
# ADMINISTRACIÓN (UTP)
# -------------------------------------------------------------
@app.route('/admin')
@login_required
@role_required('utp')
def admin_panel():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()
        cursor.execute("SELECT * FROM asignaturas")
        asignaturas = cursor.fetchall()
        cursor.execute("SELECT * FROM profesores")
        profesores = cursor.fetchall()
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
    conn.close()

    return render_template(
        'admin/index.html',
        title='Administración del Sistema',
        active='admin',
        cursos=cursos,
        asignaturas=asignaturas,
        profesores=profesores,
        usuarios=usuarios,
        total_cursos=len(cursos),
        total_asignaturas=len(asignaturas),
        total_profesores=len(profesores),
        total_usuarios=len(usuarios)
    )

# Admin: Cursos
@app.route('/admin/cursos', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_cursos():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        nivel = request.form.get('nivel', '').strip()
        if nombre and nivel:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO cursos (nombre, nivel) VALUES (%s, %s)", (nombre, nivel))
                conn.commit()
            conn.close()
            flash(f'Curso {nombre} registrado.', 'success')
            return redirect(url_for('admin_cursos'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
        cursos = cursor.fetchall()
    conn.close()
    return render_template('admin/cursos.html', title='Cursos', active='admin', data=cursos)

@app.route('/admin/cursos/<int:curso_id>/eliminar', methods=['POST'])
@login_required
@role_required('utp')
def admin_eliminar_curso(curso_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM cursos WHERE id = %s", (curso_id,))
        conn.commit()
    conn.close()
    flash('Curso eliminado.', 'info')
    return redirect(url_for('admin_cursos'))

# Admin: Asignaturas
@app.route('/admin/asignaturas', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_asignaturas():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        color = request.form.get('color', '#2563eb').strip()
        if nombre:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO asignaturas (nombre, color) VALUES (%s, %s)", (nombre, color))
                conn.commit()
            conn.close()
            flash(f'Asignatura {nombre} registrada.', 'success')
            return redirect(url_for('admin_asignaturas'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
        asignaturas = cursor.fetchall()
    conn.close()
    return render_template('admin/asignaturas.html', title='Asignaturas', active='admin', data=asignaturas)

@app.route('/admin/asignaturas/<int:asig_id>/eliminar', methods=['POST'])
@login_required
@role_required('utp')
def admin_eliminar_asignatura(asig_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM asignaturas WHERE id = %s", (asig_id,))
        conn.commit()
    conn.close()
    flash('Asignatura eliminada.', 'info')
    return redirect(url_for('admin_asignaturas'))

# Admin: Profesores
@app.route('/admin/profesores', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_profesores():
    conn = get_db_connection()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        if nombre and apellido:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO profesores (nombre, apellido, email) VALUES (%s, %s, %s)", (nombre, apellido, email or None))
                conn.commit()
            conn.close()
            flash(f'Profesor {nombre} {apellido} registrado.', 'success')
            return redirect(url_for('admin_profesores'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM profesores ORDER BY apellido ASC, nombre ASC")
        profesores = cursor.fetchall()
    conn.close()
    return render_template('admin/profesores.html', title='Profesores', active='admin', data=profesores)

@app.route('/admin/profesores/<int:profe_id>/eliminar', methods=['POST'])
@login_required
@role_required('utp')
def admin_eliminar_profesor(profe_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM profesores WHERE id = %s", (profe_id,))
        conn.commit()
    conn.close()
    flash('Profesor eliminado.', 'info')
    return redirect(url_for('admin_profesores'))

# Admin: Usuarios
@app.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
@role_required('utp')
def admin_usuarios():
    conn = get_db_connection()
    if request.method == 'POST':
        rut = request.form.get('rut', '').strip()
        correo = request.form.get('correo', '').strip()
        clave = request.form.get('password', '').strip()
        nombre = request.form.get('nombre', '').strip()
        rol = request.form.get('rol', 'profe').strip()

        if rut and correo and clave and nombre:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (rut, correo, clave, nombre, rol, activo)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, (rut, correo, clave, nombre, rol))
                conn.commit()
            conn.close()
            flash(f'Usuario {correo} creado con éxito.', 'success')
            return redirect(url_for('admin_usuarios'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios ORDER BY nombre ASC")
        usuarios = cursor.fetchall()
    conn.close()
    return render_template(
        'admin/usuarios.html',
        title='Usuarios',
        active='admin',
        data=usuarios,
        roles={
            'utp': 'UTP / Directivo',
            'profe': 'Profesor',
            'inspe': 'Inspectoría',
            'alumno': 'Alumno'
        }
    )

@app.route('/admin/usuarios/<string:rut>/toggle', methods=['POST'])
@login_required
@role_required('utp')
def admin_toggle_usuario(rut):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT activo FROM usuarios WHERE rut = %s", (rut,))
        row = cursor.fetchone()
        if row:
            nuevo_estado = 0 if row['activo'] else 1
            cursor.execute("UPDATE usuarios SET activo = %s WHERE rut = %s", (nuevo_estado, rut))
            conn.commit()
            estado_txt = 'Activo' if nuevo_estado else 'Inactivo'
            flash(f'Estado de usuario actualizado: {estado_txt}', 'info')
    conn.close()
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<string:rut>/eliminar', methods=['POST'])
@login_required
@role_required('utp')
def admin_eliminar_usuario(rut):
    if rut == '19.000.001-1':
        flash('No se puede eliminar la cuenta principal de UTP.', 'danger')
        return redirect(url_for('admin_usuarios'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios WHERE rut = %s AND correo != 'utp@liceorbl.cl'", (rut,))
        conn.commit()
    conn.close()
    flash('Usuario eliminado.', 'info')
    return redirect(url_for('admin_usuarios'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==================================================")
    print(f"  Iniciando AgendEx (Flask + MySQL) en http://localhost:{port}")
    print(f"==================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
