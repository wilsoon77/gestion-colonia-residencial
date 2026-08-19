from app import db

# Tabla intermedia de relación muchos a muchos con metadata de parentesco
vecino_parentesco = db.Table(
    'vecino_parentescos',
    db.Column('id_vecino', db.Integer, db.ForeignKey('vecinos.id_vecino'), primary_key=True),
    db.Column('id_relacionado', db.Integer, db.ForeignKey('vecinos.id_vecino'), primary_key=True),
    db.Column('id_parentesco', db.Integer, db.ForeignKey('parentescos.id_parentesco'), primary_key=True)
)

class Casa(db.Model):
    __tablename__ = 'casas'

    id_casa = db.Column(db.Integer, primary_key=True)
    numero_casa = db.Column(db.String(20), nullable=False)
    manzana = db.Column(db.String(20), nullable=True)
    calle_avenida = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(30), default='Ocupada', nullable=False)  # Ocupada, Desocupada, En Construcción

    vecinos = db.relationship('Vecino', backref='casa', lazy=True)

    def __repr__(self):
        return f'<Casa {self.numero_casa} - Mz {self.manzana}>'

class Familia(db.Model):
    __tablename__ = 'familias'

    id_familia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej. "Familia Pérez López"

    integrantes = db.relationship('Vecino', backref='familia', lazy=True)

    def __repr__(self):
        return f'<Familia {self.nombre}>'

class Vecino(db.Model):
    __tablename__ = 'vecinos'

    id_vecino = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(120), nullable=True)
    id_casa = db.Column(db.Integer, db.ForeignKey('casas.id_casa'), nullable=True)
    id_familia = db.Column(db.Integer, db.ForeignKey('familias.id_familia'), nullable=True)

    # Relaciones de deudas, multas y cuenta de usuario
    deudas = db.relationship('Deuda', backref='vecino', lazy=True, cascade="all, delete-orphan")
    multas = db.relationship('Multa', backref='vecino', lazy=True, cascade="all, delete-orphan")
    usuario_cuenta = db.relationship('Usuario', backref='vecino_asociado', uselist=False)

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __repr__(self):
        return f'<Vecino {self.nombre_completo}>'

class Parentesco(db.Model):
    __tablename__ = 'parentescos'

    id_parentesco = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # Padre, Madre, Hijo, Hija, Encargado, Cónyuge

    def __repr__(self):
        return f'<Parentesco {self.nombre}>'
