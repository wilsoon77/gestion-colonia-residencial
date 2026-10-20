import io
from decimal import Decimal
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino
from app.models.finanzas import Deuda, ComprobanteDeuda


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


def test_crear_deuda_con_comprobante(client, app, monkeypatch):
    """Verifica la creación de una deuda con comprobante bancario adjunto."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder='residencial/deudas_comprobantes'):
        return {
            'url': 'https://res.cloudinary.com/test/comprobante1.jpg',
            'public_id': 'residencial/deudas_comprobantes/comp_001',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.deudas.subir_imagen', mock_subir)

    with app.app_context():
        vecino = Vecino(nombres='Karina', apellidos='Duarte')
        db.session.add(vecino)
        db.session.commit()
        v_id = vecino.id_vecino

    data = {
        'id_vecino': v_id,
        'concepto': 'Mantenimiento Septiembre 2026',
        'monto': '300.00',
        'comprobantes': (io.BytesIO(b'voucher-bytes'), 'boleta_banco.jpg')
    }

    response = client.post('/deudas/crear', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        deuda = Deuda.query.filter_by(concepto='Mantenimiento Septiembre 2026').first()
        assert deuda is not None
        assert len(deuda.comprobantes) == 1
        comp = deuda.comprobantes[0]
        assert comp.public_id == 'residencial/deudas_comprobantes/comp_001'
        assert comp.nombre_archivo == 'boleta_banco.jpg'


def test_subir_comprobante_deuda_existente(client, app, monkeypatch):
    """Verifica adjuntar un comprobante de pago a una deuda existente."""
    _login_as_admin(client, app)

    def mock_subir(file_storage, folder='residencial/deudas_comprobantes'):
        return {
            'url': 'https://res.cloudinary.com/test/recibo2.png',
            'public_id': 'residencial/deudas_comprobantes/recibo_002',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.deudas.subir_imagen', mock_subir)

    with app.app_context():
        vecino = Vecino(nombres='Mario', apellidos='Bautista')
        db.session.add(vecino)
        db.session.commit()

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Cuota extraordinaria', monto=Decimal('500.00'))
        db.session.add(deuda)
        db.session.commit()
        d_id = deuda.id_deuda

    data = {
        'comprobantes': (io.BytesIO(b'img-bytes'), 'recibo_transferencia.png')
    }

    response = client.post(
        f'/deudas/{d_id}/comprobantes/subir',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200

    with app.app_context():
        d = db.session.get(Deuda, d_id)
        assert len(d.comprobantes) == 1
        assert d.comprobantes[0].nombre_archivo == 'recibo_transferencia.png'


def test_eliminar_comprobante_deuda(client, app, monkeypatch):
    """Verifica que se elimine el comprobante de la deuda y de Cloudinary."""
    _login_as_admin(client, app)

    deleted_pids = []

    def mock_eliminar(public_id):
        deleted_pids.append(public_id)
        return True

    monkeypatch.setattr('app.routes.deudas.eliminar_imagen', mock_eliminar)

    with app.app_context():
        vecino = Vecino(nombres='Sandra', apellidos='Giron')
        db.session.add(vecino)
        db.session.commit()

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Reparacion bomba', monto=Decimal('120.00'))
        db.session.add(deuda)
        db.session.commit()

        comp = ComprobanteDeuda(
            id_deuda=deuda.id_deuda,
            url='https://res.cloudinary.com/test/comp.jpg',
            public_id='residencial/deudas_comprobantes/sandra_voucher',
            nombre_archivo='comp.jpg'
        )
        db.session.add(comp)
        db.session.commit()
        d_id = deuda.id_deuda
        comp_id = comp.id_comprobante

    response = client.post(f'/deudas/{d_id}/comprobantes/{comp_id}/eliminar', follow_redirects=True)
    assert response.status_code == 200
    assert 'residencial/deudas_comprobantes/sandra_voucher' in deleted_pids

    with app.app_context():
        assert db.session.get(ComprobanteDeuda, comp_id) is None


def test_usuario_consulta_sube_comprobante_su_deuda(client, app, monkeypatch):
    """Verifica que un residente pueda adjuntar comprobante a su propia deuda."""
    def mock_subir(file_storage, folder='residencial/deudas_comprobantes'):
        return {
            'url': 'https://res.cloudinary.com/test/residente_boleta.jpg',
            'public_id': 'residencial/deudas_comprobantes/residente_001',
            'nombre_archivo': file_storage.filename,
        }

    monkeypatch.setattr('app.routes.deudas.subir_imagen', mock_subir)

    with app.app_context():
        rol_consulta = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        vecino = Vecino(nombres='Elena', apellidos='Pineda')
        db.session.add(vecino)
        db.session.commit()

        usuario = Usuario(
            usuario='elena_residente',
            id_rol=rol_consulta.id_rol,
            id_vecino=vecino.id_vecino,
            estado='Activo'
        )
        usuario.set_password('pass123')
        db.session.add(usuario)

        deuda = Deuda(id_vecino=vecino.id_vecino, concepto='Cuota de Agua Elena', monto=Decimal('100.00'))
        db.session.add(deuda)
        db.session.commit()
        d_id = deuda.id_deuda

    client.post('/auth/login', data={'usuario': 'elena_residente', 'password': 'pass123'})

    data = {
        'comprobantes': (io.BytesIO(b'boleta-bytes'), 'boleta_deposito.jpg')
    }

    response = client.post(
        f'/deudas/{d_id}/comprobantes/subir',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 200

    with app.app_context():
        d = db.session.get(Deuda, d_id)
        assert len(d.comprobantes) == 1
        assert d.comprobantes[0].nombre_archivo == 'boleta_deposito.jpg'
