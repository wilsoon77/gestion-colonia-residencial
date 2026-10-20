from datetime import date, datetime, timezone
from app import db


class Deuda(db.Model):
    __tablename__ = 'deuda'

    id_deuda = db.Column(db.Integer, primary_key=True)
    id_vecino = db.Column(db.Integer, db.ForeignKey('vecino.id_vecino'), nullable=False)
    concepto = db.Column(db.String(150), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.Date, default=date.today, nullable=False)
    estado = db.Column(db.String(20), default='Pendiente', nullable=False)  # Pendiente, Pagada, Anulada

    comprobantes = db.relationship(
        'ComprobanteDeuda',
        back_populates='deuda',
        cascade='all, delete-orphan',
        order_by='ComprobanteDeuda.id_comprobante.desc()',
        lazy=True
    )

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

    evidencias = db.relationship(
        'EvidenciaMulta',
        back_populates='multa',
        cascade='all, delete-orphan',
        order_by='EvidenciaMulta.id_evidencia.desc()',
        lazy=True
    )

    def __repr__(self):
        return f'<Multa {self.motivo} - Q{self.monto} ({self.estado})>'


class EvidenciaMulta(db.Model):
    __tablename__ = 'evidencia_multa'

    id_evidencia = db.Column(db.Integer, primary_key=True)
    id_multa = db.Column(db.Integer, db.ForeignKey('multa.id_multa', ondelete='CASCADE'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=True)
    nombre_archivo = db.Column(db.String(255), nullable=True)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    multa = db.relationship('Multa', back_populates='evidencias')

    def __repr__(self):
        return f'<EvidenciaMulta #{self.id_evidencia} (Multa #{self.id_multa})>'


class ComprobanteDeuda(db.Model):
    __tablename__ = 'comprobante_deuda'

    id_comprobante = db.Column(db.Integer, primary_key=True)
    id_deuda = db.Column(db.Integer, db.ForeignKey('deuda.id_deuda', ondelete='CASCADE'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255), nullable=True)
    nombre_archivo = db.Column(db.String(255), nullable=True)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    deuda = db.relationship('Deuda', back_populates='comprobantes')

    def __repr__(self):
        return f'<ComprobanteDeuda #{self.id_comprobante} (Deuda #{self.id_deuda})>'
