from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.finanzas import Multa
from app.models.residencia import Vecino
from app.utils.decorators import role_required

multas_bp = Blueprint('multas', __name__)


@multas_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def index():
    estado_filtro = request.args.get('estado', '').strip()
    vecino_filtro = request.args.get('vecino_id', '').strip()
    busqueda = request.args.get('q', '').strip()

    query = Multa.query.join(Vecino)

    # Restricción de seguridad: Si es Usuario de Consulta, limitar estrictamente a sus propias multas
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino:
            flash('No tienes una ficha de residente vinculada.', 'warning')
            return redirect(url_for('dashboard.index'))

        query = query.filter(Multa.id_vecino == current_user.vecino.id_vecino)
        vecinos = [current_user.vecino]
        vecino_filtro = str(current_user.vecino.id_vecino)
    else:
        vecinos = Vecino.query.order_by(Vecino.apellidos.asc(), Vecino.nombres.asc()).all()
        if vecino_filtro and vecino_filtro.isdigit():
            query = query.filter(Multa.id_vecino == int(vecino_filtro))

    if estado_filtro:
        query = query.filter(Multa.estado == estado_filtro)

    if busqueda:
        query = query.filter(
            (Multa.motivo.ilike(f'%{busqueda}%')) |
            (Vecino.nombres.ilike(f'%{busqueda}%')) |
            (Vecino.apellidos.ilike(f'%{busqueda}%'))
        )

    multas = query.order_by(Multa.fecha.desc(), Multa.id_multa.desc()).all()

    # Cálculo de métricas financieras respetando el rol
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        v_id = current_user.vecino.id_vecino
        total_multas = Multa.query.filter_by(id_vecino=v_id).count()
        monto_pendiente = db.session.query(
            db.func.sum(Multa.monto)
        ).filter_by(id_vecino=v_id, estado='Pendiente').scalar() or Decimal('0.00')
        monto_pagado = db.session.query(
            db.func.sum(Multa.monto)
        ).filter_by(id_vecino=v_id, estado='Pagada').scalar() or Decimal('0.00')
        cantidad_pendientes = Multa.query.filter_by(id_vecino=v_id, estado='Pendiente').count()
    else:
        total_multas = Multa.query.count()
        monto_pendiente = db.session.query(
            db.func.sum(Multa.monto)
        ).filter_by(estado='Pendiente').scalar() or Decimal('0.00')
        monto_pagado = db.session.query(
            db.func.sum(Multa.monto)
        ).filter_by(estado='Pagada').scalar() or Decimal('0.00')
        cantidad_pendientes = Multa.query.filter_by(estado='Pendiente').count()

    return render_template(
        'multas/index.html',
        multas=multas,
        vecinos=vecinos,
        estado_filtro=estado_filtro,
        vecino_filtro=vecino_filtro,
        busqueda=busqueda,
        total_multas=total_multas,
        monto_pendiente=monto_pendiente,
        monto_pagado=monto_pagado,
        cantidad_pendientes=cantidad_pendientes
    )


@multas_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    id_vecino = request.form.get('id_vecino')
    motivo = request.form.get('motivo', '').strip()
    monto_str = request.form.get('monto', '').strip()
    fecha_str = request.form.get('fecha', '').strip()
    estado = request.form.get('estado', 'Pendiente').strip()
    next_url = request.form.get('next_url')

    if not id_vecino or not motivo or not monto_str:
        flash('El infractor, motivo y monto son campos obligatorios.', 'danger')
        return redirect(next_url or url_for('multas.index'))

    try:
        monto = Decimal(monto_str)
        if monto <= 0:
            flash('El monto de la multa debe ser un valor positivo.', 'danger')
            return redirect(next_url or url_for('multas.index'))
    except Exception:
        flash('El monto ingresado no tiene un formato válido.', 'danger')
        return redirect(next_url or url_for('multas.index'))

    fecha_emision = date.today()
    if fecha_str:
        try:
            fecha_emision = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    nueva_multa = Multa(
        id_vecino=int(id_vecino),
        motivo=motivo,
        monto=monto,
        fecha=fecha_emision,
        estado=estado
    )

    db.session.add(nueva_multa)
    db.session.commit()

    vecino = db.session.get(Vecino, int(id_vecino))
    flash(f'Multa de Q{monto:.2f} aplicada exitosamente a {vecino.nombre_completo}.', 'success')
    return redirect(next_url or url_for('multas.index'))


@multas_bp.route('/<int:id_multa>')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def detalle(id_multa):
    multa = db.get_or_404(Multa, id_multa)

    # Restricción: Residente solo puede ver sus propias multas
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino or multa.id_vecino != current_user.vecino.id_vecino:
            abort(403)

    vecinos = Vecino.query.order_by(Vecino.apellidos.asc(), Vecino.nombres.asc()).all()
    return render_template('multas/detalle.html', multa=multa, vecinos=vecinos)


@multas_bp.route('/<int:id_multa>/editar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def editar(id_multa):
    multa = db.get_or_404(Multa, id_multa)

    id_vecino = request.form.get('id_vecino')
    motivo = request.form.get('motivo', '').strip()
    monto_str = request.form.get('monto', '').strip()
    fecha_str = request.form.get('fecha', '').strip()
    estado = request.form.get('estado')

    if not id_vecino or not motivo or not monto_str:
        flash('Todos los campos obligatorios deben ser completados.', 'danger')
        return redirect(url_for('multas.detalle', id_multa=id_multa))

    try:
        monto = Decimal(monto_str)
        if monto <= 0:
            flash('El monto de la multa debe ser un valor positivo.', 'danger')
            return redirect(url_for('multas.detalle', id_multa=id_multa))
    except Exception:
        flash('El formato del monto es inválido.', 'danger')
        return redirect(url_for('multas.detalle', id_multa=id_multa))

    if fecha_str:
        try:
            multa.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    multa.id_vecino = int(id_vecino)
    multa.motivo = motivo
    multa.monto = monto
    if estado:
        multa.estado = estado

    db.session.commit()
    flash(f'Multa #{multa.id_multa} actualizada exitosamente.', 'success')
    return redirect(url_for('multas.detalle', id_multa=id_multa))


@multas_bp.route('/<int:id_multa>/cambiar-estado', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def cambiar_estado(id_multa):
    multa = db.get_or_404(Multa, id_multa)
    nuevo_estado = request.form.get('nuevo_estado', '').strip()
    next_url = request.form.get('next_url')

    if nuevo_estado in ['Pendiente', 'Pagada', 'Exonerada']:
        multa.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado de la multa #{multa.id_multa} cambiado a {nuevo_estado}.', 'info')
    else:
        flash('Estado no válido.', 'danger')

    return redirect(next_url or url_for('multas.index'))


@multas_bp.route('/<int:id_multa>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_multa):
    multa = db.get_or_404(Multa, id_multa)
    num_multa = multa.id_multa

    db.session.delete(multa)
    db.session.commit()

    flash(f'Registro de multa #{num_multa} eliminado.', 'info')
    return redirect(url_for('multas.index'))
