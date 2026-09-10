from datetime import date
from app import db


class Deuda(db.Model):
    __tablename__ = 'deuda'

    id_deuda = db.Column(db.Integer, primary_key=True)
    id_vecino = db.Column(db.Integer, db.ForeignKey('vecino.id_vecino'), nullable=False)
    concepto = db.Column(db.String(150), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    estado = db.Column(db.String(20), default='Pendiente', nullable=False)  # Pendiente, Pagada, Anulada

    def __repr__(self):
        return f'<Deuda {self.concepto} - Q{self.monto} ({self.estado})>'


class Multa(db.Model):
    __tablename__ = 'multa'

    id_multa = db.Column(db.Integer, primary_key=True)
    id_vecino = db.Column(db.Integer, db.ForeignKey('vecino.id_vecino'), nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    estado = db.Column(db.String(20), default='Pendiente', nullable=False)  # Pendiente, Pagada, Exonerada

    def __repr__(self):
        return f'<Multa {self.motivo} - Q{self.monto} ({self.estado})>'
