from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, current_user

from auth import role_required
from models import (
    db,
    Alumno,
    Asistencia,
    Curso,
    Evaluacion,
    Recuperacion,
)


alumnos_bp = Blueprint("alumnos", __name__)


@alumnos_bp.route("/")
@role_required("utp", "profe", "inspe")
def listar():
    curso_id = request.args.get("curso_id", "", type=str)
    busqueda = request.args.get("busqueda", "").strip()

    q = Alumno.query

    if curso_id:
        q = q.filter_by(curso_id=int(curso_id))
    if busqueda:
        like = f"%{busqueda}%"
        q = q.filter(
            (Alumno.nombre.like(like))
            | (Alumno.apellido.like(like))
            | (Alumno.rut.like(like))
        )

    alumnos = q.order_by(Alumno.apellido, Alumno.nombre).all()
    cursos = Curso.query.order_by(Curso.nombre).all()

    return render_template(
        "alumnos/listar.html",
        alumnos=alumnos,
        cursos=cursos,
        filtros={"curso_id": curso_id, "busqueda": busqueda},
    )


@alumnos_bp.route("/crear", methods=["GET", "POST"])
@role_required("utp")
def crear():
    if request.method == "POST":
        rut = request.form["rut"].strip()
        nombre = request.form["nombre"].strip()
        apellido = request.form["apellido"].strip()
        curso_id = int(request.form["curso_id"])

        if Alumno.query.filter_by(rut=rut).first():
            flash("Ya existe un alumno con ese RUT.", "danger")
            return redirect(url_for("alumnos.crear"))

        alumno = Alumno(rut=rut, nombre=nombre, apellido=apellido, curso_id=curso_id)
        db.session.add(alumno)
        db.session.commit()

        flash(f"Alumno {alumno.nombre_completo} creado exitosamente.", "success")
        return redirect(url_for("alumnos.perfil", id=alumno.id))

    cursos = Curso.query.order_by(Curso.nombre).all()
    return render_template("alumnos/crear.html", cursos=cursos)


@alumnos_bp.route("/<int:id>")
@login_required
def perfil(id):
    alumno = db.session.get(Alumno, id)
    if not alumno:
        abort(404)

    # Un alumno solo puede ver su propio perfil
    if current_user.es_alumno:
        if not current_user.alumno_id or current_user.alumno_id != id:
            abort(403)

    asistencias = (
        db.session.query(Asistencia, Evaluacion)
        .join(Evaluacion, Asistencia.evaluacion_id == Evaluacion.id)
        .filter(Asistencia.alumno_id == id)
        .order_by(Evaluacion.fecha.desc())
        .all()
    )

    total_evals = Evaluacion.query.filter_by(curso_id=alumno.curso_id).count()
    total_ausencias = Asistencia.query.filter_by(
        alumno_id=id, presente=False
    ).count()

    recuperaciones = (
        Recuperacion.query.filter_by(alumno_id=id)
        .join(Evaluacion, Recuperacion.evaluacion_id == Evaluacion.id)
        .order_by(Recuperacion.fecha_recuperacion.desc())
        .all()
    )

    return render_template(
        "alumnos/perfil.html",
        alumno=alumno,
        asistencias=asistencias,
        total_evals=total_evals,
        total_ausencias=total_ausencias,
        recuperaciones=recuperaciones,
    )


@alumnos_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@role_required("utp")
def editar(id):
    alumno = db.session.get(Alumno, id)
    if not alumno:
        abort(404)

    if request.method == "POST":
        alumno.rut = request.form["rut"].strip()
        alumno.nombre = request.form["nombre"].strip()
        alumno.apellido = request.form["apellido"].strip()
        alumno.curso_id = int(request.form["curso_id"])

        existing = Alumno.query.filter(
            Alumno.rut == alumno.rut, Alumno.id != alumno.id
        ).first()
        if existing:
            flash("Ya existe otro alumno con ese RUT.", "danger")
            return redirect(url_for("alumnos.editar", id=id))

        db.session.commit()
        flash("Alumno actualizado.", "success")
        return redirect(url_for("alumnos.perfil", id=id))

    cursos = Curso.query.order_by(Curso.nombre).all()
    return render_template("alumnos/editar.html", alumno=alumno, cursos=cursos)


@alumnos_bp.route("/<int:id>/eliminar", methods=["POST"])
@role_required("utp")
def eliminar(id):
    alumno = db.session.get(Alumno, id)
    if alumno:
        nombre = alumno.nombre_completo
        db.session.delete(alumno)
        db.session.commit()
        flash(f"Alumno {nombre} eliminado.", "success")
    return redirect(url_for("alumnos.listar"))
