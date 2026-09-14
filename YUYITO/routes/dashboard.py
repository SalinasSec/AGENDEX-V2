from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db, Alumno, Curso, Evaluacion, Recuperacion

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()

    # ---------- ALUMNO: solo su propio contexto ----------
    if current_user.es_alumno:
        alumno = None
        if current_user.alumno_id:
            alumno = db.session.get(Alumno, current_user.alumno_id)

        # Si el alumno no está vinculado a un registro de alumno, solo se
        # muestra información general del calendario.
        evals_hoy = Evaluacion.query.filter_by(fecha=today).all()
        mis_evals = []
        mis_recuperaciones = []
        total_mis_evals = 0
        if alumno:
            curso_eval = (
                Evaluacion.query.filter_by(curso_id=alumno.curso_id)
                .order_by(Evaluacion.fecha.desc())
                .all()
            )
            mis_evals = curso_eval
            total_mis_evals = len(curso_eval)
            mis_recuperaciones = (
                Recuperacion.query.filter_by(alumno_id=alumno.id)
                .order_by(Recuperacion.fecha_recuperacion.desc())
                .limit(5)
                .all()
            )

        stats = {
            "total_evaluaciones": total_mis_evals,
            "evals_hoy": sum(1 for e in mis_evals if e.fecha == today),
            "evals_semana": sum(
                1
                for e in mis_evals
                if today <= e.fecha <= today + timedelta(days=7)
            ),
            "total_alumnos": 1,
            "recuperaciones_pendientes": sum(
                1 for r in mis_recuperaciones if r.estado == "pendiente"
            ),
        }
        return render_template(
            "index_alumno.html",
            stats=stats,
            mis_evals=mis_evals,
            mis_recuperaciones=mis_recuperaciones,
            alumno=alumno,
        )

    # ---------- OTROS ROLES: vista general ----------
    evals_hoy = Evaluacion.query.filter_by(fecha=today).all()
    evals_semana = Evaluacion.query.filter(
        Evaluacion.fecha >= today, Evaluacion.fecha <= today + timedelta(days=7)
    ).all()

    ultimas_evals = (
        Evaluacion.query.order_by(Evaluacion.fecha.desc(), Evaluacion.hora.desc())
        .limit(5)
        .all()
    )

    evals_por_curso = (
        db.session.query(Curso.nombre, func.count(Evaluacion.id))
        .join(Evaluacion, Curso.id == Evaluacion.curso_id)
        .group_by(Curso.nombre)
        .order_by(func.count(Evaluacion.id).desc())
        .all()
    )

    recuperaciones_pendientes = (
        Recuperacion.query.filter_by(estado="pendiente")
        .order_by(Recuperacion.fecha_recuperacion)
        .limit(5)
        .all()
    )

    stats = {
        "total_evaluaciones": Evaluacion.query.count(),
        "evals_hoy": len(evals_hoy),
        "evals_semana": len(evals_semana),
        "total_alumnos": Alumno.query.count(),
        "recuperaciones_pendientes": Recuperacion.query.filter_by(
            estado="pendiente"
        ).count(),
    }

    return render_template(
        "index.html",
        stats=stats,
        ultimas_evals=ultimas_evals,
        evals_por_curso=evals_por_curso,
        recuperaciones_pendientes=recuperaciones_pendientes,
        evals_hoy=evals_hoy,
        evals_semana=evals_semana,
    )
