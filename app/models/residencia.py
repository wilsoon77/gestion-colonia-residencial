from app import db


class Casa(db.Model):
    __tablename__ = 'casa'

    id_casa = db.Column(db.Integer, primary_key=True)
    numero_casa = db.Column(db.String(20), nullable=False)
    manzana = db.Column(db.String(20), nullable=True)
    calle_avenida = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(30), default='Ocupada', nullable=False)  # Ocupada, Desocupada, En Construcción

    vecinos = db.relationship('Vecino', backref='casa', lazy=True)

    def __repr__(self):
        return f'<Casa {self.numero_casa} - Mz {self.manzana}>'


class Familia(db.Model):
    __tablename__ = 'familia'

    id_familia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Ej. "Familia Pérez López"

    integrantes = db.relationship('Vecino', backref='familia', lazy=True)

    def __repr__(self):
        return f'<Familia {self.nombre}>'


class Vecino(db.Model):
    __tablename__ = 'vecino'

    id_vecino = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(120), nullable=True)
    id_casa = db.Column(db.Integer, db.ForeignKey('casa.id_casa'), nullable=True)
    id_familia = db.Column(db.Integer, db.ForeignKey('familia.id_familia'), nullable=True)

    # Relaciones de deudas y multas
    deudas = db.relationship('Deuda', backref='vecino', lazy=True, cascade="all, delete-orphan")
    multas = db.relationship('Multa', backref='vecino', lazy=True, cascade="all, delete-orphan")

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    def __repr__(self):
        return f'<Vecino {self.nombre_completo}>'


class Parentesco(db.Model):
    __tablename__ = 'parentesco'

    id_parentesco = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # Padre, Madre, Hijo, Hija, Encargado, Cónyuge

    def __repr__(self):
        return f'<Parentesco {self.nombre}>'


class VecinoParentesco(db.Model):
    """Modelo relacional para almacenar las relaciones de parentesco entre vecinos."""
    __tablename__ = 'vecino_parentesco'

    id_vecino = db.Column(
        db.Integer,
        db.ForeignKey('vecino.id_vecino', ondelete='CASCADE'),
        primary_key=True
    )
    id_relacionado = db.Column(
        db.Integer,
        db.ForeignKey('vecino.id_vecino', ondelete='CASCADE'),
        primary_key=True
    )
    id_parentesco = db.Column(
        db.Integer,
        db.ForeignKey('parentesco.id_parentesco', ondelete='CASCADE'),
        primary_key=True
    )

    # Relaciones ORM
    vecino_origen = db.relationship(
        'Vecino',
        foreign_keys=[id_vecino],
        backref=db.backref('relaciones_origen', cascade='all, delete-orphan', lazy=True)
    )
    vecino_relacionado = db.relationship(
        'Vecino',
        foreign_keys=[id_relacionado],
        backref=db.backref('relaciones_destino', cascade='all, delete-orphan', lazy=True)
    )
    parentesco = db.relationship(
        'Parentesco',
        backref=db.backref('relaciones_asignadas', lazy=True)
    )

    def __repr__(self):
        return f'<VecinoParentesco {self.id_vecino} es {self.id_parentesco} de {self.id_relacionado}>'


# Alias para compatibilidad de importaciones
vecino_parentesco = VecinoParentesco
