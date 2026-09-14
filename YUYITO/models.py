from datetime import date
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Roles del sistema
ROLES = {
    "utp": "UTP",
    "profe": "Profesor",
    "inspe": "Inspectoría",
    "alumno": "Alumno",
}

# Exigencia de las recuperaciones según si la inasistencia fue justificada
# por Inspectoría (o UTP) o no. Si el alumno presenta justificativo, rinde
# con la misma exigencia que el resto del curso (60%). Si no justifica,
# la recuperación tiene mayor exigencia (70%).
EXIGENCIA_JUSTIFICADO = 60.00
EXIGENCIA_NO_JUSTIFICADO = 70.00


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    rut = db.Column(db.String(12), primary_key=True)
    correo = db.Column(db.String(120), nullable=False, unique=True)
    clave = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    rol = db.Column(
        db.Enum("utp", "profe", "inspe", "alumno", name="rol_usuario"),
        nullable=False,
    )
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesores.id"), nullable=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, clave):
        self.clave = generate_password_hash(clave)

    def check_password(self, clave):
        return check_password_hash(self.clave, clave)

    def get_id(self):
        return str(self.rut)

    @property
    def rol_label(self):
        return ROLES.get(self.rol, self.rol)

    @property
    def es_utp(self):
        return self.rol == "utp"

    @property
    def es_profe(self):
        return self.rol == "profe"

    @property
    def es_inspe(self):
        return self.rol == "inspe"

    @property
    def es_alumno(self):
        return self.rol == "alumno"

    @property
    def puede_gestionar_evaluaciones(self):
        return self.rol == "profe"

    @property
    def puede_gestionar_ausencias(self):
        return self.rol in ("profe", "inspe", "utp")

    @property
    def puede_justificar(self):
        return self.rol in ("inspe", "utp")

    @property
    def puede_admin(self):
        return self.rol == "utp"

    def __repr__(self):
        return f"<Usuario {self.correo} ({self.rol})>"


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    nivel = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    alumnos = db.relationship("Alumno", backref="curso", lazy="dynamic")
    evaluaciones = db.relationship("Evaluacion", backref="curso", lazy="dynamic")

    def __repr__(self):
        return f"<Curso {self.nombre}>"


class Asignatura(db.Model):
    __tablename__ = "asignaturas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    color = db.Column(db.String(7), default="#3498db")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    evaluaciones = db.relationship("Evaluacion", backref="asignatura", lazy="dynamic")

    def __repr__(self):
        return f"<Asignatura {self.nombre}>"


class Profesor(db.Model):
    __tablename__ = "profesores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    evaluaciones = db.relationship("Evaluacion", backref="profesor", lazy="dynamic")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __repr__(self):
        return f"<Profesor {self.nombre_completo}>"


class Alumno(db.Model):
    __tablename__ = "alumnos"

    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), nullable=False, unique=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    asistencias = db.relationship("Asistencia", backref="alumno", lazy="dynamic")
    recuperaciones = db.relationship("Recuperacion", backref="alumno", lazy="dynamic")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __repr__(self):
        return f"<Alumno {self.nombre_completo}>"


class Evaluacion(db.Model):
    __tablename__ = "evaluaciones"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=True)
    descripcion = db.Column(db.Text)
    asignatura_id = db.Column(
        db.Integer, db.ForeignKey("asignaturas.id"), nullable=False
    )
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesores.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    asistencias = db.relationship("Asistencia", backref="evaluacion", lazy="dynamic")

    @staticmethod
    def contar_en_fecha(curso_id, fecha, exclude_id=None):
        q = Evaluacion.query.filter_by(curso_id=curso_id, fecha=fecha)
        if exclude_id:
            q = q.filter(Evaluacion.id != exclude_id)
        return q.count()

    @staticmethod
    def hay_lugar(curso_id, fecha, exclude_id=None):
        return Evaluacion.contar_en_fecha(curso_id, fecha, exclude_id) < 2

    def __repr__(self):
        return f"<Evaluacion {self.titulo} - {self.fecha}>"


class Asistencia(db.Model):
    __tablename__ = "asistencias"

    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(
        db.Integer, db.ForeignKey("evaluaciones.id"), nullable=False
    )
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    presente = db.Column(db.Boolean, nullable=False, default=True)
    motivo = db.Column(db.String(200))
    # Solo Inspectoría (o UTP) puede marcar una ausencia como justificada.
    # Define la exigencia con la que el alumno rendirá su recuperación.
    justificado = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("evaluacion_id", "alumno_id", name="uk_eval_alumno"),
    )


class Recuperacion(db.Model):
    __tablename__ = "recuperaciones"

    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(
        db.Integer, db.ForeignKey("evaluaciones.id"), nullable=False
    )
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    fecha_recuperacion = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(200))
    # Exigencia con la que rinde la recuperación: 60% si la ausencia fue
    # justificada por Inspectoría/UTP, 70% si no se justificó.
    porcentaje_exigencia = db.Column(db.Numeric(5, 2), nullable=False, default=EXIGENCIA_NO_JUSTIFICADO)
    estado = db.Column(
        db.Enum("pendiente", "completada", "cancelada", name="estado_recuperacion"),
        nullable=False,
        default="pendiente",
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    evaluacion = db.relationship("Evaluacion", backref="recuperaciones")
