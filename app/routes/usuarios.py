from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino
from app.utils.decorators import admin_required

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/')
@login_required
@admin_required
def index():
    usuarios = Usuario.query.order_by(Usuario.id_usuario.asc()).all()
    roles = Rol.query.order_by(Rol.id_rol.asc()).all()
    vecinos = Vecino.query.order_by(Vecino.nombres.asc()).all()
    return render_template('auth/usuarios.html', usuarios=usuarios, roles=roles, vecinos=vecinos)


@usuarios_bp.route('/crear', methods=['POST'])
@login_required
@admin_required
def crear():
    username = request.form.get('usuario', '').strip()
    password = request.form.get('password', '').strip()
    id_rol = request.form.get('id_rol')
    id_vecino = request.form.get('id_vecino')
    estado = request.form.get('estado', 'Activo')

    if not username or not password or not id_rol:
        flash('Todos los campos obligatorios deben ser completados.', 'danger')
        return redirect(url_for('usuarios.index'))

    # Validar si el usuario ya existe
    if Usuario.query.filter_by(usuario=username).first():
        flash(f'El nombre de usuario "{username}" ya está registrado.', 'warning')
        return redirect(url_for('usuarios.index'))

    nuevo_usuario = Usuario(
        usuario=username,
        id_rol=int(id_rol),
        id_vecino=int(id_vecino) if id_vecino and id_vecino.isdigit() else None,
        estado=estado
    )
    nuevo_usuario.set_password(password)

    db.session.add(nuevo_usuario)
    db.session.commit()

    flash(f'Usuario {username} registrado exitosamente.', 'success')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/<int:id_usuario>/editar', methods=['POST'])
@login_required
@admin_required
def editar(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)

    id_rol = request.form.get('id_rol')
    id_vecino = request.form.get('id_vecino')
    estado = request.form.get('estado')

    if id_rol:
        usuario.id_rol = int(id_rol)

    usuario.id_vecino = int(id_vecino) if id_vecino and id_vecino.isdigit() else None

    # Prevenir que el usuario actual se inactive a sí mismo
    if estado:
        if usuario.id_usuario == current_user.id_usuario and estado != 'Activo':
            flash('No puedes desactivar tu propio usuario en sesión.', 'warning')
        else:
            usuario.estado = estado

    db.session.commit()
    flash(f'Usuario {usuario.usuario} actualizado correctamente.', 'success')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/<int:id_usuario>/toggle-estado', methods=['POST'])
@login_required
@admin_required
def toggle_estado(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)

    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes cambiar el estado de tu propia cuenta en sesión.', 'warning')
        return redirect(url_for('usuarios.index'))

    usuario.estado = 'Inactivo' if usuario.estado == 'Activo' else 'Activo'
    db.session.commit()

    flash(f'El estado del usuario {usuario.usuario} ahora es {usuario.estado}.', 'info')
    return redirect(url_for('usuarios.index'))


@usuarios_bp.route('/<int:id_usuario>/cambiar-password', methods=['POST'])
@login_required
@admin_required
def cambiar_password(id_usuario):
    usuario = db.get_or_404(Usuario, id_usuario)
    nueva_password = request.form.get('nueva_password', '').strip()

    if not nueva_password or len(nueva_password) < 6:
        flash('La contraseña debe contener al menos 6 caracteres.', 'danger')
        return redirect(url_for('usuarios.index'))

    usuario.set_password(nueva_password)
    db.session.commit()

    flash(f'Contraseña del usuario {usuario.usuario} actualizada exitosamente.', 'success')
    return redirect(url_for('usuarios.index'))
