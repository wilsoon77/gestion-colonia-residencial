from decimal import Decimal
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino
from app.models.finanzas import Deuda


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_deudas', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_deudas', 'password': 'pass123'})


def test_crear_deuda(client, app):
    """Verifica la creación exitosa de una deuda."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Fernando', apellidos='Castillo')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post('/deudas/crear', data={
        'id_vecino': v_id,
        'concepto': 'Mantenimiento Agosto 2026',
        'monto': '250.50',
        'estado': 'Pendiente'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Mantenimiento Agosto 2026' in response.data

    with app.app_context():
        d = Deuda.query.filter_by(concepto='Mantenimiento Agosto 2026').first()
        assert d is not None
        assert d.monto == Decimal('250.50')
        assert d.estado == 'Pendiente'
        assert d.id_vecino == v_id


def test_editar_deuda(client, app):
    """Verifica la edición de una deuda existente."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Gloria', apellidos='Mendez')
        db.session.add(vecino)
        db.session.commit()

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Cuota Agua', monto=Decimal('100.00'), estado='Pendiente')
        db.session.add(deuda)
        db.session.commit()

        d_id = deuda.id_deuda
        v_id = vecino.id_vecino

    response = client.post(f'/deudas/{d_id}/editar', data={
        'id_vecino': v_id,
        'concepto': 'Cuota Agua y Seguridad',
        'monto': '150.75',
        'estado': 'Pendiente'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        d = db.session.get(Deuda, d_id)
        assert d.concepto == 'Cuota Agua y Seguridad'
        assert d.monto == Decimal('150.75')


def test_cambiar_estado_deuda(client, app):
    """Verifica el cambio de estado de una deuda a Pagada."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Hector', apellidos='Lima')
        db.session.add(vecino)
        db.session.commit()

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Basura', monto=Decimal('50.00'), estado='Pendiente')
        db.session.add(deuda)
        db.session.commit()
        d_id = deuda.id_deuda

    # Cambiar a Pagada
    response = client.post(f'/deudas/{d_id}/cambiar-estado', data={
        'nuevo_estado': 'Pagada'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'cambiado a Pagada' in response.data

    with app.app_context():
        d = db.session.get(Deuda, d_id)
        assert d.estado == 'Pagada'


def test_eliminar_deuda(client, app):
    """Verifica la eliminación de un registro de deuda."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Irma', apellidos='Solis')
        db.session.add(vecino)
        db.session.commit()

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Servicio Extra', monto=Decimal('75.00'))
        db.session.add(deuda)
        db.session.commit()
        d_id = deuda.id_deuda

    response = client.post(f'/deudas/{d_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Deuda, d_id) is None


def test_rechazo_monto_invalido(client, app):
    """Verifica que montos negativos o inválidos sean rechazados."""
    _login_as_admin(client, app)

    with app.app_context():
        vecino = Vecino(nombres='Jorge', apellidos='Valdez')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    response = client.post('/deudas/crear', data={
        'id_vecino': v_id,
        'concepto': 'Invalido',
        'monto': '-50.00'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'debe ser un valor positivo' in response.data
