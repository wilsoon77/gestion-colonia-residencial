from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.auth import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('password')

        user = Usuario.query.filter_by(usuario=username).first()

        if user and user.check_password(password):
            if user.estado != 'Activo':
                flash('Esta cuenta se encuentra desactivada. Consulta con un administrador.', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            flash(f'¡Bienvenido, {user.usuario}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))
