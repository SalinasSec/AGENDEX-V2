from datetime import date, timedelta
from calendar import month_name, monthrange

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import db, Alumno, Curso, Evaluacion, Recuperacion
import calendar

reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.route("/calendario")
@login_required
def calendario():
    mes = request.args.get("mes", date.today().month, type=int)
    anio = request.args.get("anio", date.today().year, type=int)
    curso_id = request.args.get("curso_id", "", type=str)

    if mes < 1:
        mes = 12
        anio -= 1
    elif mes > 12:
        mes = 1
        anio += 1

    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, mes, monthrange(anio, mes)[1])

    q = Evaluacion.query.filter(
        Evaluacion.fecha >= primer_dia, Evaluacion.fecha <= ultimo_dia
    )

    # Los alumnos solo ven su propio curso
    if current_user.es_alumno:
        if current_user.alumno_id:
            alumno = db.session.get(Alumno, current_user.alumno_id)
            if alumno:
                q = q.filter(Evaluacion.curso_id == alumno.curso_id)
    elif curso_id:
        q = q.filter(Evaluacion.curso_id == int(curso_id))

    evaluaciones = q.order_by(Evaluacion.fecha, Evaluacion.hora).all()

    evals_por_dia = {}
    for ev in evaluaciones:
        dia = ev.fecha.day
        evals_por_dia.setdefault(dia, []).append(ev)

    cal = calendar.Calendar(firstweekday=0)
    semanas = cal.monthdayscalendar(anio, mes)

    cursos = Curso.query.order_by(Curso.nombre).all()
    meses = [(i, month_name[i]) for i in range(1, 13)]

    return render_template(
        "reportes/calendario.html",
        evals_por_dia=evals_por_dia,
        semanas=semanas,
        mes=mes,
        anio=anio,
        cursos=cursos,
        meses=meses,
        mes_nombre=month_name[mes],
        filtros={"curso_id": curso_id},
    )


@reportes_bp.route("/pendientes")
@login_required
def pendientes():
    # Un alumno solo ve sus propias recuperaciones pendientes
    if current_user.es_alumno:
        recuperaciones = (
            Recuperacion.query.filter_by(
                alumno_id=current_user.alumno_id, estado="pendiente"
            )
            .order_by(Recuperacion.fecha_recuperacion.asc())
            .all()
        )
        return render_template(
            "reportes/pendientes.html",
            recuperaciones=recuperaciones,
            alumnos_por_eval={},
        )

    recuperaciones = (
        Recuperacion.query.filter_by(estado="pendiente")
        .order_by(Recuperacion.fecha_recuperacion.asc())
        .all()
    )

    alumnos_por_eval = {}
    for rec in recuperaciones:
        alumnos_por_eval.setdefault(rec.evaluacion_id, []).append(rec)

    return render_template(
        "reportes/pendientes.html",
        recuperaciones=recuperaciones,
        alumnos_por_eval=alumnos_por_eval,
    )


@reportes_bp.route("/carga-evaluaciones")
@login_required
def carga_evaluaciones():
    cursos = Curso.query.order_by(Curso.nombre).all()

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    fin_mes = date(
        hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1]
    )

    datos_curso = []
    for curso in cursos:
        evals_mes = Evaluacion.query.filter(
            Evaluacion.curso_id == curso.id,
            Evaluacion.fecha >= inicio_mes,
            Evaluacion.fecha <= fin_mes,
        ).count()

        alumnos = Alumno.query.filter_by(curso_id=curso.id).count()
        evals_semana = Evaluacion.query.filter(
            Evaluacion.curso_id == curso.id,
            Evaluacion.fecha >= hoy,
            Evaluacion.fecha <= hoy + timedelta(days=7),
        ).count()

        datos_curso.append(
            {
                "curso": curso,
                "evals_mes": evals_mes,
                "evals_semana": evals_semana,
                "alumnos": alumnos,
            }
        )

    return render_template(
        "reportes/carga.html",
        datos_curso=datos_curso,
        mes_nombre=month_name[hoy.month],
        anio=hoy.year,
    )
