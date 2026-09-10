from app import db
from app.models.auth import Usuario, Rol


def test_login_successful(client, app):
    """Verifica que un usuario activo pueda iniciar sesión correctamente."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        user = Usuario(usuario='testuser', id_rol=rol.id_rol, estado='Activo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', data={
        'usuario': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Bienvenido, testuser!' in response.data


def test_login_invalid_password(client, app):
    """Verifica que no se permita iniciar sesión con contraseña incorrecta."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        user = Usuario(usuario='testuser2', id_rol=rol.id_rol, estado='Activo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', data={
        'usuario': 'testuser2',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Usuario o contrase\xc3\xb1a incorrectos' in response.data


def test_login_inactive_user_blocked(client, app):
    """Verifica que los usuarios inactivos no puedan iniciar sesión."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        user = Usuario(usuario='inactiveuser', id_rol=rol.id_rol, estado='Inactivo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', data={
        'usuario': 'inactiveuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Esta cuenta se encuentra desactivada' in response.data


def test_logout(client, app):
    """Verifica que el logout cierre sesión y redirija a login."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        user = Usuario(usuario='logoutuser', id_rol=rol.id_rol, estado='Activo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Login
    client.post('/auth/login', data={'usuario': 'logoutuser', 'password': 'password123'})

    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Has cerrado sesi\xc3\xb3n correctamente' in response.data
