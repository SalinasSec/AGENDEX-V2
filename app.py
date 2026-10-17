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

def format_date_val(val):
    if val is None:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%Y-%m-%d')
    return str(val)

def format_time_val(val):
    if val is None:
        return ''
    if hasattr(val, 'strftime'):
        return val.strftime('%H:%M')
    s = str(val)
    if len(s) >= 5 and ':' in s:
        return s[:5]
    return s

@app.template_filter('str_date')
def str_date_filter(val):
    return format_date_val(val)

# Mapeo oficial de asignaturas y cursos por profesor (Liceo Industrial Bicentenario RBL)
PROFESORES_ASIGNACIONES = {
    1: {  # Marcela Rubio
        'cursos': [19, 26],  # 3°G, 4°G
        'asignaturas': [7],   # M8: Desarrollo de Aplicaciones Web
    },
    2: {  # Antonio Velásquez
        'cursos': [19, 26],  # 3°G, 4°G
        'asignaturas': [8, 9, 10],  # M5: DBD, M6: POO, M7: ABD
    },
    3: {  # Carolina Reyes
        'cursos': [1, 2, 7, 12, 19, 26],
        'asignaturas': [2],  # Matemática
    },
    4: {  # Patricio Muñoz
        'cursos': [1, 2, 7, 8, 19, 26],
        'asignaturas': [1],  # Lenguaje y Comunicación
    },
    5: {  # Valentina Soto
        'cursos': [1, 2, 7, 19],
        'asignaturas': [3],  # Historia
    },
    6: {  # Diego Fuentes
        'cursos': [1, 7, 19, 26],
        'asignaturas': [4],  # Inglés
    },
    7: {  # Docente Aprestos
        'cursos': [7, 8, 9, 10, 11, 12],  # 2A a 2F
        'asignaturas': [11],  # Taller Aprestos Técnicos
    }
}

def get_profesor_asignaciones(profesor_id, cursor=None):
    if not profesor_id:
        return {'cursos': [], 'asignaturas': []}
    try:
        p_id = int(profesor_id)
    except (ValueError, TypeError):
        return {'cursos': [], 'asignaturas': []}
    asig = PROFESORES_ASIGNACIONES.get(p_id, {'cursos': [], 'asignaturas': []})
    cursos_set = set(asig['cursos'])
    asig_set = set(asig['asignaturas'])
    if cursor:
        try:
            cursor.execute("SELECT DISTINCT curso_id, asignatura_id FROM evaluaciones WHERE profesor_id = %s", (p_id,))
            for row in cursor.fetchall():
                if row.get('curso_id'):
                    cursos_set.add(row['curso_id'])
                if row.get('asignatura_id'):
                    asig_set.add(row['asignatura_id'])
        except Exception:
            pass
    return {'cursos': list(cursos_set), 'asignaturas': list(asig_set)}

def resolve_profesor_id(user_sess, conn=None):
    if not user_sess or user_sess.get('rol') != 'profe':
        return user_sess.get('profesor_id') if user_sess else None
    if user_sess.get('profesor_id'):
        return user_sess['profesor_id']
    should_close = False
    if conn is None:
        try:
            conn = get_db_connection()
            should_close = True
        except Exception:
            return None
    try:
        with conn.cursor() as cursor:
            email = user_sess.get('correo', '').strip().lower()
            if email:
                cursor.execute("SELECT id FROM profesores WHERE LOWER(email) = %s LIMIT 1", (email,))
                p = cursor.fetchone()
                if p:
                    user_sess['profesor_id'] = p['id']
                    if 'user' in session:
                        session['user']['profesor_id'] = p['id']
                    try:
                        cursor.execute("UPDATE usuarios SET profesor_id = %s WHERE id = %s", (p['id'], user_sess.get('id')))
                        conn.commit()
                    except Exception:
                        pass
                    return p['id']
            nom = user_sess.get('nombre', '').strip().lower()
            p_id = None
            if 'marcela' in nom:
                p_id = 1
            elif 'antonio' in nom:
                p_id = 2
            elif 'carolina' in nom:
                p_id = 3
            elif 'patricio' in nom:
                p_id = 4
            elif 'valentina' in nom:
                p_id = 5
            elif 'diego' in nom:
                p_id = 6
            elif 'apresto' in nom:
                p_id = 7
            else:
                cursor.execute("SELECT id FROM profesores WHERE LOWER(nombre) LIKE %s LIMIT 1", (f"%{nom.split()[0]}%",))
                p = cursor.fetchone()
                p_id = p['id'] if p else None
            if p_id:
                user_sess['profesor_id'] = p_id
                if 'user' in session:
                    session['user']['profesor_id'] = p_id
                try:
                    cursor.execute("UPDATE usuarios SET profesor_id = %s WHERE id = %s", (p_id, user_sess.get('id')))
                    conn.commit()
                except Exception:
                    pass
                return p_id
    except Exception:
        pass
    finally:
        if should_close:
            try:
                conn.close()
            except Exception:
                pass
    return user_sess.get('profesor_id')

@app.context_processor
def inject_context():
    user = session.get('user')
    if user and user.get('rol') == 'profe' and not user.get('profesor_id'):
        resolve_profesor_id(user)
    dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    t = date.today()
    hoy_fmt = f"{dias[t.weekday()]}, {t.day} de {meses[t.month - 1]} de {t.year}"

    alumno_recups_count = 0
    if user and user.get('rol') == 'alumno' and user.get('alumno_id'):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as cnt FROM recuperaciones WHERE alumno_id = %s AND estado = 'pendiente'", (user['alumno_id'],))
                row = cursor.fetchone()
                if row:
                    alumno_recups_count = row['cnt']
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
        format_date=format_date_val
    )

def check_and_update_database_schema(conn):
    """
    Verifica y actualiza automáticamente el esquema de MySQL si faltan columnas
    o tablas de versiones anteriores (evita OperationalError 1054 / SyntaxError).
    """
    try:
        with conn.cursor() as cursor:
            # 1. Columna asistencia_guardada en evaluaciones
            try:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'evaluaciones' AND COLUMN_NAME = 'asistencia_guardada'
                """)
                row = cursor.fetchone()
                if row and row.get('cnt') == 0:
                    cursor.execute("ALTER TABLE evaluaciones ADD COLUMN asistencia_guardada TINYINT(1) DEFAULT 0")
            except Exception:
                pass

            # 2. Columna estado_asistencia en asistencia_evaluaciones
            try:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asistencia_evaluaciones' AND COLUMN_NAME = 'estado_asistencia'
                """)
                row = cursor.fetchone()
                if row and row.get('cnt') == 0:
                    cursor.execute("ALTER TABLE asistencia_evaluaciones ADD COLUMN estado_asistencia ENUM('presente', 'injustificada', 'justificado', 'salida') DEFAULT 'presente'")
            except Exception:
                pass

            # 3. Columna motivo_inasistencia en asistencia_evaluaciones
            try:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asistencia_evaluaciones' AND COLUMN_NAME = 'motivo_inasistencia'
                """)
                row = cursor.fetchone()
                if row and row.get('cnt') == 0:
                    cursor.execute("ALTER TABLE asistencia_evaluaciones ADD COLUMN motivo_inasistencia VARCHAR(255) DEFAULT NULL")
            except Exception:
                pass

            # 4. Asegurar índice único en asistencia_evaluaciones
            try:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM information_schema.STATISTICS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'asistencia_evaluaciones' AND INDEX_NAME = 'uk_eval_alumno'
                """)
                row = cursor.fetchone()
                if row and row.get('cnt') == 0:
                    cursor.execute("ALTER TABLE asistencia_evaluaciones ADD UNIQUE KEY uk_eval_alumno (evaluacion_id, alumno_id)")
            except Exception:
                pass

            # 5. Columna exigencia en recuperaciones
            try:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'recuperaciones' AND COLUMN_NAME = 'exigencia'
                """)
                row = cursor.fetchone()
                if row and row.get('cnt') == 0:
                    cursor.execute("ALTER TABLE recuperaciones ADD COLUMN exigencia DECIMAL(5,2) NOT NULL DEFAULT 60.00")
            except Exception:
                pass

            # 6. Vincular usuarios docentes a sus registros en profesores
            try:
                cursor.execute("""
                    UPDATE usuarios u
                    JOIN profesores p ON LOWER(TRIM(u.correo)) = LOWER(TRIM(p.email))
                    SET u.profesor_id = p.id
                    WHERE u.rol = 'profe' AND (u.profesor_id IS NULL OR u.profesor_id = 0)
                """)
                cursor.execute("UPDATE usuarios SET profesor_id = 1 WHERE LOWER(correo) LIKE '%marcela%' AND (profesor_id IS NULL OR profesor_id = 0)")
                cursor.execute("UPDATE usuarios SET profesor_id = 2 WHERE LOWER(correo) LIKE '%antonio%' AND (profesor_id IS NULL OR profesor_id = 0)")
                cursor.execute("UPDATE usuarios SET profesor_id = 3 WHERE LOWER(correo) LIKE '%carolina%' AND (profesor_id IS NULL OR profesor_id = 0)")
                conn.commit()
            except Exception:
                pass
    except Exception:
        pass

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

        session_user = {
            'id': user['id'],
            'rut': user['rut'],
            'correo': user['correo'],
            'nombre': user['nombre'],
            'rol': user['rol'],
            'profesor_id': user.get('profesor_id'),
            'alumno_id': user.get('alumno_id')
        }
        if session_user['rol'] == 'profe' and not session_user['profesor_id']:
            resolve_profesor_id(session_user)

        session['user'] = session_user

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
                LEFT JOIN asignaturas a ON e.asignatura_id = a.id
                LEFT JOIN profesores p ON e.profesor_id = p.id
                LEFT JOIN cursos c ON e.curso_id = c.id
                WHERE e.curso_id = %s
                ORDER BY e.fecha ASC
            """, (curso_id,))
            evals = cursor.fetchall()

            for ev in evals:
                ev['fecha'] = format_date_val(ev.get('fecha'))
                ev['hora'] = format_time_val(ev.get('hora'))
                ev['asignatura'] = {'nombre': ev.get('asignatura_nombre') or 'General', 'color': ev.get('asignatura_color') or '#14213D'}
                ev['profesor'] = {'nombre_completo': f"{ev.get('profe_nombre') or ''} {ev.get('profe_apellido') or ''}".strip() or 'Docente'}
                ev['curso'] = {'nombre': ev.get('curso_nombre') or 'Curso'}

            cursor.execute("""
                SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha, e.descripcion AS eval_descripcion,
                       e.hora AS eval_hora,
                       a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                       p.nombre AS profe_nombre, p.apellido AS profe_apellido, p.email AS profe_email
                FROM recuperaciones r
                JOIN evaluaciones e ON r.evaluacion_id = e.id
                LEFT JOIN asignaturas a ON e.asignatura_id = a.id
                LEFT JOIN profesores p ON e.profesor_id = p.id
                WHERE r.alumno_id = %s
                ORDER BY (r.estado = 'pendiente') DESC, r.fecha_recuperacion ASC
            """, (alumno_id,))
            recuperaciones = cursor.fetchall()

            for r in recuperaciones:
                f_rec = format_date_val(r.get('fecha_recuperacion'))
                r['fecha_recuperacion'] = f_rec
                r['eval_fecha'] = format_date_val(r.get('eval_fecha'))
                if f_rec == hoy:
                    r['aviso_tiempo'] = '¡Rinde Hoy!'
                    r['aviso_clase'] = 'danger'
                elif f_rec > hoy:
                    try:
                        dias = (datetime.strptime(f_rec, '%Y-%m-%d').date() - date.today()).days
                        if dias == 1:
                            r['aviso_tiempo'] = 'Rinde Mañana'
                            r['aviso_clase'] = 'warning text-dark'
                        else:
                            r['aviso_tiempo'] = f'En {dias} días'
                            r['aviso_clase'] = 'primary'
                    except Exception:
                        r['aviso_tiempo'] = f_rec
                        r['aviso_clase'] = 'secondary'
                else:
                    r['aviso_tiempo'] = 'Fecha cumplida'
                    r['aviso_clase'] = 'secondary'

                r['porcentaje_exigencia'] = float(r.get('exigencia') or 70.00)
                prof_nom = f"{r.get('profe_nombre') or ''} {r.get('profe_apellido') or ''}".strip()
                r['profesor_nombre'] = prof_nom or 'Profesor de la Asignatura'
                r['asignatura'] = {'nombre': r.get('asignatura_nombre') or 'General', 'color': r.get('asignatura_color') or '#14213D'}

            recs_pendientes = [r for r in recuperaciones if r['estado'] == 'pendiente']

            # Inasistencias registradas a evaluaciones
            cursor.execute("""
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
            inasistencias = cursor.fetchall()
            for inas in inasistencias:
                inas['eval_fecha'] = format_date_val(inas.get('eval_fecha'))
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

        # Vista de UTP / Profesor / Inspectoría
        query_evals = """
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN asignaturas a ON e.asignatura_id = a.id
            JOIN profesores p ON e.profesor_id = p.id
            JOIN cursos c ON e.curso_id = c.id
        """
        params_evals = []
        user_sess = session.get('user', {})
        prof_id = resolve_profesor_id(user_sess, conn)
        mi_profesor = None

        if user_sess.get('rol') == 'profe':
            if prof_id:
                query_evals += " WHERE e.profesor_id = %s"
                params_evals.append(prof_id)
                cursor.execute("SELECT * FROM profesores WHERE id = %s", (prof_id,))
                p_row = cursor.fetchone()
                if p_row:
                    p_row['nombre_completo'] = f"{p_row['nombre']} {p_row['apellido']}"
                    mi_profesor = p_row
            else:
                query_evals += " WHERE 1 = 0"

        query_evals += " ORDER BY e.fecha ASC, e.hora ASC"
        cursor.execute(query_evals, params_evals)
        todas_evals = cursor.fetchall()

        for ev in todas_evals:
            ev['fecha'] = format_date_val(ev.get('fecha'))
            ev['hora'] = format_time_val(ev.get('hora'))
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
            ev['curso'] = {'nombre': ev['curso_nombre']}

        cursor.execute("SELECT COUNT(*) AS total FROM alumnos")
        total_alumnos = cursor.fetchone()['total']

        query_recs = """
            SELECT r.*, e.titulo AS eval_titulo, a.nombre AS alumno_nombre, a.apellido AS alumno_apellido, c.nombre AS curso_nombre
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos a ON r.alumno_id = a.id
            JOIN cursos c ON a.curso_id = c.id
            WHERE r.estado = 'pendiente'
        """
        params_recs = []
        if user_sess.get('rol') == 'profe':
            if prof_id:
                query_recs += " AND e.profesor_id = %s"
                params_recs.append(prof_id)
            else:
                query_recs += " AND 1 = 0"
        cursor.execute(query_recs, params_recs)
        recuperaciones_pendientes = cursor.fetchall()
        for r in recuperaciones_pendientes:
            r['fecha_recuperacion'] = format_date_val(r.get('fecha_recuperacion'))
            r['porcentaje_exigencia'] = float(r.get('exigencia') or 70.00)
            r['alumno'] = {'nombre': r['alumno_nombre'], 'apellido': r['alumno_apellido'], 'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}"}
            r['curso'] = {'nombre': r['curso_nombre']}

        if user_sess.get('rol') == 'profe':
            if prof_id:
                cursor.execute("""
                    SELECT c.nombre AS curso_nombre, COUNT(e.id) AS count
                    FROM cursos c
                    JOIN evaluaciones e ON c.id = e.curso_id AND e.profesor_id = %s
                    GROUP BY c.id, c.nombre
                    HAVING count > 0
                    ORDER BY count DESC
                """, (prof_id,))
                evals_por_curso = cursor.fetchall()
                total_cursos = len(evals_por_curso)
            else:
                evals_por_curso = []
                total_cursos = 0
        else:
            cursor.execute("""
                SELECT c.nombre AS curso_nombre, COUNT(e.id) AS count
                FROM cursos c
                LEFT JOIN evaluaciones e ON c.id = e.curso_id
                GROUP BY c.id, c.nombre
                ORDER BY count DESC
            """)
            evals_por_curso = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) AS total FROM cursos")
            total_cursos = cursor.fetchone()['total']

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
        evals_por_curso=evals_por_curso,
        mi_profesor=mi_profesor
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
    user_sess = session.get('user', {})
    prof_id = resolve_profesor_id(user_sess, conn)

    with conn.cursor() as cursor:
        if user_sess.get('rol') == 'profe':
            if prof_id:
                asigs_info = get_profesor_asignaciones(prof_id, cursor)
                if asigs_info['cursos']:
                    fmt_c = ','.join(['%s'] * len(asigs_info['cursos']))
                    cursor.execute(f"SELECT DISTINCT id, nombre, nivel FROM cursos WHERE id IN ({fmt_c}) ORDER BY nombre ASC", tuple(asigs_info['cursos']))
                    cursos = cursor.fetchall()
                else:
                    cursor.execute("""
                        SELECT DISTINCT c.id, c.nombre, c.nivel
                        FROM cursos c
                        JOIN evaluaciones e ON c.id = e.curso_id
                        WHERE e.profesor_id = %s
                        ORDER BY c.nombre ASC
                    """, (prof_id,))
                    cursos = cursor.fetchall()

                if asigs_info['asignaturas']:
                    fmt_a = ','.join(['%s'] * len(asigs_info['asignaturas']))
                    cursor.execute(f"SELECT DISTINCT id, nombre, color FROM asignaturas WHERE id IN ({fmt_a}) ORDER BY nombre ASC", tuple(asigs_info['asignaturas']))
                    asignaturas = cursor.fetchall()
                else:
                    cursor.execute("""
                        SELECT DISTINCT a.id, a.nombre, a.color
                        FROM asignaturas a
                        JOIN evaluaciones e ON a.id = e.asignatura_id
                        WHERE e.profesor_id = %s
                        ORDER BY a.nombre ASC
                    """, (prof_id,))
                    asignaturas = cursor.fetchall()
            else:
                cursos = []
                asignaturas = []
        else:
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
        if user_sess.get('rol') == 'profe':
            if prof_id:
                query += " AND e.profesor_id = %s"
                params.append(prof_id)
            else:
                query += " AND 1=0"
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
        if user_sess.get('rol') == 'inspe':
            cursor.execute("""
                SELECT DISTINCT evaluacion_id 
                FROM asistencia_evaluaciones 
                WHERE (estado_asistencia != 'presente' AND estado_asistencia IS NOT NULL) OR presente = 0
            """)
            eval_ids_con_inasistencias = {row['evaluacion_id'] for row in cursor.fetchall()}
            evaluaciones = [e for e in evaluaciones if e['id'] in eval_ids_con_inasistencias]

        for ev in evaluaciones:
            ev['fecha'] = format_date_val(ev.get('fecha'))
            ev['hora'] = format_time_val(ev.get('hora'))
            ev['asignatura'] = {'nombre': ev['asignatura_nombre'], 'color': ev['asignatura_color']}
            ev['profesor'] = {'nombre_completo': f"{ev['profe_nombre']} {ev['profe_apellido']}"}
            ev['curso'] = {'nombre': ev['curso_nombre']}

    conn.close()
    page_title = 'Mis Evaluaciones Asignadas' if user_sess.get('rol') == 'profe' else ('Evaluaciones con Inasistencias' if user_sess.get('rol') == 'inspe' else 'Gestión de Evaluaciones')
    return render_template(
        'evaluaciones/listar.html',
        title=page_title,
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
    check_and_update_database_schema(conn)

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip() or None
        asignatura_id = request.form.get('asignatura_id')
        curso_id = request.form.get('curso_id')
        profesor_id = resolve_profesor_id(session['user'], conn)

        with conn.cursor() as cursor:
            if not profesor_id:
                cursor.execute("SELECT id FROM profesores LIMIT 1")
                first_p = cursor.fetchone()
                profesor_id = first_p['id'] if first_p else 1

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
            new_eval_id = cursor.lastrowid
            conn.commit()

        conn.close()
        flash('Evaluación calendarizada exitosamente.', 'success')
        return redirect(url_for('detalle_evaluacion', eval_id=new_eval_id) if new_eval_id else url_for('listar_evaluaciones'))

    hoy = date.today().strftime('%Y-%m-%d')
    mi_profesor = None
    prof_id = resolve_profesor_id(session['user'], conn)
    with conn.cursor() as cursor:
        if session['user']['rol'] == 'profe' and prof_id:
            asigs_info = get_profesor_asignaciones(prof_id, cursor)
            if asigs_info['cursos']:
                fmt_c = ','.join(['%s'] * len(asigs_info['cursos']))
                cursor.execute(f"SELECT * FROM cursos WHERE id IN ({fmt_c}) ORDER BY nombre ASC", tuple(asigs_info['cursos']))
                cursos = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
                cursos = cursor.fetchall()

            if asigs_info['asignaturas']:
                fmt_a = ','.join(['%s'] * len(asigs_info['asignaturas']))
                cursor.execute(f"SELECT * FROM asignaturas WHERE id IN ({fmt_a}) ORDER BY nombre ASC", tuple(asigs_info['asignaturas']))
                asignaturas = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
                asignaturas = cursor.fetchall()

            cursor.execute("SELECT * FROM profesores WHERE id = %s", (prof_id,))
            p = cursor.fetchone()
            if p:
                p['nombre_completo'] = f"{p['nombre']} {p['apellido']}"
                mi_profesor = p
        else:
            cursor.execute("SELECT * FROM cursos ORDER BY nombre ASC")
            cursos = cursor.fetchall()
            cursor.execute("SELECT * FROM asignaturas ORDER BY nombre ASC")
            asignaturas = cursor.fetchall()
            if prof_id:
                cursor.execute("SELECT * FROM profesores WHERE id = %s", (prof_id,))
                p = cursor.fetchone()
                if p:
                    p['nombre_completo'] = f"{p['nombre']} {p['apellido']}"
                    mi_profesor = p
    conn.close()

    if not mi_profesor:
        mi_profesor = {'nombre_completo': session['user'].get('nombre', 'Docente')}

    return render_template(
        'evaluaciones/crear.html',
        title='Calendarizar Evaluación',
        active='evaluaciones',
        cursos=cursos,
        asignaturas=asignaturas,
        mi_profesor=mi_profesor,
        hoy=hoy
    )

@app.route('/evaluaciones/<int:eval_id>')
@login_required
def detalle_evaluacion(eval_id):
    conn = get_db_connection()
    check_and_update_database_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.*, a.nombre AS asignatura_nombre, a.color AS asignatura_color,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido, c.nombre AS curso_nombre, c.nivel AS curso_nivel
            FROM evaluaciones e
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            LEFT JOIN profesores p ON e.profesor_id = p.id
            LEFT JOIN cursos c ON e.curso_id = c.id
            WHERE e.id = %s
        """, (eval_id,))
        ev = cursor.fetchone()

        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        ev['fecha'] = format_date_val(ev.get('fecha'))
        ev['hora'] = format_time_val(ev.get('hora'))
        ev['asignatura'] = {'nombre': ev.get('asignatura_nombre') or 'General', 'color': ev.get('asignatura_color') or '#14213D'}
        prof_nombre = f"{ev.get('profe_nombre') or ''} {ev.get('profe_apellido') or ''}".strip() or 'Docente'
        ev['profesor'] = {'nombre_completo': prof_nombre}
        ev['curso'] = {'nombre': ev.get('curso_nombre') or 'Curso', 'nivel': ev.get('curso_nivel') or 'Media'}

        # Alumnos del curso
        cursor.execute("""
            SELECT id, rut, nombre, apellido, 
                    CONCAT(COALESCE(nombre, ''), ' ', COALESCE(apellido, '')) as nombre_completo
            FROM alumnos
            WHERE curso_id = %s
            ORDER BY apellido ASC, nombre ASC
        """, (ev['curso_id'],))
        alumnos = cursor.fetchall()
        for al in alumnos:
            if not al.get('nombre_completo') or not al['nombre_completo'].strip():
                al['nombre_completo'] = f"{al.get('nombre', '')} {al.get('apellido', '')}".strip() or al.get('rut', 'Alumno')

        # Asistencia registrada
        cursor.execute("""
            SELECT * FROM asistencia_evaluaciones
            WHERE evaluacion_id = %s
        """, (eval_id,))
        asistencias_raw = cursor.fetchall()
        asistencias_map = {}
        for a in asistencias_raw:
            aid = a['alumno_id']
            asistencias_map[aid] = {
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
    hoy = date.today().strftime('%Y-%m-%d')
    return render_template(
        'evaluaciones/detalle.html',
        title=ev['titulo'],
        active='evaluaciones',
        ev=ev,
        evaluacion=ev,
        alumnos=alumnos,
        alumnos_afectados=alumnos_afectados,
        asistencias=asistencias_map,
        hoy=hoy
    )

@app.route('/evaluaciones/<int:eval_id>/asistencia', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def asistencia_evaluacion(eval_id):
    conn = get_db_connection()
    check_and_update_database_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM evaluaciones WHERE id = %s", (eval_id,))
        ev = cursor.fetchone()
        if not ev:
            conn.close()
            flash('Evaluación no encontrada.', 'danger')
            return redirect(url_for('listar_evaluaciones'))

        user_rol = session['user']['rol']
        user_prof_id = session['user'].get('profesor_id')

        # Si el profesor no es el docente titular asignado a la evaluación, se bloquea
        if user_rol == 'profe' and str(user_prof_id) != str(ev.get('profesor_id')):
            conn.close()
            flash('Acceso denegado: Solo el docente titular asignado a esta asignatura/evaluación puede registrar la lista de asistencia.', 'danger')
            return redirect(url_for('detalle_evaluacion', eval_id=eval_id))

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

            cursor.execute("SELECT id, estado_asistencia FROM asistencia_evaluaciones WHERE evaluacion_id = %s AND alumno_id = %s", (eval_id, aid))
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
                elif estado_enviado == 'justificado':
                    estado_final = 'justificado'
                elif estado_enviado == 'injustificada':
                    estado_final = 'injustificada'
                else:
                    if existing and existing.get('estado_asistencia') == 'justificado':
                        estado_final = 'justificado'
                    else:
                        estado_final = 'presente'

            presente = 1 if estado_final == 'presente' else 0
            justificado = 1 if estado_final in ('justificado', 'salida') else 0
            motivo = motivo_enviado if estado_final != 'presente' else None

            if existing:
                cursor.execute("""
                    UPDATE asistencia_evaluaciones
                    SET estado_asistencia = %s, presente = %s, justificado = %s, motivo_inasistencia = %s
                    WHERE id = %s
                """, (estado_final, presente, justificado, motivo, existing['id']))
            else:
                cursor.execute("""
                    INSERT INTO asistencia_evaluaciones (evaluacion_id, alumno_id, estado_asistencia, presente, justificado, motivo_inasistencia)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (eval_id, aid, estado_final, presente, justificado, motivo))

            # Sincronizar automáticamente cualquier recuperación existente del alumno para esta prueba
            if estado_final in ('justificado', 'salida'):
                cursor.execute("""
                    UPDATE recuperaciones
                    SET exigencia = 60.00
                    WHERE evaluacion_id = %s AND alumno_id = %s
                """, (eval_id, aid))
            elif estado_final == 'injustificada':
                cursor.execute("""
                    UPDATE recuperaciones
                    SET exigencia = 70.00
                    WHERE evaluacion_id = %s AND alumno_id = %s
                """, (eval_id, aid))

        # Si el profesor guarda, se marca la evaluación como asistencia cerrada
        if user_rol == 'profe':
            try:
                cursor.execute("UPDATE evaluaciones SET asistencia_guardada = 1 WHERE id = %s", (eval_id,))
            except Exception:
                try:
                    cursor.execute("ALTER TABLE evaluaciones ADD COLUMN asistencia_guardada TINYINT(1) DEFAULT 0")
                    cursor.execute("UPDATE evaluaciones SET asistencia_guardada = 1 WHERE id = %s", (eval_id,))
                except Exception:
                    pass

        conn.commit()

    conn.close()
    flash('Asistencia guardada exitosamente. Ha quedado registrada y cerrada para el curso.', 'success')
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
    ev['fecha'] = format_date_val(ev.get('fecha'))
    ev['hora'] = format_time_val(ev.get('hora'))
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
            r['fecha_recuperacion'] = format_date_val(r.get('fecha_recuperacion'))
            r['eval_fecha'] = format_date_val(r.get('eval_fecha'))
            r['alumno'] = {'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}", 'rut': r['alumno_rut'], 'curso': {'nombre': r['curso_nombre']}}
            r['evaluacion'] = {'titulo': r['eval_titulo'], 'fecha': r['eval_fecha'], 'asignatura': {'nombre': r['asignatura_nombre']}}
            r['porcentaje_exigencia'] = float(r.get('exigencia') or r.get('porcentaje_exigencia') or 70.00)

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
@role_required('profe', 'inspe')
def crear_recuperacion():
    if session['user']['rol'] == 'utp':
        flash('La asignación de recuperaciones corresponde a Profesores e Inspectoría General. El perfil UTP cumple funciones de supervisión y reportería.', 'warning')
        return redirect(url_for('listar_recuperaciones'))

    conn = get_db_connection()

    if request.method == 'POST':
        evaluacion_id = request.form.get('evaluacion_id')
        alumno_id = request.form.get('alumno_id')
        fecha_recup = request.form.get('fecha_recuperacion')
        hora_recup = request.form.get('hora_recuperacion', '').strip()
        indicaciones = request.form.get('indicaciones', '').strip()
        motivo = request.form.get('motivo', '').strip()

        if indicaciones and not motivo:
            motivo = indicaciones
        if hora_recup:
            motivo = f"{motivo} [{hora_recup}]".strip() if motivo else f"[{hora_recup}]"

        # Validar que si es profesor, solo pueda agendar recuperaciones de sus propias evaluaciones
        if session['user']['rol'] == 'profe' and session['user'].get('profesor_id'):
            with conn.cursor() as cursor:
                cursor.execute("SELECT profesor_id FROM evaluaciones WHERE id = %s", (evaluacion_id,))
                ev_tit = cursor.fetchone()
                if ev_tit and str(ev_tit['profesor_id']) != str(session['user']['profesor_id']):
                    conn.close()
                    flash('Acceso denegado: Solo el docente titular de la evaluación puede programar sus recuperaciones.', 'danger')
                    return redirect(url_for('listar_recuperaciones'))

        # Revisar si la inasistencia ya estaba justificada previamente por Inspectoría
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT justificado, estado_asistencia FROM asistencia_evaluaciones
                WHERE evaluacion_id = %s AND alumno_id = %s
            """, (evaluacion_id, alumno_id))
            asist = cursor.fetchone()

            # Regla institucional: el profesor programa con 70%; pasa al 60% al presentar justificado en Inspectoría
            exigencia = 60.00 if (asist and (asist.get('justificado') or asist.get('estado_asistencia') in ('justificado', 'salida'))) else 70.00

            cursor.execute("""
                INSERT INTO recuperaciones (evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado)
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """, (evaluacion_id, alumno_id, fecha_recup, motivo, exigencia))
            conn.commit()

        conn.close()
        flash(f'Evaluación recuperativa agendada con éxito ({int(exigencia)}% de exigencia inicial).', 'success')
        return redirect(url_for('listar_recuperaciones'))

    with conn.cursor() as cursor:
        query_evals = """
            SELECT e.*, c.nombre AS curso_nombre, a.nombre AS asignatura_nombre
            FROM evaluaciones e
            JOIN cursos c ON e.curso_id = c.id
            JOIN asignaturas a ON e.asignatura_id = a.id
        """
        params_evals = []
        if session['user']['rol'] == 'profe' and session['user'].get('profesor_id'):
            query_evals += " WHERE e.profesor_id = %s"
            params_evals.append(session['user']['profesor_id'])
        query_evals += " ORDER BY e.fecha DESC"
        cursor.execute(query_evals, params_evals)
        evaluaciones = cursor.fetchall()
        for ev in evaluaciones:
            ev['fecha'] = format_date_val(ev.get('fecha'))
            ev['hora'] = format_time_val(ev.get('hora'))
            ev['curso'] = {'nombre': ev['curso_nombre']}
            ev['asignatura'] = {'nombre': ev['asignatura_nombre']}

        cursor.execute("""
            SELECT al.*, c.nombre AS curso_nombre
            FROM alumnos al
            JOIN cursos c ON al.curso_id = c.id
            ORDER BY c.nombre ASC, al.apellido ASC, al.nombre ASC
        """)
        alumnos = cursor.fetchall()
        for a in alumnos:
            a['curso'] = {'nombre': a['curso_nombre']}
            a['nombre_completo'] = f"{a['nombre']} {a['apellido']}"
    conn.close()

    hoy = date.today().strftime('%Y-%m-%d')
    return render_template(
        'recuperaciones/crear.html',
        title='Agendar Recuperación',
        active='recuperaciones',
        evaluaciones=evaluaciones,
        alumnos=alumnos,
        hoy=hoy,
        alumno_id_preselect=request.args.get('alumno_id', type=int),
        evaluacion_id_preselect=request.args.get('evaluacion_id', type=int)
    )

@app.route('/recuperaciones/<int:recup_id>/completar', methods=['POST'])
@login_required
@role_required('profe', 'inspe', 'utp')
def completar_recuperacion(recup_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.*, e.profesor_id
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            WHERE r.id = %s
        """, (recup_id,))
        rec = cursor.fetchone()
        if not rec:
            conn.close()
            flash('Recuperación no encontrada.', 'danger')
            return redirect(url_for('listar_recuperaciones'))
        prof_id = resolve_profesor_id(session['user'], conn)
        if session['user']['rol'] == 'profe' and str(rec.get('profesor_id')) != str(prof_id):
            conn.close()
            flash('Acceso denegado: Solo el docente titular de la asignatura puede calificar o completar esta recuperación.', 'danger')
            return redirect(url_for('listar_recuperaciones'))
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
        cursor.execute("""
            SELECT r.*, e.profesor_id
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            WHERE r.id = %s
        """, (recup_id,))
        rec = cursor.fetchone()
        if not rec:
            conn.close()
            flash('Recuperación no encontrada.', 'danger')
            return redirect(url_for('listar_recuperaciones'))
        prof_id = resolve_profesor_id(session['user'], conn)
        if session['user']['rol'] == 'profe' and str(rec.get('profesor_id')) != str(prof_id):
            conn.close()
            flash('Acceso denegado: Solo el docente titular de la asignatura puede cancelar esta recuperación.', 'danger')
            return redirect(url_for('listar_recuperaciones'))
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
            cursor.execute("""
                SELECT r.*, e.profesor_id
                FROM recuperaciones r
                JOIN evaluaciones e ON r.evaluacion_id = e.id
                WHERE r.id = %s
            """, (recup_id,))
            rec = cursor.fetchone()
            if not rec:
                conn.close()
                flash('Recuperación no encontrada.', 'danger')
                return redirect(url_for('listar_recuperaciones'))
            prof_id = resolve_profesor_id(session['user'], conn)
            if session['user']['rol'] == 'profe' and str(rec.get('profesor_id')) != str(prof_id):
                conn.close()
                flash('Acceso denegado: Solo el docente titular de la asignatura puede modificar el estado de esta recuperación.', 'danger')
                return redirect(url_for('listar_recuperaciones'))
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

        # Historial completo de asistencias a evaluaciones
        cursor.execute("""
            SELECT ae.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   asig.nombre AS asignatura_nombre, asig.color AS asignatura_color
            FROM asistencia_evaluaciones ae
            JOIN evaluaciones e ON ae.evaluacion_id = e.id
            LEFT JOIN asignaturas a ON e.asignatura_id = a.id
            LEFT JOIN asignaturas asig ON e.asignatura_id = asig.id
            WHERE ae.alumno_id = %s
            ORDER BY e.fecha DESC
        """, (alumno_id,))
        raw_asistencias = cursor.fetchall()
        asistencias = []
        for row in raw_asistencias:
            asistencias.append({
                'asistencia': {
                    'presente': row.get('presente', 1),
                    'justificado': row.get('justificado', 0),
                    'motivo': row.get('motivo_inasistencia') or '',
                    'estado_asistencia': row.get('estado_asistencia') or ('justificado' if row.get('justificado') else ('presente' if row.get('presente') else 'injustificada'))
                },
                'evaluacion': {
                    'id': row['evaluacion_id'],
                    'titulo': row['eval_titulo'],
                    'fecha': format_date_val(row['eval_fecha']),
                    'asignatura': {
                        'nombre': row.get('asignatura_nombre') or 'General',
                        'color': row.get('asignatura_color') or '#14213D'
                    }
                }
            })

        cursor.execute("""
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            WHERE r.alumno_id = %s
            ORDER BY r.fecha_recuperacion DESC
        """, (alumno_id,))
        recuperaciones = cursor.fetchall()
        for r in recuperaciones:
            r['fecha_recuperacion'] = format_date_val(r.get('fecha_recuperacion'))
            r['eval_fecha'] = format_date_val(r.get('eval_fecha'))
            r['porcentaje_exigencia'] = float(r.get('exigencia') or 70.00)

        cursor.execute("SELECT COUNT(*) AS cnt FROM evaluaciones WHERE curso_id = %s", (alumno['curso_id'],))
        row_evals = cursor.fetchone()
        total_evals = row_evals['cnt'] if row_evals else 0
        total_ausencias = sum(1 for a in asistencias if not a['asistencia']['presente'])

    conn.close()
    return render_template(
        'alumnos/perfil.html',
        title=alumno['nombre_completo'],
        active='alumnos',
        alumno=alumno,
        asistencias=asistencias,
        inasistencias=[a for a in asistencias if not a['asistencia']['presente']],
        recuperaciones=recuperaciones,
        total_evals=total_evals,
        total_ausencias=total_ausencias
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
    user = session.get('user', {})
    with conn.cursor() as cursor:
        query = """
            SELECT r.*, e.titulo AS eval_titulo, e.fecha AS eval_fecha,
                   al.nombre AS alumno_nombre, al.apellido AS alumno_apellido,
                   al.rut AS alumno_rut, c.nombre AS curso_nombre, asig.nombre AS asignatura_nombre,
                   p.nombre AS profe_nombre, p.apellido AS profe_apellido
            FROM recuperaciones r
            JOIN evaluaciones e ON r.evaluacion_id = e.id
            JOIN alumnos al ON r.alumno_id = al.id
            JOIN cursos c ON al.curso_id = c.id
            JOIN asignaturas asig ON e.asignatura_id = asig.id
            LEFT JOIN profesores p ON e.profesor_id = p.id
            WHERE r.estado = 'pendiente'
        """
        params = []
        if user.get('rol') == 'profe' and user.get('profesor_id'):
            query += " AND e.profesor_id = %s"
            params.append(user['profesor_id'])
        query += " ORDER BY r.fecha_recuperacion ASC"
        cursor.execute(query, params)
        pendientes = cursor.fetchall()

        alumnos_por_eval = {}
        for r in pendientes:
            r['alumno'] = {
                'nombre_completo': f"{r['alumno_nombre']} {r['alumno_apellido']}",
                'rut': r['alumno_rut'],
                'curso': {'nombre': r['curso_nombre']}
            }
            prof_nom = f"{r.get('profe_nombre') or ''} {r.get('profe_apellido') or ''}".strip()
            r['evaluacion'] = {
                'id': r['evaluacion_id'],
                'titulo': r['eval_titulo'],
                'fecha': format_date_val(r.get('eval_fecha')),
                'asignatura': {'nombre': r['asignatura_nombre']},
                'curso': {'nombre': r['curso_nombre']},
                'profesor': {'nombre_completo': prof_nom or 'Docente'}
            }
            r['fecha_recuperacion'] = format_date_val(r.get('fecha_recuperacion'))
            r['porcentaje_exigencia'] = float(r.get('exigencia') or 70.00)

            ev_id = r['evaluacion_id']
            if ev_id not in alumnos_por_eval:
                alumnos_por_eval[ev_id] = []
            alumnos_por_eval[ev_id].append(r)
    conn.close()

    return render_template(
        'reportes/pendientes.html',
        title='Alumnos con Evaluaciones Pendientes',
        active='pendientes',
        pendientes=pendientes,
        alumnos_por_eval=alumnos_por_eval
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
        title='Configuración',
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
    return render_template('admin/profesores.html', title='Gestión de Profesores', active='profesores', data=profesores)

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
