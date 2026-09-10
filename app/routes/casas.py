from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.residencia import Casa
from app.utils.decorators import role_required

casas_bp = Blueprint('casas', __name__)


@casas_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def index():
    # Si es Usuario de Consulta, redirigir directamente a su vivienda
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if current_user.vecino and current_user.vecino.id_casa:
            return redirect(url_for('casas.detalle', id_casa=current_user.vecino.id_casa))
        flash('No tienes una vivienda asignada actualmente.', 'info')
        return redirect(url_for('dashboard.index'))

    estado_filtro = request.args.get('estado', '').strip()
    busqueda = request.args.get('q', '').strip()

    query = Casa.query

    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    if busqueda:
        query = query.filter(
            (Casa.numero_casa.ilike(f'%{busqueda}%')) |
            (Casa.manzana.ilike(f'%{busqueda}%')) |
            (Casa.calle_avenida.ilike(f'%{busqueda}%'))
        )

    casas = query.order_by(Casa.manzana.asc(), Casa.numero_casa.asc()).all()

    # Contadores para tarjetas
    total = Casa.query.count()
    ocupadas = Casa.query.filter_by(estado='Ocupada').count()
    desocupadas = Casa.query.filter_by(estado='Desocupada').count()
    construccion = Casa.query.filter_by(estado='En Construcción').count()

    return render_template(
        'casas/index.html',
        casas=casas,
        estado_filtro=estado_filtro,
        busqueda=busqueda,
        total=total,
        ocupadas=ocupadas,
        desocupadas=desocupadas,
        construccion=construccion
    )


@casas_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    numero_casa = request.form.get('numero_casa', '').strip()
    manzana = request.form.get('manzana', '').strip()
    calle_avenida = request.form.get('calle_avenida', '').strip()
    estado = request.form.get('estado', 'Ocupada').strip()

    if not numero_casa:
        flash('El número de casa es obligatorio.', 'danger')
        return redirect(url_for('casas.index'))

    nueva_casa = Casa(
        numero_casa=numero_casa,
        manzana=manzana if manzana else None,
        calle_avenida=calle_avenida if calle_avenida else None,
        estado=estado
    )

    db.session.add(nueva_casa)
    db.session.commit()

    flash(f'Casa #{numero_casa} registrada exitosamente.', 'success')
    return redirect(url_for('casas.index'))


@casas_bp.route('/<int:id_casa>')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def detalle(id_casa):
    casa = db.get_or_404(Casa, id_casa)

    # Restricción: Usuario de consulta solo puede ver su propia casa
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino or current_user.vecino.id_casa != id_casa:
            abort(403)

    return render_template('casas/detalle.html', casa=casa)


@casas_bp.route('/<int:id_casa>/editar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def editar(id_casa):
    casa = db.get_or_404(Casa, id_casa)

    numero_casa = request.form.get('numero_casa', '').strip()
    manzana = request.form.get('manzana', '').strip()
    calle_avenida = request.form.get('calle_avenida', '').strip()
    estado = request.form.get('estado', 'Ocupada').strip()

    if not numero_casa:
        flash('El número de casa es obligatorio.', 'danger')
        return redirect(url_for('casas.detalle', id_casa=id_casa))

    casa.numero_casa = numero_casa
    casa.manzana = manzana if manzana else None
    casa.calle_avenida = calle_avenida if calle_avenida else None
    casa.estado = estado

    db.session.commit()
    flash(f'Información de la Casa #{casa.numero_casa} actualizada correctamente.', 'success')
    return redirect(url_for('casas.detalle', id_casa=id_casa))


@casas_bp.route('/<int:id_casa>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_casa):
    casa = db.get_or_404(Casa, id_casa)

    # Desasociar vecinos que viven en la casa antes de borrarla
    for vecino in casa.vecinos:
        vecino.id_casa = None

    num = casa.numero_casa
    db.session.delete(casa)
    db.session.commit()

    flash(f'Casa #{num} eliminada del registro.', 'info')
    return redirect(url_for('casas.index'))
