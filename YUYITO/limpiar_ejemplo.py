"""Limpia los datos de ejemplo creados por seed_ejemplo.py.

Uso:  .venv\\Scripts\\python.exe limpiar_ejemplo.py

Borra evaluaciones, asistencias, recuperaciones, alumnos, profesores,
asignaturas y los usuarios de ejemplo. Deja intactos los cursos del
liceo y los usuarios iniciales (utp/profe/inspe/alumno).
"""
from app import create_app
from models import (
    db,
    Alumno,
    Asignatura,
    Asistencia,
    Evaluacion,
    Profesor,
    Recuperacion,
    Curso,
    Usuario,
)

app = create_app()

USUARIOS_EJEMPLO = {
    "carolina.reyes@liceosofofa.cl",
    "rodrigo.araya@liceosofofa.cl",
    "joaquin.rivas@liceorbl.cl",
    "inspe.diaz@liceorbl.cl",
}


def main():
    with app.app_context():
        # Borrar en orden (respetando FKs): recuperaciones, asistencias,
        # evaluaciones, luego alumnos/profesores/asignaturas.
        Recuperacion.query.delete()
        Asistencia.query.delete()
        Evaluacion.query.delete()
        Alumno.query.delete()
        Profesor.query.delete()
        Asignatura.query.delete()
        for correo in USUARIOS_EJEMPLO:
            u = Usuario.query.filter_by(correo=correo).first()
            if u:
                db.session.delete(u)
        db.session.commit()

        resto = {
            "cursos": Curso.query.count(),
            "usuarios": Usuario.query.count(),
            "asignaturas": Asignatura.query.count(),
            "profesores": Profesor.query.count(),
            "alumnos": Alumno.query.count(),
            "evaluaciones": Evaluacion.query.count(),
        }
        print("Datos de ejemplo eliminados.")
        print("Estado de la base:", resto)


if __name__ == "__main__":
    main()
