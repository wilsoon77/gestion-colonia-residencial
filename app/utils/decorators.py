from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user


def role_required(*allowed_roles):
    """
    Decorador para restringir el acceso a usuarios que tengan uno de los roles permitidos.
    Uso: @role_required('Administrador', 'Administrador de Colonia')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            if not current_user.rol or current_user.rol.nombre not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Acceso restringido únicamente para el rol 'Administrador'."""
    return role_required('Administrador')(f)
