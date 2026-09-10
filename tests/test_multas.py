from decimal import Decimal
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino
from app.models.finanzas import Multa


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
