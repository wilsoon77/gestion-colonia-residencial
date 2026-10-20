import io
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Casa, FotoCasa, Vecino


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


def test_crear_casa_con_fotos(client, app, monkeypatch):
    """Verifica la creación de una casa con fotos de fachada."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder='residencial/casas'):
        return {
            'url': 'https://res.cloudinary.com/test/fachada.jpg',
            'public_id': 'residencial/casas/casa_102_fachada',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.casas.subir_imagen', mock_subir)

    data = {
        'numero_casa': '505-E',
        'manzana': 'Mz 5',
        'calle_avenida': 'Boulevard Principal',
        'estado': 'Ocupada',
        'fotos': (io.BytesIO(b'dummy-photo'), 'fachada_principal.jpg')
    }

    response = client.post('/casas/crear', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        c = Casa.query.filter_by(numero_casa='505-E').first()
        assert c is not None
        assert len(c.fotos) == 1
        assert c.fotos[0].nombre_archivo == 'fachada_principal.jpg'
        assert c.fotos[0].public_id == 'residencial/casas/casa_102_fachada'


def test_subir_fotos_casa_existente(client, app, monkeypatch):
    """Verifica la carga de fotos adicionales en el detalle de una casa."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder='residencial/casas'):
        return {
            'url': 'https://res.cloudinary.com/test/patio.jpg',
            'public_id': 'residencial/casas/casa_patio_01',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.casas.subir_imagen', mock_subir)

    with app.app_context():
        casa = Casa(numero_casa='606-F', estado='Ocupada')
        db.session.add(casa)
        db.session.commit()
        c_id = casa.id_casa

    data = {
        'descripcion': 'Jardin y cochera',
        'fotos': (io.BytesIO(b'patio-bytes'), 'patio.png')
    }

    response = client.post(
        f'/casas/{c_id}/fotos/subir',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200

    with app.app_context():
        c = db.session.get(Casa, c_id)
        assert len(c.fotos) == 1
        assert c.fotos[0].descripcion == 'Jardin y cochera'


def test_eliminar_foto_casa(client, app, monkeypatch):
    """Verifica que se elimine una foto del inmueble y de Cloudinary."""
    _login_as_admin(client, app)

    deleted_pids = []

    def mock_eliminar(public_id):
        deleted_pids.append(public_id)
        return True

    monkeypatch.setattr('app.routes.casas.eliminar_imagen', mock_eliminar)

    with app.app_context():
        casa = Casa(numero_casa='707-G', estado='Ocupada')
        db.session.add(casa)
        db.session.commit()

        foto = FotoCasa(
            id_casa=casa.id_casa,
            url='https://res.cloudinary.com/test/casa707.jpg',
            public_id='residencial/casas/casa_707_foto',
            nombre_archivo='casa707.jpg'
        )
        db.session.add(foto)
        db.session.commit()
        c_id = casa.id_casa
        f_id = foto.id_foto

    response = client.post(f'/casas/{c_id}/fotos/{f_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200
    assert 'residencial/casas/casa_707_foto' in deleted_pids

    with app.app_context():
        assert db.session.get(FotoCasa, f_id) is None
