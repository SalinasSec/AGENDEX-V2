"""Datos de ejemplo para probar AgendEx como si estuviera en practica.

Uso:  .venv\\Scripts\\python.exe seed_ejemplo.py

Crea asignaturas, profesores repartidos, alumnos, usuarios vinculados
y algunas evaluaciones. Cuando pases a la realidad, ejecuta:
    .venv\\Scripts\\python.exe limpiar_ejemplo.py
para dejar la base como estaba (solo cursos + usuarios iniciales).
"""
from datetime import date

from app import create_app
from models import (
    db,
    Alumno,
    Asignatura,
    Curso,
    Evaluacion,
    Profesor,
    Usuario,
)

app = create_app()


ASIGNATURAS = {
    "Lenguaje y Comunicación": {"color": "#2F6F4E"},
    "Matemática": {"color": "#14213D"},
    "Historia": {"color": "#A87F2C"},
    "Inglés": {"color": "#2C5F7A"},
    "Educación Física": {"color": "#A5332A"},
    "Ciencias Naturales": {"color": "#3B7A6B"},
    "Programación": {"color": "#1E3157"},
    "Bases de Datos": {"color": "#4A3B7A"},
}

PROFESORES = [
    {"nombre": "Carolina", "apellido": "Reyes", "email": "c.reyes@liceo.cl",
     "materia": "Matemática"},
    {"nombre": "Patricio", "apellido": "Muñoz", "email": "p.munoz@liceo.cl",
     "materia": "Lenguaje y Comunicación"},
    {"nombre": "Valentina", "apellido": "Soto", "email": "v.soto@liceo.cl",
     "materia": "Historia"},
    {"nombre": "Diego", "apellido": "Fuentes", "email": "d.fuentes@liceo.cl",
     "materia": "Inglés"},
    {"nombre": "Marcela", "apellido": "Vargas", "email": "m.vargas@liceo.cl",
     "materia": "Ciencias Naturales"},
    {"nombre": "Rodrigo", "apellido": "Araya", "email": "r.araya@liceo.cl",
     "materia": "Programación"},
    {"nombre": "Andrea", "apellido": "Pizarro", "email": "a.pizarro@liceo.cl",
     "materia": "Bases de Datos"},
]

ALUMNOS = [
    ("20.123.456-1", "Joaquín", "Rivas", "4G"),
    ("20.234.567-2", "Camila", "Torres", "4G"),
    ("20.345.678-3", "Bastián", "Núñez", "4G"),
    ("21.111.222-3", "Francisca", "Lara", "3G"),
    ("20.555.666-7", "Matías", "González", "1A"),
    ("19.888.999-0", "Antonia", "Sepúlveda", "2F"),
]

# Evaluaciones de ejemplo por curso/asignatura/profesor (max 2 por curso y dia)
EVALUACIONES = [
    {"titulo": "Prueba números enteros",
     "fecha": "2026-09-02", "hora": "10:00", "materia": "Matemática",
     "curso": "1A", "prof_email": "c.reyes@liceo.cl"},
    {"titulo": "Ensayo narrativo",
     "fecha": "2026-09-03", "hora": "08:30", "materia": "Lenguaje y Comunicación",
     "curso": "1A", "prof_email": "p.munoz@liceo.cl"},
    {"titulo": "Parcial funciones",
     "fecha": "2026-09-04", "hora": "09:00", "materia": "Matemática",
     "curso": "2F", "prof_email": "c.reyes@liceo.cl"},
    {"titulo": "Prueba POO en Python",
     "fecha": "2026-09-05", "hora": "08:00", "materia": "Programación",
     "curso": "4G", "prof_email": "r.araya@liceo.cl"},
    {"titulo": "Taller modelo entidad-relación",
     "fecha": "2026-09-05", "hora": "11:00", "materia": "Bases de Datos",
     "curso": "4G", "prof_email": "a.pizarro@liceo.cl"},
    {"titulo": "Prueba verbos en inglés",
     "fecha": "2026-09-08", "hora": "10:30", "materia": "Inglés",
     "curso": "3G", "prof_email": "d.fuentes@liceo.cl"},
]


def crear_login(user, clave):
    """Genera el hash scrypt (mismo metodo que usuarios_iniciales)."""
    return Usuario(rut=user).set_password(clave)


def main():
    with app.app_context():
        # Seguridad: no correr dos veces
        if Asignatura.query.count() > 0:
            print("Ya hay asignaturas; skip (usa limpiar_ejemplo.py para reiniciar).")
            return

        # --- Asignaturas ---
        asignaturas = {}
        for nombre, info in ASIGNATURAS.items():
            a = Asignatura(nombre=nombre, color=info["color"])
            db.session.add(a)
            asignaturas[nombre] = a
        db.session.flush()
        for nombre in ASIGNATURAS:
            asignaturas[nombre] = Asignatura.query.filter_by(nombre=nombre).first()

        # --- Profesores ---
        profesores = {}  # email -> profe
        for p in PROFESORES:
            prof = Profesor(nombre=p["nombre"], apellido=p["apellido"],
                            email=p["email"])
            db.session.add(prof)
        db.session.flush()
        for p in PROFESORES:
            profesores[p["email"]] = Profesor.query.filter_by(email=p["email"]).first()

        # --- Cursos (mapa por nombre) ---
        cursos = {c.nombre: c for c in Curso.query.all()}

        # --- Alumnos ---
        alumno_por_rut = {}
        for rut, n, ap, curso_nom in ALUMNOS:
            curso = cursos.get(curso_nom)
            if not curso:
                print(f"  ! Curso {curso_nom} no existe; se omite {rut}")
                continue
            al = Alumno(rut=rut, nombre=n, apellido=ap, curso_id=curso.id)
            db.session.add(al)
            alumno_por_rut[rut] = al
        db.session.flush()

        # --- Evaluaciones ---
        for ev in EVALUACIONES:
            asig = asignaturas.get(ev["materia"])
            curso = cursos.get(ev["curso"])
            prof = profesores.get(ev["prof_email"])
            if not (asig and curso and prof):
                print(f"  ! Falta referencia para {ev['titulo']}, se omite")
                continue
            e = Evaluacion(
                titulo=ev["titulo"],
                fecha=date.fromisoformat(ev["fecha"]),
                hora=__import__("datetime").datetime.strptime(ev["hora"], "%H:%M").time(),
                asignatura_id=asig.id,
                curso_id=curso.id,
                profesor_id=prof.id,
            )
            db.session.add(e)

        db.session.commit()

        # --- Usuarios de ejemplo (vinculados) ---
        # profe_reyes vinculado a Carolina Reyes (Matemática)
        u_profe = Usuario(rut="15.111.222-3", correo="carolina.reyes@liceosofofa.cl",
                          rol="profe", nombre="Carolina Reyes",
                          profesor_id=profesores["c.reyes@liceo.cl"].id)
        u_profe.set_password("profe123")
        db.session.add(u_profe)

        # profe_araya vinculado a programación
        u_prog = Usuario(rut="13.444.555-6", correo="rodrigo.araya@liceosofofa.cl",
                         rol="profe", nombre="Rodrigo Araya",
                         profesor_id=profesores["r.araya@liceo.cl"].id)
        u_prog.set_password("profe123")
        db.session.add(u_prog)

        # alumno 1 de 4G (test como alumno) -> correo @liceorbl.cl
        al = alumno_por_rut.get("20.123.456-1")
        if al:
            u_al = Usuario(rut="20.123.456-1", correo="joaquin.rivas@liceorbl.cl",
                           rol="alumno", nombre="Joaquín Rivas", alumno_id=al.id)
            u_al.set_password("alumno123")
            db.session.add(u_al)

        # un inspector de ejemplo
        u_ins = Usuario(rut="18.777.888-9", correo="inspe.diaz@liceorbl.cl",
                        rol="inspe", nombre="Claudia Díaz")
        u_ins.set_password("inspe123")
        db.session.add(u_ins)

        db.session.commit()
        print("Seed de ejemplo listo: asignaturas, profesores, alumnos, evaluaciones y usuarios.")

        print("\nCuentas de ejemplo (login con correo):")
        print("  UTP        : utp@liceorbl.cl / utp123")
        print("  Profesor   : carolina.reyes@liceosofofa.cl / profe123  (Matemática)")
        print("  Prof. Prog : rodrigo.araya@liceosofofa.cl / profe123   (Programación 3G/4G)")
        print("  Inspector  : inspe.diaz@liceorbl.cl / inspe123")
        print("  Alumno 4G  : joaquin.rivas@liceorbl.cl / alumno123")


if __name__ == "__main__":
    main()
