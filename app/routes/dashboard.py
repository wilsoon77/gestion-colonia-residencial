from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.residencia import Casa, Vecino, Familia
from app.models.finanzas import Deuda, Multa

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Métricas generales para el dashboard
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
