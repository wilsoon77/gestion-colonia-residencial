from decimal import Decimal
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models.residencia import Casa, Vecino, Familia
from app.models.finanzas import Deuda, Multa

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    # Si es Usuario de Consulta (Residente), mostrar su panel personalizado
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        vecino = current_user.vecino
        if not vecino:
            return render_template(
                'dashboard/residente_sin_perfil.html'
            )

        # Métricas individuales del residente
        mis_deudas_pendientes = Deuda.query.filter_by(
            id_vecino=vecino.id_vecino,
            estado='Pendiente'
        ).count()
        mis_multas_pendientes = Multa.query.filter_by(
            id_vecino=vecino.id_vecino,
            estado='Pendiente'
        ).count()

        monto_deudas_pendiente = db.session.query(
            db.func.sum(Deuda.monto)
        ).filter_by(
            id_vecino=vecino.id_vecino,
            estado='Pendiente'
        ).scalar() or Decimal('0.00')

        monto_multas_pendiente = db.session.query(
            db.func.sum(Multa.monto)
        ).filter_by(
            id_vecino=vecino.id_vecino,
            estado='Pendiente'
        ).scalar() or Decimal('0.00')

        ultimas_deudas = Deuda.query.filter_by(
            id_vecino=vecino.id_vecino
        ).order_by(Deuda.fecha.desc()).limit(5).all()

        ultimas_multas = Multa.query.filter_by(
            id_vecino=vecino.id_vecino
        ).order_by(Multa.fecha.desc()).limit(5).all()

        return render_template(
            'dashboard/residente.html',
            vecino=vecino,
            mis_deudas_pendientes=mis_deudas_pendientes,
            mis_multas_pendientes=mis_multas_pendientes,
            monto_deudas_pendiente=monto_deudas_pendiente,
            monto_multas_pendiente=monto_multas_pendiente,
            ultimas_deudas=ultimas_deudas,
            ultimas_multas=ultimas_multas
        )

    # Vista general para Administradores
    total_casas = Casa.query.count()
    total_vecinos = Vecino.query.count()
    total_familias = Familia.query.count()
    deudas_pendientes = Deuda.query.filter_by(estado='Pendiente').count()
    multas_pendientes = Multa.query.filter_by(estado='Pendiente').count()

    return render_template(
        'dashboard/index.html',
        total_casas=total_casas,
        total_vecinos=total_vecinos,
        total_familias=total_familias,
        deudas_pendientes=deudas_pendientes,
        multas_pendientes=multas_pendientes
    )
