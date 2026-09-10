from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Rol(db.Model):
    __tablename__ = 'rol'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __repr__(self):
        return f'<Rol {self.nombre}>'


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    id_vecino = db.Column(db.Integer, db.ForeignKey('vecino.id_vecino'), nullable=True)
    estado = db.Column(db.String(20), default='Activo', nullable=False)

    # Relación bidireccional con Vecino
    vecino = db.relationship(
        'Vecino',
        foreign_keys=[id_vecino],
        backref=db.backref('usuario_cuenta', uselist=False),
        lazy=True
    )

    def get_id(self):
        return str(self.id_usuario)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.usuario}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))
