from app import db
from app.models.auth import Usuario, Rol


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='superadmin', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'superadmin', 'password': 'adminpass'})


def test_crear_usuario(client, app):
    """Verifica la creación exitosa de un nuevo usuario."""
    _login_as_admin(client, app)

    with app.app_context():
        rol_consulta = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        rol_id = rol_consulta.id_rol

    response = client.post('/usuarios/crear', data={
        'usuario': 'nuevousuario',
        'password': 'password123',
        'id_rol': rol_id,
        'estado': 'Activo'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'nuevousuario' in response.data
    assert b'registrado exitosamente' in response.data

    with app.app_context():
        u = Usuario.query.filter_by(usuario='nuevousuario').first()
        assert u is not None
        assert u.check_password('password123') is True
        assert u.rol.nombre == 'Usuario de Consulta'


def test_toggle_estado_usuario(client, app):
    """Verifica la activación y desactivación de un usuario."""
    _login_as_admin(client, app)

    with app.app_context():
        rol = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        u = Usuario(usuario='toggleuser', id_rol=rol.id_rol, estado='Activo')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()
        u_id = u.id_usuario

    # Desactivar
    response = client.post(f'/usuarios/{u_id}/toggle-estado', follow_redirects=True)
    assert response.status_code == 200
    assert b'Inactivo' in response.data

    with app.app_context():
        u = db.session.get(Usuario, u_id)
        assert u.estado == 'Inactivo'


def test_cambiar_password_usuario(client, app):
    """Verifica el cambio de contraseña de un usuario."""
    _login_as_admin(client, app)

    with app.app_context():
        rol = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        u = Usuario(usuario='pwduser', id_rol=rol.id_rol, estado='Activo')
        u.set_password('oldpass123')
        db.session.add(u)
        db.session.commit()
        u_id = u.id_usuario

    # Cambiar contraseña
    response = client.post(f'/usuarios/{u_id}/cambiar-password', data={
        'nueva_password': 'newpass456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'actualizada exitosamente' in response.data

    with app.app_context():
        u = db.session.get(Usuario, u_id)
        assert u.check_password('newpass456') is True
        assert u.check_password('oldpass123') is False
