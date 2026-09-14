from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, current_user

from auth import role_required
from models import (
    db,
    Alumno,
    Asistencia,
    Evaluacion,
    Recuperacion,
    EXIGENCIA_JUSTIFICADO,
    EXIGENCIA_NO_JUSTIFICADO,
)

recuperaciones_bp = Blueprint("recuperaciones", __name__)


@recuperaciones_bp.route("/")
@login_required
def listar():
    # Los alumnos ven SOLO sus propias recuperaciones
    if current_user.es_alumno:
        if current_user.alumno_id:
            recuperaciones = (
                Recuperacion.query.filter_by(alumno_id=current_user.alumno_id)
                .order_by(Recuperacion.fecha_recuperacion.asc())
                .all()
            )
        else:
            recuperaciones = []
        return render_template(
            "recuperaciones/mis_recuperaciones.html",
            recuperaciones=recuperaciones,
        )

    estado = request.args.get("estado", "")
    q = Recuperacion.query
    if estado:
        q = q.filter_by(estado=estado)

    recuperaciones = q.order_by(Recuperacion.fecha_recuperacion.asc()).all()
    return render_template(
        "recuperaciones/listar.html",
        recuperaciones=recuperaciones,
        filtros={"estado": estado},
    )


@recuperaciones_bp.route("/crear", methods=["GET", "POST"])
@role_required("utp", "profe", "inspe")
def crear():
    if request.method == "POST":
        evaluacion_id = int(request.form["evaluacion_id"])
        alumno_id = int(request.form["alumno_id"])
        fecha_str = request.form["fecha_recuperacion"]
        motivo = request.form.get("motivo", "").strip()

        fecha_rec = date.fromisoformat(fecha_str)

        existing = Recuperacion.query.filter_by(
            evaluacion_id=evaluacion_id, alumno_id=alumno_id, estado="pendiente"
        ).first()
        if existing:
            flash(
                "Ya existe una recuperación pendiente para este alumno en esta evaluación.",
                "danger",
            )
            return redirect(url_for("recuperaciones.crear"))

        # La exigencia de la recuperación depende de si Inspectoría/UTP
        # justificó la inasistencia registrada para esa evaluación:
        # justificada -> misma exigencia que el resto (60%)
        # no justificada (o sin registro de asistencia) -> mayor exigencia (70%)
        asistencia = Asistencia.query.filter_by(
            evaluacion_id=evaluacion_id, alumno_id=alumno_id
        ).first()
        porcentaje = (
            EXIGENCIA_JUSTIFICADO
            if asistencia and asistencia.justificado
            else EXIGENCIA_NO_JUSTIFICADO
        )

        rec = Recuperacion(
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            fecha_recuperacion=fecha_rec,
            motivo=motivo,
            porcentaje_exigencia=porcentaje,
        )
        db.session.add(rec)
        db.session.commit()
        if porcentaje == EXIGENCIA_JUSTIFICADO:
            flash(
                f"Fecha de recuperación asignada. Ausencia justificada: rinde con {porcentaje:.0f}% de exigencia (igual que el curso).",
                "success",
            )
        else:
            flash(
                f"Fecha de recuperación asignada. Ausencia sin justificar: rinde con {porcentaje:.0f}% de exigencia.",
                "warning",
            )
        return redirect(url_for("recuperaciones.listar"))

    evaluaciones = Evaluacion.query.order_by(Evaluacion.fecha.desc()).all()
    alumnos = Alumno.query.order_by(Alumno.apellido).all()
    return render_template(
        "recuperaciones/crear.html",
        evaluaciones=evaluaciones,
        alumnos=alumnos,
        hoy=date.today().isoformat(),
    )


@recuperaciones_bp.route("/<int:id>/completar", methods=["POST"])
@role_required("utp", "profe", "inspe")
def completar(id):
    rec = db.session.get(Recuperacion, id)
    if rec:
        rec.estado = "completada"
        db.session.commit()
        flash("Recuperación marcada como completada.", "success")
    return redirect(url_for("recuperaciones.listar"))


@recuperaciones_bp.route("/<int:id>/cancelar", methods=["POST"])
@role_required("utp", "profe", "inspe")
def cancelar(id):
    rec = db.session.get(Recuperacion, id)
    if rec:
        rec.estado = "cancelada"
        db.session.commit()
        flash("Recuperación cancelada.", "success")
    return redirect(url_for("recuperaciones.listar"))
