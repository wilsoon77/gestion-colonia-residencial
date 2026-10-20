import io
from decimal import Decimal
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino
from app.models.finanzas import Multa, EvidenciaMulta


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_multas', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_multas', 'password': 'pass123'})


def test_crear_multa(client, app):
    """Verifica la creación exitosa de una multa."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Karla', apellidos='Pineda')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post('/multas/crear', data={
        'id_vecino': v_id,
        'motivo': 'Musica a alto volumen',
        'monto': '150.00',
        'estado': 'Pendiente'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Musica a alto volumen' in response.data

    with app.app_context():
        m = Multa.query.filter_by(motivo='Musica a alto volumen').first()
        assert m is not None
        assert m.monto == Decimal('150.00')
        assert m.estado == 'Pendiente'
        assert m.id_vecino == v_id


def test_editar_multa(client, app):
    """Verifica la edición de una multa existente."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Leonel', apellidos='Cruz')
        db.session.add(vecino)
        db.session.commit()

        multa = Multa(
            id_vecino=vecino.id_vecino,
            motivo='Mascota sin correa',
            monto=Decimal('75.00'),
            estado='Pendiente'
        )
        db.session.add(multa)
        db.session.commit()

        m_id = multa.id_multa
        v_id = vecino.id_vecino

    response = client.post(f'/multas/{m_id}/editar', data={
        'id_vecino': v_id,
        'motivo': 'Mascota sin correa en area comun',
        'monto': '100.00',
        'estado': 'Pendiente'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        m = db.session.get(Multa, m_id)
        assert m.motivo == 'Mascota sin correa en area comun'
        assert m.monto == Decimal('100.00')


def test_cambiar_estado_multa_exonerada(client, app):
    """Verifica el cambio de estado de una multa a Exonerada."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Manuel', apellidos='Soto')
        db.session.add(vecino)
        db.session.commit()

        multa = Multa(
            id_vecino=vecino.id_vecino,
            motivo='Estacionamiento indebido',
            monto=Decimal('100.00'),
            estado='Pendiente'
        )
        db.session.add(multa)
        db.session.commit()
        m_id = multa.id_multa

    # Cambiar a Exonerada
    response = client.post(f'/multas/{m_id}/cambiar-estado', data={
        'nuevo_estado': 'Exonerada'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'cambiado a Exonerada' in response.data

    with app.app_context():
        m = db.session.get(Multa, m_id)
        assert m.estado == 'Exonerada'


def test_eliminar_multa(client, app):
    """Verifica la eliminación de un registro de multa."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Nadia', apellidos='Lopez')
        db.session.add(vecino)
        db.session.commit()

        multa = Multa(id_vecino=vecino.id_vecino, motivo='Tirar basura', monto=Decimal('50.00'))
        db.session.add(multa)
        db.session.commit()
        m_id = multa.id_multa

    response = client.post(f'/multas/{m_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Multa, m_id) is None


def test_rechazo_monto_multa_invalido(client, app):
    """Verifica que montos negativos o inválidos en multas sean rechazados."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Oscar', apellidos='Paz')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post('/multas/crear', data={
        'id_vecino': v_id,
        'motivo': 'Invalido',
        'monto': '0.00'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'debe ser un valor positivo' in response.data


def test_crear_multa_con_evidencias(client, app, monkeypatch):
    """Verifica que al crear una multa con imágenes adjuntas, se guarden como EvidenciaMulta."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder="residencial/multas"):
        return {
            'url': 'https://res.cloudinary.com/test/image/upload/v123/foto.jpg',
            'public_id': 'residencial/multas/foto_123',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.multas.subir_imagen', mock_subir)

    with app.app_context():
        vecino = Vecino(nombres='Roberto', apellidos='Gomez')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    data = {
        'id_vecino': v_id,
        'motivo': 'Exceso de velocidad',
        'monto': '200.00',
        'evidencias': (io.BytesIO(b'dummy-image-bytes'), 'infraccion.jpg')
    }

    response = client.post('/multas/crear', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        multa = Multa.query.filter_by(motivo='Exceso de velocidad').first()
        assert multa is not None
        assert len(multa.evidencias) == 1
        ev = multa.evidencias[0]
        assert ev.public_id == 'residencial/multas/foto_123'
        assert ev.nombre_archivo == 'infraccion.jpg'
        assert 'https://res.cloudinary.com' in ev.url


def test_subir_evidencias_multa_existente(client, app, monkeypatch):
    """Verifica la carga posterior de fotos de evidencia en el detalle de una multa."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder="residencial/multas"):
        return {
            'url': 'https://res.cloudinary.com/test/image/upload/v456/extra.png',
            'public_id': 'residencial/multas/extra_456',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.multas.subir_imagen', mock_subir)

    with app.app_context():
        vecino = Vecino(nombres='Lucia', apellidos='Mendez')
        db.session.add(vecino)
        db.session.commit()

        multa = Multa(id_vecino=vecino.id_vecino, motivo='Estacionar sobre banqueta', monto=Decimal('150.00'))
        db.session.add(multa)
        db.session.commit()
        m_id = multa.id_multa

    data = {
        'evidencias': (io.BytesIO(b'extra-image-bytes'), 'evidencia2.png')
    }

    response = client.post(
        f'/multas/{m_id}/evidencias/subir',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200

    with app.app_context():
        multa = db.session.get(Multa, m_id)
        assert len(multa.evidencias) == 1
        assert multa.evidencias[0].nombre_archivo == 'evidencia2.png'


def test_eliminar_evidencia_multa(client, app, monkeypatch):
    """Verifica que se elimine el registro de evidencia y se llame a eliminar_imagen de Cloudinary."""
    _login_as_admin(client, app)

    deleted_public_ids = []

    def mock_eliminar(public_id):
        deleted_public_ids.append(public_id)
        return True

    monkeypatch.setattr('app.routes.multas.eliminar_imagen', mock_eliminar)

    with app.app_context():
        vecino = Vecino(nombres='Diana', apellidos='Morales')
        db.session.add(vecino)
        db.session.commit()

        multa = Multa(id_vecino=vecino.id_vecino, motivo='Desechos en parque', monto=Decimal('100.00'))
        db.session.add(multa)
        db.session.commit()

        evidencia = EvidenciaMulta(
            id_multa=multa.id_multa,
            url='https://res.cloudinary.com/test/diana.jpg',
            public_id='residencial/multas/diana_999',
            nombre_archivo='diana.jpg'
        )
        db.session.add(evidencia)
        db.session.commit()

        m_id = multa.id_multa
        ev_id = evidencia.id_evidencia

    response = client.post(f'/multas/{m_id}/evidencias/{ev_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200
    assert 'residencial/multas/diana_999' in deleted_public_ids

    with app.app_context():
        assert db.session.get(EvidenciaMulta, ev_id) is None


def test_rechazo_archivo_no_imagen(client, app):
    """Verifica que archivos que no son imágenes sean rechazados y no se registren como evidencias."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Fernando', apellidos='Castillo')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    data = {
        'id_vecino': v_id,
        'motivo': 'Ruido fuera de horario',
        'monto': '125.00',
        'evidencias': (io.BytesIO(b'%PDF-1.4...fake pdf'), 'documento.pdf')
    }

    response = client.post('/multas/crear', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        multa = Multa.query.filter_by(motivo='Ruido fuera de horario').first()
        assert multa is not None
        assert len(multa.evidencias) == 0


def test_usuario_consulta_ve_evidencias_su_multa(client, app):
    """Verifica que un residente pueda ver el detalle de su multa con sus evidencias fotográficas."""
    with app.app_context():
        rol_consulta = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        vecino = Vecino(nombres='Sonia', apellidos='Alvarez')
        db.session.add(vecino)
        db.session.commit()

        usuario = Usuario(
            usuario='sonia_residente',
            id_rol=rol_consulta.id_rol,
            id_vecino=vecino.id_vecino,
            estado='Activo'
        )
        usuario.set_password('pass123')
        db.session.add(usuario)

        multa = Multa(id_vecino=vecino.id_vecino, motivo='Pintar porton sin permiso', monto=Decimal('80.00'))
        db.session.add(multa)
        db.session.commit()

        evidencia = EvidenciaMulta(
            id_multa=multa.id_multa,
            url='https://res.cloudinary.com/test/porton.jpg',
            public_id='residencial/multas/porton_789',
            nombre_archivo='porton.jpg'
        )
        db.session.add(evidencia)
        db.session.commit()
        m_id = multa.id_multa

    client.post('/auth/login', data={'usuario': 'sonia_residente', 'password': 'pass123'})

    response = client.get(f'/multas/{m_id}')
    assert response.status_code == 200
    assert b'porton.jpg' in response.data
    assert b'https://res.cloudinary.com/test/porton.jpg' in response.data
