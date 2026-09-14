# -*- coding: utf-8 -*-
"""
AgendEx - Sistema de Gestión de Evaluaciones Escolares
Backend en Flask con Base de Datos MySQL
"""

import os
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
        total_alumnos=total_alumnos
    )

# -------------------------------------------------------------
# EVALUACIONES
# -------------------------------------------------------------
@app.route('/evaluaciones')
@login_required
def listar_evaluaciones():
    conn = get_db_connection()
    curso_id = request.args.get('curso_id', '')
    asignatura_id = request.args.get('asignatura_id', '')

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

        query += " ORDER BY e.fecha DESC, e.hora ASC"
        cursor.execute(query, params)
        evaluaciones = cursor.fetchall()

        for ev in evaluaciones:
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
            ev['curso'] = {'nombre': ev['curso_nombre']}

    conn.close()
    return render_template(
        'evaluaciones/listar.html',
        title='Gestión de Evaluaciones',
        active='evaluaciones',
        evaluaciones=evaluaciones,
        cursos=cursos,
        asignaturas=asignaturas,
        filtro_curso=curso_id,
        filtro_asignatura=asignatura_id
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
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
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
        ev['curso'] = {'nombre': ev['curso_nombre']}

        # Asistencia
        cursor.execute("""
            SELECT ae.*, al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut
            FROM asistencia_evaluaciones ae
            JOIN alumnos al ON ae.alumno_id = al.id
            WHERE ae.evaluacion_id = %s
        """, (eval_id,))
        asistencias = cursor.fetchall()

    conn.close()
    return render_template(
        'evaluaciones/detalle.html',
        title=ev['titulo'],
        active='evaluaciones',
        evaluacion=ev,
        asistencias=asistencias
    )

@app.route('/evaluaciones/<int:eval_id>/asistencia', methods=['GET', 'POST'])
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

        if request.method == 'POST':
            cursor.execute("SELECT id FROM alumnos WHERE curso_id = %s", (ev['curso_id'],))
            alumnos = cursor.fetchall()

            for a in alumnos:
                aid = a['id']
                presente = 1 if request.form.get(f'alumno_{aid}') == 'on' else 0
                justificado = 1 if request.form.get(f'justificado_{aid}') == 'on' else 0
                motivo = request.form.get(f'motivo_{aid}', '').strip() if not presente else None

                cursor.execute("""
                    INSERT INTO asistencia_evaluaciones (evaluacion_id, alumno_id, presente, justificado, motivo_inasistencia)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    presente=VALUES(presente), justificado=VALUES(justificado), motivo_inasistencia=VALUES(motivo_inasistencia)
                """, (eval_id, aid, presente, justificado, motivo))

            conn.close()
            flash('Asistencia guardada correctamente.', 'success')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

        cursor.execute("""
            SELECT al.*, ae.presente, ae.justificado, ae.motivo_inasistencia
            FROM alumnos al
            LEFT JOIN asistencia_evaluaciones ae ON al.id = ae.alumno_id AND ae.evaluacion_id = %s
            WHERE al.curso_id = %s
            ORDER BY al.apellido ASC, al.nombre ASC
        """, (eval_id, ev['curso_id']))
        alumnos_asistencia = cursor.fetchall()

    conn.close()
    return render_template(
        'evaluaciones/asistencia.html',
        title=f"Asistencia · {ev['titulo']}",
        active='evaluaciones',
        evaluacion=ev,
        alumnos=alumnos_asistencia
    )

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

# -------------------------------------------------------------
# RECUPERACIONES
# -------------------------------------------------------------
@app.route('/recuperaciones')
@login_required
def listar_recuperaciones():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido, al.rut AS alumno_rut,
                   c.nombre AS curso_nombre, asig.nombre AS asignatura_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            JOIN asignaturas asig ON e.asignatura_id = asig.id
            ORDER BY r.fecha_recuperacion DESC
        """)
        recuperaciones = cursor.fetchall()

        for r in recuperaciones:
            r['alumno'] = {'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}", 'rut': r['alumno_rut'], 'curso': {'nombre': r['curso_nombre']}}
            r['evaluacion'] = {'titulo': r['eval_titulo'], 'fecha': r['eval_fecha'], 'asignatura': {'nombre': r['asignatura_nombre']}}

    conn.close()
    return render_template(
        'recuperaciones/listar.html',
        title='Evaluaciones de Recuperación',
        active='recuperaciones',
        recuperaciones=recuperaciones
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

        conn.close()
        flash(f'Recuperación agendada con éxito ({exigencia}% de exigencia).', 'success')
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

@app.route('/recuperaciones/<int:recup_id>/estado', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def cambiar_estado_recuperacion(recup_id):
    nuevo_estado = request.form.get('estado')
    if nuevo_estado in ['pendiente', 'rendida', 'cancelada']:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE recuperaciones SET estado = %s WHERE id = %s", (nuevo_estado, recup_id))
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
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT al.*, c.nombre AS curso_nombre
            FROM alumnos al
            JOIN cursos c ON al.curso_id = c.id
            ORDER BY c.nombre ASC, al.apellido ASC
        """)
        alumnos = cursor.fetchall()
        for a in alumnos:
            a['curso'] = {'nombre': a['curso_nombre']}
            a['nombre_completo'] = f"{a['nombre']} {a['apellido']}"
    conn.close()

    return render_template(
        'alumnos/listar.html',
        title='Nómina de Alumnos',
        active='alumnos',
        alumnos=alumnos
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
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN cursos c ON e.curso_id = c.id
            ORDER BY e.fecha ASC
        """)
        evaluaciones = cursor.fetchall()
        for ev in evaluaciones:
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['curso'] = {'nombre': ev['curso_nombre']}
    conn.close()

    return render_template(
        'reportes/calendario.html',
        title='Calendario Mensual',
        active='calendario',
        evaluaciones=evaluaciones
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
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT c.nombre AS curso_nombre, COUNT(e.id) AS total_evaluaciones
            FROM cursos c
            LEFT JOIN evaluaciones e ON c.id = e.curso_id
            GROUP BY c.id, c.nombre
            ORDER BY total_evaluaciones DESC
        """)
        carga = cursor.fetchall()
    conn.close()

    return render_template(
        'reportes/carga.html',
        title='Distribución de Carga Académica',
        active='carga',
        carga=carga
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
        cursor.execute("SELECT COUNT(*) AS total FROM cursos")
        total_cursos = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM asignaturas")
        total_asignaturas = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM profesores")
        total_profesores = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        total_usuarios = cursor.fetchone()['total']
    conn.close()

    return render_template(
        'admin/index.html',
        title='Administración del Sistema',
        active='admin',
        total_cursos=total_cursos,
        total_asignaturas=total_asignaturas,
        total_profesores=total_profesores,
        total_usuarios=total_usuarios
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==================================================")
    print(f"  Iniciando AgendEx (Flask + MySQL) en http://localhost:{port}")
    print(f"==================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
