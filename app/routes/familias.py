from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.residencia import Familia
from app.utils.decorators import role_required

familias_bp = Blueprint('familias', __name__)


@familias_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def index():
    # Si es Usuario de Consulta, redirigir directamente a su familia
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if current_user.vecino and current_user.vecino.id_familia:
            return redirect(url_for('familias.detalle', id_familia=current_user.vecino.id_familia))
        flash('No tienes un grupo familiar asignado actualmente.', 'info')
        return redirect(url_for('dashboard.index'))

    busqueda = request.args.get('q', '').strip()

    query = Familia.query

    if busqueda:
        query = query.filter(Familia.nombre.ilike(f'%{busqueda}%'))

    familias = query.order_by(Familia.nombre.asc()).all()
    total = Familia.query.count()

    return render_template('familias/index.html', familias=familias, busqueda=busqueda, total=total)


@familias_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        flash('El nombre de la familia es obligatorio.', 'danger')
        return redirect(url_for('familias.index'))

    nueva_familia = Familia(nombre=nombre)
    db.session.add(nueva_familia)
    db.session.commit()

    flash(f'{nombre} registrada exitosamente.', 'success')
    return redirect(url_for('familias.index'))


@familias_bp.route('/<int:id_familia>')
@login_required
@role_required('Administrador', 'Administrador de Colonia', 'Usuario de Consulta')
def detalle(id_familia):
    familia = db.get_or_404(Familia, id_familia)

    # Restricción: Usuario de consulta solo puede ver su propia familia
    if current_user.rol and current_user.rol.nombre == 'Usuario de Consulta':
        if not current_user.vecino or current_user.vecino.id_familia != id_familia:
            abort(403)

    return render_template('familias/detalle.html', familia=familia)


@familias_bp.route('/<int:id_familia>/editar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def editar(id_familia):
    familia = db.get_or_404(Familia, id_familia)
    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        flash('El nombre de la familia es obligatorio.', 'danger')
        return redirect(url_for('familias.detalle', id_familia=id_familia))

    familia.nombre = nombre
    db.session.commit()

    flash('Nombre de la familia actualizado correctamente.', 'success')
    return redirect(url_for('familias.detalle', id_familia=id_familia))


@familias_bp.route('/<int:id_familia>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar(id_familia):
    familia = db.get_or_404(Familia, id_familia)

    # Desvincular integrantes de la familia antes de eliminar
    for integrante in familia.integrantes:
        integrante.id_familia = None

    nom = familia.nombre
    db.session.delete(familia)
    db.session.commit()

    flash(f'{nom} eliminada del registro.', 'info')
    return redirect(url_for('familias.index'))
