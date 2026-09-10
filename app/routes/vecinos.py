from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.residencia import Vecino, Casa, Familia, Parentesco
from app.utils.decorators import role_required

vecinos_bp = Blueprint('vecinos', __name__)


@vecinos_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def index():
    # Si es Usuario de Consulta, redirigir a su propio perfil de residente
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if current_user.vecino:
            return redirect(url_for('vecinos.detalle', id_vecino=current_user.vecino.id_vecino))
        flash('No tienes una ficha de residente vinculada actualmente.', 'info')
        return redirect(url_for('dashboard.index'))

    busqueda = request.args.get('q', '').strip()
    casa_filtro = request.args.get('casa_id', '').strip()
    familia_filtro = request.args.get('familia_id', '').strip()

    query = Vecino.query

    if casa_filtro and casa_filtro.isdigit():
        query = query.filter_by(id_casa=int(casa_filtro))

    if familia_filtro and familia_filtro.isdigit():
        query = query.filter_by(id_familia=int(familia_filtro))

    if busqueda:
        query = query.filter(
            (Vecino.nombres.ilike(f'%{busqueda}%')) |
            (Vecino.apellidos.ilike(f'%{busqueda}%')) |
            (Vecino.telefono.ilike(f'%{busqueda}%')) |
            (Vecino.correo.ilike(f'%{busqueda}%'))
        )

    vecinos = query.order_by(Vecino.apellidos.asc(), Vecino.nombres.asc()).all()
    casas = Casa.query.order_by(Casa.numero_casa.asc()).all()
    familias = Familia.query.order_by(Familia.nombre.asc()).all()

    total = Vecino.query.count()

    return render_template(
        'vecinos/index.html',
        vecinos=vecinos,
        casas=casas,
        familias=familias,
        busqueda=busqueda,
        casa_filtro=casa_filtro,
        familia_filtro=familia_filtro,
        total=total
    )


@vecinos_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    nombres = request.form.get('nombres', '').strip()
    apellidos = request.form.get('apellidos', '').strip()
    telefono = request.form.get('telefono', '').strip()
    correo = request.form.get('correo', '').strip()
    id_casa = request.form.get('id_casa')
    id_familia = request.form.get('id_familia')

    if not nombres or not apellidos:
        flash('Los nombres y apellidos son obligatorios.', 'danger')
        return redirect(url_for('vecinos.index'))

    nuevo_vecino = Vecino(
        nombres=nombres,
        apellidos=apellidos,
        telefono=telefono if telefono else None,
        correo=correo if correo else None,
        id_casa=int(id_casa) if id_casa and id_casa.isdigit() else None,
        id_familia=int(id_familia) if id_familia and id_familia.isdigit() else None
    )

    db.session.add(nuevo_vecino)
    db.session.commit()

    flash(f'Vecino {nuevo_vecino.nombre_completo} registrado exitosamente.', 'success')
    return redirect(url_for('vecinos.index'))


@vecinos_bp.route('/<int:id_vecino>')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def detalle(id_vecino):
    vecino = db.get_or_404(Vecino, id_vecino)

    # Restricción: Usuario de consulta solo puede ver su propio perfil o el de su núcleo familiar
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino:
            abort(403)
        es_mismo = (current_user.vecino.id_vecino == id_vecino)
        es_familiar = bool(
            current_user.vecino.id_familia and
            vecino.id_familia == current_user.vecino.id_familia
        )
        if not es_mismo and not es_familiar:
            abort(403)

    casas = Casa.query.order_by(Casa.numero_casa.asc()).all()
    familias = Familia.query.order_by(Familia.nombre.asc()).all()
    parentescos = Parentesco.query.order_by(Parentesco.nombre.asc()).all()
    otros_vecinos = Vecino.query.filter(Vecino.id_vecino != id_vecino).order_by(Vecino.nombres.asc()).all()

    return render_template(
        'vecinos/detalle.html',
        vecino=vecino,
        casas=casas,
        familias=familias,
        parentescos=parentescos,
        otros_vecinos=otros_vecinos
    )


@vecinos_bp.route('/<int:id_vecino>/editar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def editar(id_vecino):
    vecino = db.get_or_404(Vecino, id_vecino)

    nombres = request.form.get('nombres', '').strip()
    apellidos = request.form.get('apellidos', '').strip()
    telefono = request.form.get('telefono', '').strip()
    correo = request.form.get('correo', '').strip()
    id_casa = request.form.get('id_casa')
    id_familia = request.form.get('id_familia')

    if not nombres or not apellidos:
        flash('Los nombres y apellidos son obligatorios.', 'danger')
        return redirect(url_for('vecinos.detalle', id_vecino=id_vecino))

    vecino.nombres = nombres
    vecino.apellidos = apellidos
    vecino.telefono = telefono if telefono else None
    vecino.correo = correo if correo else None
    vecino.id_casa = int(id_casa) if id_casa and id_casa.isdigit() else None
    vecino.id_familia = int(id_familia) if id_familia and id_familia.isdigit() else None

    db.session.commit()
    flash(f'Datos del vecino {vecino.nombre_completo} actualizados correctamente.', 'success')
    return redirect(url_for('vecinos.detalle', id_vecino=id_vecino))


@vecinos_bp.route('/<int:id_vecino>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_vecino):
    vecino = db.get_or_404(Vecino, id_vecino)
    nom = vecino.nombre_completo

    db.session.delete(vecino)
    db.session.commit()

    flash(f'Vecino {nom} eliminado del registro.', 'info')
    return redirect(url_for('vecinos.index'))
