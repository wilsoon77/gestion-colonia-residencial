from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Familia, Vecino


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_familias', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_familias', 'password': 'pass123'})


def test_crear_familia(client, app):
    """Verifica la creación de una familia."""
    _login_as_admin(client, app)

    response = client.post('/familias/crear', data={
        'nombre': 'Familia Perez Lopez'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Familia Perez Lopez' in response.data

    with app.app_context():
        fam = Familia.query.filter_by(nombre='Familia Perez Lopez').first()
        assert fam is not None


def test_editar_familia(client, app):
    """Verifica la edición del nombre de una familia."""
    _login_as_admin(client, app)

    with app.app_context():
        fam = Familia(nombre='Familia Gomez')
        db.session.add(fam)
        db.session.commit()
        fam_id = fam.id_familia

    response = client.post(f'/familias/{fam_id}/editar', data={
        'nombre': 'Familia Gomez Morales'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        f = db.session.get(Familia, fam_id)
        assert f.nombre == 'Familia Gomez Morales'


def test_eliminar_familia(client, app):
    """Verifica la eliminación de una familia y desvinculación de integrantes."""
    _login_as_admin(client, app)

    with app.app_context():
        fam = Familia(nombre='Familia Diaz')
        db.session.add(fam)
        db.session.commit()

        vecino = Vecino(nombres='Maria', apellidos='Diaz', id_familia=fam.id_familia)
        db.session.add(vecino)
        db.session.commit()

        fam_id = fam.id_familia
        vecino_id = vecino.id_vecino

    response = client.post(f'/familias/{fam_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Familia, fam_id) is None
        v = db.session.get(Vecino, vecino_id)
        assert v is not None
        assert v.id_familia is None
