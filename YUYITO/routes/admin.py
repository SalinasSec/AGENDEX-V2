from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from auth import role_required
from models import db, Curso, Asignatura, Profesor, Alumno, Usuario, ROLES

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@role_required("utp")
def index():
    return render_template(
        "admin/index.html",
        cursos=Curso.query.order_by(Curso.nombre).all(),
        asignaturas=Asignatura.query.order_by(Asignatura.nombre).all(),
        profesores=Profesor.query.order_by(Profesor.apellido).all(),
        alumnos=Alumno.query.count(),
        usuarios=Usuario.query.all(),
    )


@admin_bp.route("/cursos", methods=["GET", "POST"])
@role_required("utp")
def cursos():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        nivel = request.form["nivel"].strip()
        if Curso.query.filter_by(nombre=nombre).first():
            flash("Ya existe un curso con ese nombre.", "danger")
        else:
            db.session.add(Curso(nombre=nombre, nivel=nivel))
            db.session.commit()
            flash(f"Curso '{nombre}' creado.", "success")
        return redirect(url_for("admin.cursos"))

    data = Curso.query.order_by(Curso.nombre).all()
    return render_template("admin/cursos.html", data=data)


@admin_bp.route("/cursos/<int:id>/eliminar", methods=["POST"])
@role_required("utp")
def curso_eliminar(id):
    c = db.session.get(Curso, id)
    if c:
        db.session.delete(c)
        db.session.commit()
        flash("Curso eliminado.", "success")
    return redirect(url_for("admin.cursos"))


@admin_bp.route("/asignaturas", methods=["GET", "POST"])
@role_required("utp")
def asignaturas():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        color = request.form.get("color", "#3498db")
        if Asignatura.query.filter_by(nombre=nombre).first():
            flash("Ya existe una asignatura con ese nombre.", "danger")
        else:
            db.session.add(Asignatura(nombre=nombre, color=color))
            db.session.commit()
            flash(f"Asignatura '{nombre}' creada.", "success")
        return redirect(url_for("admin.asignaturas"))

    data = Asignatura.query.order_by(Asignatura.nombre).all()
    return render_template("admin/asignaturas.html", data=data)


@admin_bp.route("/asignaturas/<int:id>/eliminar", methods=["POST"])
@role_required("utp")
def asignatura_eliminar(id):
    a = db.session.get(Asignatura, id)
    if a:
        db.session.delete(a)
        db.session.commit()
        flash("Asignatura eliminada.", "success")
    return redirect(url_for("admin.asignaturas"))


@admin_bp.route("/profesores", methods=["GET", "POST"])
@role_required("utp")
def profesores():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        apellido = request.form["apellido"].strip()
        email = request.form.get("email", "").strip()
        db.session.add(Profesor(nombre=nombre, apellido=apellido, email=email or None))
        db.session.commit()
        flash(f"Profesor {nombre} {apellido} creado.", "success")
        return redirect(url_for("admin.profesores"))

    data = Profesor.query.order_by(Profesor.apellido).all()
    return render_template("admin/profesores.html", data=data)


@admin_bp.route("/profesores/<int:id>/eliminar", methods=["POST"])
@role_required("utp")
def profesor_eliminar(id):
    p = db.session.get(Profesor, id)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash("Profesor eliminado.", "success")
    return redirect(url_for("admin.profesores"))


@admin_bp.route("/usuarios", methods=["GET", "POST"])
@role_required("utp")
def usuarios():
    if request.method == "POST":
        rut = request.form["rut"].strip()
        correo = request.form["correo"].strip().lower()
        clave = request.form["password"]
        nombre = request.form["nombre"].strip()
        rol = request.form["rol"]

        if Usuario.query.filter_by(rut=rut).first():
            flash("Ya existe un usuario con ese RUT.", "danger")
            return redirect(url_for("admin.usuarios"))

        if Usuario.query.filter(
            db.func.lower(Usuario.correo) == correo
        ).first():
            flash("Ya existe un usuario con ese correo.", "danger")
            return redirect(url_for("admin.usuarios"))

        nuevo = Usuario(rut=rut, correo=correo, nombre=nombre, rol=rol)
        nuevo.set_password(clave)
        db.session.add(nuevo)
        db.session.commit()
        flash(f"Usuario '{correo}' creado con rol {ROLES[rol]}.", "success")
        return redirect(url_for("admin.usuarios"))

    data = Usuario.query.order_by(Usuario.rol, Usuario.correo).all()
    return render_template("admin/usuarios.html", data=data, roles=ROLES)


@admin_bp.route("/usuarios/<string:rut>/togglerestado", methods=["POST"])
@role_required("utp")
def usuario_toggle(rut):
    u = db.session.get(Usuario, rut)
    if u:
        u.activo = not u.activo
        db.session.commit()
        flash(f"Usuario '{u.correo}' {'activado' if u.activo else 'desactivado'}.", "success")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<string:rut>/eliminar", methods=["POST"])
@role_required("utp")
def usuario_eliminar(rut):
    u = db.session.get(Usuario, rut)
    if u:
        db.session.delete(u)
        db.session.commit()
        flash("Usuario eliminado.", "success")
    return redirect(url_for("admin.usuarios"))
