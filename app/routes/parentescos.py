from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.residencia import Parentesco, VecinoParentesco, Vecino
from app.utils.decorators import role_required

parentescos_bp = Blueprint('parentescos', __name__)


@parentescos_bp.route('/')
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def index():
    parentescos = Parentesco.query.order_by(Parentesco.nombre.asc()).all()
    total_relaciones = VecinoParentesco.query.count()
    return render_template('parentescos/index.html', parentescos=parentescos, total_relaciones=total_relaciones)


@parentescos_bp.route('/crear', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def crear():
    nombre = request.form.get('nombre', '').strip()

    if not nombre:
        flash('El nombre del parentesco es obligatorio.', 'danger')
        return redirect(url_for('parentescos.index'))

    if Parentesco.query.filter_by(nombre=nombre).first():
        flash(f'El parentesco "{nombre}" ya existe en el catálogo.', 'warning')
        return redirect(url_for('parentescos.index'))

    nuevo_parentesco = Parentesco(nombre=nombre)
    db.session.add(nuevo_parentesco)
    db.session.commit()

    flash(f'Parentesco "{nombre}" añadido exitosamente al catálogo.', 'success')
    return redirect(url_for('parentescos.index'))


@parentescos_bp.route('/asignar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def asignar():
    id_vecino = request.form.get('id_vecino')
    id_relacionado = request.form.get('id_relacionado')
    id_parentesco = request.form.get('id_parentesco')
    next_url = request.form.get('next_url')

    if not id_vecino or not id_relacionado or not id_parentesco:
        flash('Todos los campos son obligatorios para establecer el parentesco.', 'danger')
        return redirect(next_url or url_for('vecinos.index'))

    id_vecino = int(id_vecino)
    id_relacionado = int(id_relacionado)
    id_parentesco = int(id_parentesco)

    if id_vecino == id_relacionado:
        flash('No se puede asignar una relación de parentesco de una persona consigo misma.', 'warning')
        return redirect(next_url or url_for('vecinos.detalle', id_vecino=id_vecino))

    # Verificar si la relación ya existe
    existe = VecinoParentesco.query.filter_by(
        id_vecino=id_vecino,
        id_relacionado=id_relacionado,
        id_parentesco=id_parentesco
    ).first()

    if existe:
        flash('Esta relación de parentesco ya se encuentra registrada.', 'info')
        return redirect(next_url or url_for('vecinos.detalle', id_vecino=id_vecino))

    nueva_relacion = VecinoParentesco(
        id_vecino=id_vecino,
        id_relacionado=id_relacionado,
        id_parentesco=id_parentesco
    )
    db.session.add(nueva_relacion)
    db.session.commit()

    vecino_a = db.session.get(Vecino, id_vecino)
    vecino_b = db.session.get(Vecino, id_relacionado)
    tipo_p = db.session.get(Parentesco, id_parentesco)

    flash(
        f'Relación establecida: {vecino_a.nombre_completo} es {tipo_p.nombre} de {vecino_b.nombre_completo}.',
        'success'
    )
    return redirect(next_url or url_for('vecinos.detalle', id_vecino=id_vecino))


@parentescos_bp.route('/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Administrador de Colonia')
def eliminar():
    id_vecino = request.form.get('id_vecino')
    id_relacionado = request.form.get('id_relacionado')
    id_parentesco = request.form.get('id_parentesco')
    next_url = request.form.get('next_url')

    if not id_vecino or not id_relacionado or not id_parentesco:
        flash('Datos incompletos para eliminar la relación.', 'danger')
        return redirect(next_url or url_for('vecinos.index'))

    relacion = VecinoParentesco.query.filter_by(
        id_vecino=int(id_vecino),
        id_relacionado=int(id_relacionado),
        id_parentesco=int(id_parentesco)
    ).first()

    if relacion:
        db.session.delete(relacion)
        db.session.commit()
        flash('Relación de parentesco eliminada correctamente.', 'info')
    else:
        flash('La relación que intentas eliminar no fue encontrada.', 'warning')

    return redirect(next_url or url_for('vecinos.detalle', id_vecino=int(id_vecino)))
