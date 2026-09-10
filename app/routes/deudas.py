from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.finanzas import Deuda
from app.models.residencia import Vecino
from app.utils.decorators import role_required

deudas_bp = Blueprint('deudas', __name__)


@deudas_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def index():
    estado_filtro = request.args.get('estado', '').strip()
    vecino_filtro = request.args.get('vecino_id', '').strip()
    busqueda = request.args.get('q', '').strip()

    query = Deuda.query.join(Vecino)

    # Restricción de seguridad: Si es Usuario de Consulta, limitar estrictamente a sus propias deudas
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino:
            flash('No tienes una ficha de residente vinculada.', 'warning')
            return redirect(url_for('dashboard.index'))

        query = query.filter(Deuda.id_vecino == current_user.vecino.id_vecino)
        vecinos = [current_user.vecino]
        vecino_filtro = str(current_user.vecino.id_vecino)
    else:
        vecinos = Vecino.query.order_by(Vecino.apellidos.asc(), Vecino.nombres.asc()).all()
        if vecino_filtro and vecino_filtro.isdigit():
            query = query.filter(Deuda.id_vecino == int(vecino_filtro))

    if estado_filtro:
        query = query.filter(Deuda.estado == estado_filtro)

    if busqueda:
        query = query.filter(
            (Deuda.concepto.ilike(f'%{busqueda}%')) |
            (Vecino.nombres.ilike(f'%{busqueda}%')) |
            (Vecino.apellidos.ilike(f'%{busqueda}%'))
        )

    deudas = query.order_by(Deuda.fecha.desc(), Deuda.id_deuda.desc()).all()

    # Cálculo de métricas financieras respetando el rol
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        v_id = current_user.vecino.id_vecino
        total_deudas = Deuda.query.filter_by(id_vecino=v_id).count()
        monto_pendiente = db.session.query(
            db.func.sum(Deuda.monto)
        ).filter_by(id_vecino=v_id, estado='Pendiente').scalar() or Decimal('0.00')
        monto_pagado = db.session.query(
            db.func.sum(Deuda.monto)
        ).filter_by(id_vecino=v_id, estado='Pagada').scalar() or Decimal('0.00')
        cantidad_pendientes = Deuda.query.filter_by(id_vecino=v_id, estado='Pendiente').count()
    else:
        total_deudas = Deuda.query.count()
        monto_pendiente = db.session.query(
            db.func.sum(Deuda.monto)
        ).filter_by(estado='Pendiente').scalar() or Decimal('0.00')
        monto_pagado = db.session.query(
            db.func.sum(Deuda.monto)
        ).filter_by(estado='Pagada').scalar() or Decimal('0.00')
        cantidad_pendientes = Deuda.query.filter_by(estado='Pendiente').count()

    return render_template(
        'deudas/index.html',
        deudas=deudas,
        vecinos=vecinos,
        estado_filtro=estado_filtro,
        vecino_filtro=vecino_filtro,
        busqueda=busqueda,
        total_deudas=total_deudas,
        monto_pendiente=monto_pendiente,
        monto_pagado=monto_pagado,
        cantidad_pendientes=cantidad_pendientes
    )


@deudas_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    id_vecino = request.form.get('id_vecino')
    concepto = request.form.get('concepto', '').strip()
    monto_str = request.form.get('monto', '').strip()
    fecha_str = request.form.get('fecha', '').strip()
    estado = request.form.get('estado', 'Pendiente').strip()
    next_url = request.form.get('next_url')

    if not id_vecino or not concepto or not monto_str:
        flash('El residente, concepto y monto son campos obligatorios.', 'danger')
        return redirect(next_url or url_for('deudas.index'))

    try:
        monto = Decimal(monto_str)
        if monto <= 0:
            flash('El monto de la deuda debe ser un valor positivo.', 'danger')
            return redirect(next_url or url_for('deudas.index'))
    except Exception:
        flash('El monto ingresado no tiene un formato válido.', 'danger')
        return redirect(next_url or url_for('deudas.index'))

    fecha_emision = date.today()
    if fecha_str:
        try:
            fecha_emision = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    nueva_deuda = Deuda(
        id_vecino=int(id_vecino),
        concepto=concepto,
        monto=monto,
        fecha=fecha_emision,
        estado=estado
    )

    db.session.add(nueva_deuda)
    db.session.commit()

    vecino = db.session.get(Vecino, int(id_vecino))
    flash(f'Deuda de Q{monto:.2f} registrada exitosamente a {vecino.nombre_completo}.', 'success')
    return redirect(next_url or url_for('deudas.index'))


@deudas_bp.route('/<int:id_deuda>')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def detalle(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)

    # Restricción: Residente solo puede ver sus propias deudas
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino or deuda.id_vecino != current_user.vecino.id_vecino:
            abort(403)

    vecinos = Vecino.query.order_by(Vecino.apellidos.asc(), Vecino.nombres.asc()).all()
    return render_template('deudas/detalle.html', deuda=deuda, vecinos=vecinos)


@deudas_bp.route('/<int:id_deuda>/editar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def editar(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)

    id_vecino = request.form.get('id_vecino')
    concepto = request.form.get('concepto', '').strip()
    monto_str = request.form.get('monto', '').strip()
    fecha_str = request.form.get('fecha', '').strip()
    estado = request.form.get('estado')

    if not id_vecino or not concepto or not monto_str:
        flash('Todos los campos obligatorios deben ser completados.', 'danger')
        return redirect(url_for('deudas.detalle', id_deuda=id_deuda))

    try:
        monto = Decimal(monto_str)
        if monto <= 0:
            flash('El monto de la deuda debe ser un valor positivo.', 'danger')
            return redirect(url_for('deudas.detalle', id_deuda=id_deuda))
    except Exception:
        flash('El formato del monto es inválido.', 'danger')
        return redirect(url_for('deudas.detalle', id_deuda=id_deuda))

    if fecha_str:
        try:
            deuda.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    deuda.id_vecino = int(id_vecino)
    deuda.concepto = concepto
    deuda.monto = monto
    if estado:
        deuda.estado = estado

    db.session.commit()
    flash(f'Deuda #{deuda.id_deuda} actualizada exitosamente.', 'success')
    return redirect(url_for('deudas.detalle', id_deuda=id_deuda))


@deudas_bp.route('/<int:id_deuda>/cambiar-estado', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def cambiar_estado(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)
    nuevo_estado = request.form.get('nuevo_estado', '').strip()
    next_url = request.form.get('next_url')

    if nuevo_estado in ['Pendiente', 'Pagada', 'Anulada']:
        deuda.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado de la deuda #{deuda.id_deuda} cambiado a {nuevo_estado}.', 'info')
    else:
        flash('Estado no válido.', 'danger')

    return redirect(next_url or url_for('deudas.index'))


@deudas_bp.route('/<int:id_deuda>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)
    num_deuda = deuda.id_deuda

    db.session.delete(deuda)
    db.session.commit()

    flash(f'Registro de deuda #{num_deuda} eliminado.', 'info')
    return redirect(url_for('deudas.index'))
