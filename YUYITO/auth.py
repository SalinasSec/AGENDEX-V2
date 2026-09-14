from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import ROLES, db, Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        clave = request.form["password"]

        user = Usuario.query.filter(
            db.func.lower(Usuario.correo) == correo
        ).first()

        if not user:
            flash("No se encontró una cuenta con ese correo.", "danger")
            return redirect(url_for("auth.login"))

        if not user.activo:
            flash("El usuario está desactivado. Contacta a la UTP.", "danger")
            return redirect(url_for("auth.login"))

        if not user.check_password(clave):
            flash("Contraseña incorrecta.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        session["rol"] = user.rol
        session["nombre"] = user.nombre
        flash(f"¡Bienvenido, {user.nombre}!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("auth.login"))


def role_required(*roles):
    """Decorador que restringe el acceso a los roles indicados."""

    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.rol not in roles:
                flash("No tienes permisos para acceder a esta sección.", "danger")
                return redirect(url_for("dashboard.index"))
            return f(*args, **kwargs)

        return wrapper

    return decorator
