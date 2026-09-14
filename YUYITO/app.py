from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
from models import db, Usuario

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, user_id)

    from auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.evaluaciones import evaluaciones_bp
    from routes.alumnos import alumnos_bp
    from routes.recuperaciones import recuperaciones_bp
    from routes.reportes import reportes_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")
    app.register_blueprint(alumnos_bp, url_prefix="/alumnos")
    app.register_blueprint(recuperaciones_bp, url_prefix="/recuperaciones")
    app.register_blueprint(reportes_bp, url_prefix="/reportes")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_globals():
        from datetime import date
        from models import Curso, Alumno, Evaluacion, Recuperacion
        from models import ROLES
        return {
            "today": date.today(),
            "current_user": current_user,
            "ROLES": ROLES,
            "total_cursos": Curso.query.count(),
            "total_alumnos": Alumno.query.count(),
            "total_evaluaciones": Evaluacion.query.count(),
            "recuperaciones_pendientes": Recuperacion.query.filter_by(estado="pendiente").count(),
        }

    return app


if __name__ == "__main__":
    import os

    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
