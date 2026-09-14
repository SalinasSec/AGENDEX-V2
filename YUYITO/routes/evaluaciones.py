from datetime import date, datetime as dt

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy import text

from auth import role_required
from models import db, Alumno, Asignatura, Asistencia, Curso, Evaluacion, Profesor

evaluaciones_bp = Blueprint("evaluaciones", __name__)


def _generar_disponibilidad(curso_id, fecha, exclude_id=None):
    """Consulta el procedimiento almacenado de disponibilidad."""
    if exclude_id:
        total = Evaluacion.contar_en_fecha(curso_id, fecha, exclude_id)
        return total, 2, 2 - total
    row = db.session.execute(
        text("CALL sp_validar_disponibilidad(:curso_id, :fecha)"),
        {"curso_id": curso_id, "fecha": fecha},
    ).fetchone()
    db.session.commit()  # cierra el CALL
    if row:
        return row.existentes, row.maximo, row.disponibles
    return None


@evaluaciones_bp.route("/")
@login_required
def listar():
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    curso_id = request.args.get("curso_id", "", type=str)
    asignatura_id = request.args.get("asignatura_id", "", type=str)

    q = Evaluacion.query

    # Un alumno solo ve las evaluaciones de su propio curso
    if current_user.es_alumno and current_user.alumno_id:
        alumno = db.session.get(Alumno, current_user.alumno_id)
        if alumno:
            q = q.filter(Evaluacion.curso_id == alumno.curso_id)
            curso_id = str(alumno.curso_id)

    if fecha_desde:
        q = q.filter(Evaluacion.fecha >= fecha_desde)
    if fecha_hasta:
        q = q.filter(Evaluacion.fecha <= fecha_hasta)
    if curso_id:
        q = q.filter(Evaluacion.curso_id == int(curso_id))
    if asignatura_id:
        q = q.filter(Evaluacion.asignatura_id == int(asignatura_id))

    evaluaciones = q.order_by(Evaluacion.fecha.desc(), Evaluacion.hora.asc()).all()
    cursos = Curso.query.order_by(Curso.nombre).all()
    asignaturas = Asignatura.query.order_by(Asignatura.nombre).all()

    return render_template(
        "evaluaciones/listar.html",
        evaluaciones=evaluaciones,
        cursos=cursos,
        asignaturas=asignaturas,
        filtros={
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "curso_id": curso_id,
            "asignatura_id": asignatura_id,
        },
    )


@evaluaciones_bp.route("/crear", methods=["GET", "POST"])
@role_required("profe")
def crear():
    if not current_user.profesor_id:
        flash(
            "Tu usuario de profesor no está vinculado a un registro de Profesor. Contacta a UTP.",
            "danger",
        )
        return redirect(url_for("evaluaciones.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        fecha_str = request.form["fecha"]
        hora_str = request.form.get("hora", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        asignatura_id = int(request.form["asignatura_id"])
        curso_id = int(request.form["curso_id"])
        # El profesor siempre agenda a su propio nombre; se ignora
        # cualquier profesor_id que llegue del formulario.
        profesor_id = current_user.profesor_id

        fecha_eval = date.fromisoformat(fecha_str)
        hora = dt.strptime(hora_str, "%H:%M").time() if hora_str else None

        try:
            result = db.session.execute(
                text("CALL sp_crear_evaluacion(:t, :f, :h, :d, :a, :c, :p)"),
                {
                    "t": titulo,
                    "f": fecha_eval,
                    "h": hora,
                    "d": descripcion,
                    "a": asignatura_id,
                    "c": curso_id,
                    "p": profesor_id,
                },
            ).fetchone()
            db.session.commit()
            new_id = result.id if result else None
            flash("Evaluación creada exitosamente.", "success")
            if new_id:
                return redirect(url_for("evaluaciones.detalle", id=new_id))
            return redirect(url_for("evaluaciones.listar"))
        except Exception as e:
            db.session.rollback()
            msg = str(e)
            if "Limite excedido" in msg:
                flash(
                    "Límite alcanzado: máximo 2 evaluaciones por curso por día.",
                    "danger",
                )
            else:
                flash(f"No se pudo crear la evaluación: {msg}", "danger")
            return redirect(url_for("evaluaciones.crear"))

    cursos = Curso.query.order_by(Curso.nombre).all()
    asignaturas = Asignatura.query.order_by(Asignatura.nombre).all()
    mi_profesor = db.session.get(Profesor, current_user.profesor_id)
    return render_template(
        "evaluaciones/crear.html",
        cursos=cursos,
        asignaturas=asignaturas,
        mi_profesor=mi_profesor,
        hoy=date.today().isoformat(),
    )


@evaluaciones_bp.route("/<int:id>")
@login_required
def detalle(id):
    from flask import abort

    ev = db.session.get(Evaluacion, id)
    if not ev:
        abort(404)

    # Si es alumno, solo ve si pertenece a su curso
    if current_user.es_alumno:
        if not current_user.alumno_id:
            abort(403)
        alumno = db.session.get(Alumno, current_user.alumno_id)
        if not alumno or ev.curso_id != alumno.curso_id:
            abort(403)

    alumnos_curso = (
        Alumno.query.filter_by(curso_id=ev.curso_id).order_by(Alumno.apellido).all()
    )
    asistencias = {
        a.alumno_id: a for a in Asistencia.query.filter_by(evaluacion_id=id).all()
    }
    return render_template(
        "evaluaciones/detalle.html",
        ev=ev,
        alumnos=alumnos_curso,
        asistencias=asistencias,
    )


@evaluaciones_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@role_required("profe")
def editar(id):
    from flask import abort

    ev = db.session.get(Evaluacion, id)
    if not ev:
        abort(404)

    if ev.profesor_id != current_user.profesor_id:
        flash("Solo el profesor que creó esta evaluación puede editarla.", "danger")
        abort(403)

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        fecha = date.fromisoformat(request.form["fecha"])
        hora_str = request.form.get("hora", "").strip()
        hora = dt.strptime(hora_str, "%H:%M").time() if hora_str else None
        descripcion = request.form.get("descripcion", "").strip()
        asignatura_id = int(request.form["asignatura_id"])
        curso_id = int(request.form["curso_id"])
        # El profesor no puede reasignar la prueba a otro profesor.
        profesor_id = current_user.profesor_id

        try:
            db.session.execute(
                text(
                    "CALL sp_actualizar_evaluacion(:id, :t, :f, :h, :d, :a, :c, :p)"
                ),
                {
                    "id": id,
                    "t": titulo,
                    "f": fecha,
                    "h": hora,
                    "d": descripcion,
                    "a": asignatura_id,
                    "c": curso_id,
                    "p": profesor_id,
                },
            )
            db.session.commit()
            flash("Evaluación actualizada.", "success")
            return redirect(url_for("evaluaciones.detalle", id=id))
        except Exception as e:
            db.session.rollback()
            msg = str(e)
            if "Limite excedido" in msg:
                flash(
                    "Límite alcanzado: máximo 2 evaluaciones por curso por día.",
                    "danger",
                )
            else:
                flash(f"No se pudo actualizar: {msg}", "danger")
            return redirect(url_for("evaluaciones.editar", id=id))

    cursos = Curso.query.order_by(Curso.nombre).all()
    asignaturas = Asignatura.query.order_by(Asignatura.nombre).all()
    return render_template(
        "evaluaciones/editar.html",
        ev=ev,
        cursos=cursos,
        asignaturas=asignaturas,
    )


@evaluaciones_bp.route("/<int:id>/eliminar", methods=["POST"])
@role_required("profe")
def eliminar(id):
    from flask import abort

    ev = db.session.get(Evaluacion, id)
    if not ev:
        abort(404)
    if ev.profesor_id != current_user.profesor_id:
        flash("Solo el profesor que creó esta evaluación puede eliminarla.", "danger")
        abort(403)
    db.session.delete(ev)
    db.session.commit()
    flash("Evaluación eliminada.", "success")
    return redirect(url_for("evaluaciones.listar"))


@evaluaciones_bp.route("/<int:id>/asistencia", methods=["POST"])
@role_required("profe", "inspe", "utp")
def registrar_asistencia(id):
    from flask import abort

    ev = db.session.get(Evaluacion, id)
    if not ev:
        abort(404)

    alumnos_curso = Alumno.query.filter_by(curso_id=ev.curso_id).all()

    # Solo Inspectoría (o UTP) puede marcar/editar el justificativo de una
    # ausencia. Un profesor puede registrar la inasistencia y el motivo,
    # pero no decide si queda justificada.
    puede_justificar = current_user.rol in ("inspe", "utp")

    for alumno in alumnos_curso:
        presente = request.form.get(f"alumno_{alumno.id}") == "on"
        motivo = request.form.get(f"motivo_{alumno.id}", "").strip()

        existing = Asistencia.query.filter_by(
            evaluacion_id=id, alumno_id=alumno.id
        ).first()

        if existing:
            existing.presente = presente
            existing.motivo = motivo
            if puede_justificar:
                existing.justificado = (
                    request.form.get(f"justificado_{alumno.id}") == "on"
                )
        else:
            justificado = False
            if puede_justificar:
                justificado = request.form.get(f"justificado_{alumno.id}") == "on"
            db.session.add(
                Asistencia(
                    evaluacion_id=id,
                    alumno_id=alumno.id,
                    presente=presente,
                    motivo=motivo if motivo else None,
                    justificado=justificado,
                )
            )

    db.session.commit()
    flash("Asistencia registrada exitosamente.", "success")
    return redirect(url_for("evaluaciones.detalle", id=id))


@evaluaciones_bp.route("/api/disponibilidad")
@login_required
def api_disponibilidad():
    curso_id = request.args.get("curso_id", type=int)
    fecha_str = request.args.get("fecha")

    if not curso_id or not fecha_str:
        return jsonify({"error": "Faltan parámetros"}), 400

    fecha = date.fromisoformat(fecha_str)
    info = _generar_disponibilidad(curso_id, fecha)

    evals_existentes = (
        Evaluacion.query.filter_by(curso_id=curso_id, fecha=fecha).all()
    )

    return jsonify(
        {
            "existentes": info[0] if info else 0,
            "maximo": 2,
            "disponibles": info[2] if info else 0,
            "evaluaciones": [
                {
                    "id": e.id,
                    "titulo": e.titulo,
                    "asignatura": e.asignatura.nombre,
                }
                for e in evals_existentes
            ],
        }
    )
