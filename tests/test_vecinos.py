from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Casa, Familia, Vecino


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_vecinos', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_vecinos', 'password': 'pass123'})


def test_crear_vecino(client, app):
    """Verifica la creación de un vecino con casa y familia."""
    _login_as_admin(client, app)

    with app.app_context():
        casa = Casa(numero_casa='505-A')
        fam = Familia(nombre='Familia Morales')
        db.session.add_all([casa, fam])
        db.session.commit()
        casa_id = casa.id_casa
        fam_id = fam.id_familia

    response = client.post('/vecinos/crear', data={
        'nombres': 'Ana Lucia',
        'apellidos': 'Morales Santos',
        'telefono': '5555-4321',
        'correo': 'ana.morales@test.com',
        'id_casa': casa_id,
        'id_familia': fam_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Ana Lucia Morales Santos' in response.data

    with app.app_context():
        v = Vecino.query.filter_by(correo='ana.morales@test.com').first()
        assert v is not None
        assert v.id_casa == casa_id
        assert v.id_familia == fam_id
        assert v.nombre_completo == 'Ana Lucia Morales Santos'


def test_editar_vecino(client, app):
    """Verifica la edición de los datos de un vecino."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Pedro', apellidos='Alvarez', telefono='1111-2222')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post(f'/vecinos/{v_id}/editar', data={
        'nombres': 'Pedro Antonio',
        'apellidos': 'Alvarez Gomez',
        'telefono': '3333-4444',
        'correo': 'pedro.alvarez@test.com'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        v = db.session.get(Vecino, v_id)
        assert v.nombres == 'Pedro Antonio'
        assert v.telefono == '3333-4444'


def test_eliminar_vecino(client, app):
    """Verifica la eliminación de un vecino."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Luis', apellidos='Reyes')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post(f'/vecinos/{v_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Vecino, v_id) is None
