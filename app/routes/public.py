from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.residencia import Casa, Vecino

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    # Métricas reales de la colonia para mostrar en la landing page
    total_casas = Casa.query.count()
    total_vecinos = Vecino.query.count()

    return render_template(
        'public/index.html',
        total_casas=total_casas,
        total_vecinos=total_vecinos
    )


@public_bp.route('/contacto', methods=['POST'])
def contacto():
    nombre = request.form.get('nombre', '').strip()
    telefono = request.form.get('telefono', '').strip()
    correo = request.form.get('correo', '').strip()
    motivo = request.form.get('motivo', 'Información General').strip()

    if not nombre or not (telefono or correo):
        flash('Por favor completa tu nombre y un método de contacto (teléfono o correo).', 'warning')
        return redirect(url_for('public.index') + '#contacto')

    # En una implementación real se enviaría una notificación por correo o a garita
    flash(
        f'¡Gracias {nombre}! Tu solicitud sobre "{motivo}" fue recibida. '
        'La administración de Las Encinas se comunicará contigo pronto.',
        'success'
    )
    return redirect(url_for('public.index') + '#contacto')
