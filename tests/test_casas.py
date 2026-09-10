from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Casa, Vecino


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_casas', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_casas', 'password': 'pass123'})


def test_crear_casa(client, app):
    """Verifica la creación exitosa de una casa."""
    _login_as_admin(client, app)

    response = client.post('/casas/crear', data={
        'numero_casa': '101-A',
        'manzana': 'M-1',
        'calle_avenida': 'Calle Principal',
        'estado': 'Ocupada'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'101-A' in response.data

    with app.app_context():
        casa = Casa.query.filter_by(numero_casa='101-A').first()
        assert casa is not None
        assert casa.manzana == 'M-1'
        assert casa.estado == 'Ocupada'


def test_editar_casa(client, app):
    """Verifica la edición de una casa."""
    _login_as_admin(client, app)

    with app.app_context():
        casa = Casa(numero_casa='202-B', manzana='M-2', estado='Desocupada')
        db.session.add(casa)
        db.session.commit()
        casa_id = casa.id_casa

    response = client.post(f'/casas/{casa_id}/editar', data={
        'numero_casa': '202-B-Mod',
        'manzana': 'M-2-Norte',
        'calle_avenida': 'Avenida Central',
        'estado': 'Ocupada'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'202-B-Mod' in response.data

    with app.app_context():
        c = db.session.get(Casa, casa_id)
        assert c.numero_casa == '202-B-Mod'
        assert c.estado == 'Ocupada'


def test_eliminar_casa(client, app):
    """Verifica la eliminación de una casa y la desasociación de vecinos."""
    _login_as_admin(client, app)

    with app.app_context():
        casa = Casa(numero_casa='303-C', estado='Ocupada')
        db.session.add(casa)
        db.session.commit()

        vecino = Vecino(nombres='Carlos', apellidos='Ruiz', id_casa=casa.id_casa)
        db.session.add(vecino)
        db.session.commit()

        casa_id = casa.id_casa
        vecino_id = vecino.id_vecino

    response = client.post(f'/casas/{casa_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Casa, casa_id) is None
        v = db.session.get(Vecino, vecino_id)
        assert v is not None
        assert v.id_casa is None
