from decimal import Decimal
from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino, Casa, Familia
from app.models.finanzas import Deuda, Multa


def test_admin_can_access_usuarios(client, app):
    """Verifica que un usuario con rol 'Administrador' pueda acceder al módulo de usuarios."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        user = Usuario(usuario='admin_tester', id_rol=rol.id_rol, estado='Activo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Login como Administrador
    client.post('/auth/login', data={'usuario': 'admin_tester', 'password': 'password123'})

    response = client.get('/usuarios/')
    assert response.status_code == 200
    assert b'Gesti\xc3\xb3n de Usuarios' in response.data


def test_non_admin_forbidden_from_usuarios(client, app):
    """Verifica que un usuario sin rol de 'Administrador' reciba error 403 al acceder a usuarios."""
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Usuario de Consulta').first()
        user = Usuario(usuario='consulta_user', id_rol=rol.id_rol, estado='Activo')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    # Login como Usuario de Consulta
    client.post('/auth/login', data={'usuario': 'consulta_user', 'password': 'password123'})

    response = client.get('/usuarios/')
    assert response.status_code == 403
    assert b'Acceso No Autorizado' in response.data


def test_usuario_consulta_solo_ve_sus_deudas_y_multas(client, app):
    """Verifica que un usuario de consulta solo vea sus propias deudas y reciba 403 en las de otros."""
    with app.app_context():
        rol_consulta = Rol.query.filter_by(nombre='Usuario de Consulta').first()

        # Residente 1 (con usuario)
        v1 = Vecino(nombres='Carlos', apellidos='Prueba')
        db.session.add(v1)
        db.session.flush()

        u1 = Usuario(usuario='carlos_residente', id_rol=rol_consulta.id_rol, id_vecino=v1.id_vecino, estado='Activo')
        u1.set_password('pass123')

        # Residente 2
        v2 = Vecino(nombres='Pedro', apellidos='Otro')
        db.session.add(v2)
        db.session.flush()

        d1 = Deuda(id_vecino=v1.id_vecino, concepto='Deuda de Carlos', monto=Decimal('100.00'), estado='Pendiente')
        d2 = Deuda(id_vecino=v2.id_vecino, concepto='Deuda de Pedro', monto=Decimal('200.00'), estado='Pendiente')

        m1 = Multa(id_vecino=v1.id_vecino, motivo='Multa de Carlos', monto=Decimal('50.00'), estado='Pendiente')
        m2 = Multa(id_vecino=v2.id_vecino, motivo='Multa de Pedro', monto=Decimal('75.00'), estado='Pendiente')

        db.session.add_all([u1, d1, d2, m1, m2])
        db.session.commit()

        d1_id = d1.id_deuda
        d2_id = d2.id_deuda
        m1_id = m1.id_multa
        m2_id = m2.id_multa

    # Login como Carlos
    client.post('/auth/login', data={'usuario': 'carlos_residente', 'password': 'pass123'})

    # 1. Al consultar lista de deudas, solo ve la suya
    res_deudas = client.get('/deudas/')
    assert res_deudas.status_code == 200
    assert b'Deuda de Carlos' in res_deudas.data
    assert b'Deuda de Pedro' not in res_deudas.data

    # 2. Acceso a su propia deuda OK
    assert client.get(f'/deudas/{d1_id}').status_code == 200

    # 3. Acceso a deuda ajena -> 403
    assert client.get(f'/deudas/{d2_id}').status_code == 403

    # 4. Al consultar lista de multas, solo ve la suya
    res_multas = client.get('/multas/')
    assert res_multas.status_code == 200
    assert b'Multa de Carlos' in res_multas.data
    assert b'Multa de Pedro' not in res_multas.data

    # 5. Acceso a su propia multa OK
    assert client.get(f'/multas/{m1_id}').status_code == 200

    # 6. Acceso a multa ajena -> 403
    assert client.get(f'/multas/{m2_id}').status_code == 403


def test_usuario_consulta_restringido_a_su_casa_y_familia(client, app):
    """Verifica que un usuario de consulta solo pueda acceder a su propia vivienda y familia."""
    with app.app_context():
        rol_consulta = Rol.query.filter_by(nombre='Usuario de Consulta').first()

        c1 = Casa(numero_casa='Casa-100')
        c2 = Casa(numero_casa='Casa-200')
        f1 = Familia(nombre='Familia Uno')
        f2 = Familia(nombre='Familia Dos')
        db.session.add_all([c1, c2, f1, f2])
        db.session.flush()

        v = Vecino(nombres='Laura', apellidos='Vecina', id_casa=c1.id_casa, id_familia=f1.id_familia)
        db.session.add(v)
        db.session.flush()

        u = Usuario(usuario='laura_usr', id_rol=rol_consulta.id_rol, id_vecino=v.id_vecino, estado='Activo')
        u.set_password('pass123')
        db.session.add(u)
        db.session.commit()

        c1_id = c1.id_casa
        c2_id = c2.id_casa
        f1_id = f1.id_familia
        f2_id = f2.id_familia

    # Login como Laura
    client.post('/auth/login', data={'usuario': 'laura_usr', 'password': 'pass123'})

    # Su propia casa -> 200
    assert client.get(f'/casas/{c1_id}').status_code == 200
    # Casa ajena -> 403
    assert client.get(f'/casas/{c2_id}').status_code == 403

    # Su propia familia -> 200
    assert client.get(f'/familias/{f1_id}').status_code == 200
    # Familia ajena -> 403
    assert client.get(f'/familias/{f2_id}').status_code == 403
