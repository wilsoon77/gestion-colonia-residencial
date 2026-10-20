from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.finanzas import Deuda, ComprobanteDeuda
from app.models.residencia import Vecino
from app.services.cloudinary_service import allowed_image_file, subir_imagen, eliminar_imagen
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

    # Procesar comprobantes de pago bancarios si se adjuntaron
    archivos = request.files.getlist('comprobantes')
    comprobantes_subidos = 0
    errores_archivos = 0

    for archivo in archivos:
        if archivo and archivo.filename:
            if not allowed_image_file(archivo.filename):
                errores_archivos += 1
                continue
            resultado_upload = subir_imagen(archivo, folder='residencial/deudas_comprobantes')
            if resultado_upload:
                comprobante = ComprobanteDeuda(
                    id_deuda=nueva_deuda.id_deuda,
                    url=resultado_upload['url'],
                    public_id=resultado_upload['public_id'],
                    nombre_archivo=resultado_upload['nombre_archivo']
                )
                db.session.add(comprobante)
                comprobantes_subidos += 1
            else:
                errores_archivos += 1

    if comprobantes_subidos > 0:
        db.session.commit()

    vecino = db.session.get(Vecino, int(id_vecino))
    msg_comp = f" con {comprobantes_subidos} comprobante(s) adjunto(s)" if comprobantes_subidos > 0 else ""
    flash(f'Deuda de Q{monto:.2f} registrada exitosamente a {vecino.nombre_completo}{msg_comp}.', 'success')
    if errores_archivos > 0:
        flash(f'{errores_archivos} archivo(s) no pudieron adjuntarse (formato no permitido o error de carga).', 'warning')
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


@deudas_bp.route('/<int:id_deuda>/comprobantes/subir', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def subir_comprobantes(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)

    # Restricción: Residente solo puede subir a sus propias deudas
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino or deuda.id_vecino != current_user.vecino.id_vecino:
            abort(403)

    archivos = request.files.getlist('comprobantes')
    if not archivos or all(not a.filename for a in archivos):
        flash('Por favor selecciona al menos una imagen de comprobante para adjuntar.', 'warning')
        return redirect(url_for('deudas.detalle', id_deuda=id_deuda))

    comprobantes_subidos = 0
    errores_archivos = 0

    for archivo in archivos:
        if archivo and archivo.filename:
            if not allowed_image_file(archivo.filename):
                errores_archivos += 1
                continue
            resultado_upload = subir_imagen(archivo, folder='residencial/deudas_comprobantes')
            if resultado_upload:
                comprobante = ComprobanteDeuda(
                    id_deuda=deuda.id_deuda,
                    url=resultado_upload['url'],
                    public_id=resultado_upload['public_id'],
                    nombre_archivo=resultado_upload['nombre_archivo']
                )
                db.session.add(comprobante)
                comprobantes_subidos += 1
            else:
                errores_archivos += 1

    if comprobantes_subidos > 0:
        db.session.commit()
        flash(f'Se adjuntaron exitosamente {comprobantes_subidos} comprobante(s) de pago.', 'success')

    if errores_archivos > 0:
        flash(f'{errores_archivos} archivo(s) no pudieron procesarse o tienen un formato no soportado.', 'warning')

    return redirect(url_for('deudas.detalle', id_deuda=id_deuda))


@deudas_bp.route('/<int:id_deuda>/comprobantes/<int:id_comprobante>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar_comprobante(id_deuda, id_comprobante):
    deuda = db.get_or_404(Deuda, id_deuda)
    comprobante = db.get_or_404(ComprobanteDeuda, id_comprobante)

    if comprobante.id_deuda != deuda.id_deuda:
        abort(400)

    if comprobante.public_id:
        eliminar_imagen(comprobante.public_id)

    db.session.delete(comprobante)
    db.session.commit()

    flash('Comprobante de pago eliminado exitosamente.', 'info')
    return redirect(url_for('deudas.detalle', id_deuda=id_deuda))


@deudas_bp.route('/<int:id_deuda>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_deuda):
    deuda = db.get_or_404(Deuda, id_deuda)
    num_deuda = deuda.id_deuda

    # Limpiar comprobantes de Cloudinary asociados a esta deuda
    for comp in deuda.comprobantes:
        if comp.public_id:
            eliminar_imagen(comp.public_id)

    db.session.delete(deuda)
    db.session.commit()

    flash(f'Registro de deuda #{num_deuda} eliminado.', 'info')
    return redirect(url_for('deudas.index'))
