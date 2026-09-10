from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Casa, Familia, Vecino, Parentesco, VecinoParentesco
from app.models.finanzas import Deuda, Multa


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_e2e', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_e2e', 'password': 'pass123'})


def test_ciclo_de_vida_completo_sistema(client, app):
    """
    Prueba de Integración End-to-End:
    Valida el flujo integral del sistema residencial:
    1. Registro de Casa y Familia.
    2. Registro de dos Residentes (Padre e Hijo).
    3. Asignación de Parentesco entre ellos.
    4. Emisión y liquidación de Deudas.
    5. Aplicación y exoneración de Multas.
    6. Verificación de integridad en las vistas y fichas técnicas.
    """
    _login_as_admin(client, app)

    # 1. Registrar Casa
    res_casa = client.post('/casas/crear', data={
        'numero_casa': '10-E2E',
        'manzana': 'Mz-Principal',
        'calle_avenida': 'Boulevard Central',
        'estado': 'Ocupada'
    }, follow_redirects=True)
    assert res_casa.status_code == 200

    # 2. Registrar Familia
    res_fam = client.post('/familias/crear', data={
        'nombre': 'Familia Perez Gomez'
    }, follow_redirects=True)
    assert res_fam.status_code == 200

    with app.app_context():
        casa = Casa.query.filter_by(numero_casa='10-E2E').first()
        familia = Familia.query.filter_by(nombre='Familia Perez Gomez').first()
        assert casa is not None
        assert familia is not None
        casa_id = casa.id_casa
        fam_id = familia.id_familia

    # 3. Registrar Vecino 1 (Padre)
    res_v1 = client.post('/vecinos/crear', data={
        'nombres': 'Juan Carlos',
        'apellidos': 'Perez Gomez',
        'telefono': '5555-1111',
        'correo': 'juan.perez@colonia.com',
        'id_casa': casa_id,
        'id_familia': fam_id
    }, follow_redirects=True)
    assert res_v1.status_code == 200

    # 4. Registrar Vecino 2 (Hijo)
    res_v2 = client.post('/vecinos/crear', data={
        'nombres': 'Mateo',
        'apellidos': 'Perez Gomez',
        'telefono': '5555-2222',
        'correo': 'mateo.perez@colonia.com',
        'id_casa': casa_id,
        'id_familia': fam_id
    }, follow_redirects=True)
    assert res_v2.status_code == 200

    with app.app_context():
        v_padre = Vecino.query.filter_by(correo='juan.perez@colonia.com').first()
        v_hijo = Vecino.query.filter_by(correo='mateo.perez@colonia.com').first()
        p_padre = Parentesco.query.filter_by(nombre='Padre').first()
        assert v_padre is not None
        assert v_hijo is not None
        padre_id = v_padre.id_vecino
        hijo_id = v_hijo.id_vecino
        parentesco_padre_id = p_padre.id_parentesco

    # 5. Asignar Parentesco: Juan es Padre de Mateo
    res_parentesco = client.post('/parentescos/asignar', data={
        'id_vecino': padre_id,
        'id_relacionado': hijo_id,
        'id_parentesco': parentesco_padre_id
    }, follow_redirects=True)
    assert res_parentesco.status_code == 200

    # 6. Registrar Deuda para el Padre
    res_deuda = client.post('/deudas/crear', data={
        'id_vecino': padre_id,
        'concepto': 'Mantenimiento Mensual',
        'monto': '200.00',
        'estado': 'Pendiente'
    }, follow_redirects=True)
    assert res_deuda.status_code == 200

    # 7. Registrar Multa para el Padre
    res_multa = client.post('/multas/crear', data={
        'id_vecino': padre_id,
        'motivo': 'Estacionamiento en banqueta',
        'monto': '100.00',
        'estado': 'Pendiente'
    }, follow_redirects=True)
    assert res_multa.status_code == 200

    with app.app_context():
        deuda = Deuda.query.filter_by(id_vecino=padre_id, concepto='Mantenimiento Mensual').first()
        multa = Multa.query.filter_by(id_vecino=padre_id, motivo='Estacionamiento en banqueta').first()
        assert deuda is not None
        assert multa is not None
        deuda_id = deuda.id_deuda
        multa_id = multa.id_multa

    # 8. Liquidar la Deuda (Marcar como Pagada)
    res_pagar_deuda = client.post(f'/deudas/{deuda_id}/cambiar-estado', data={
        'nuevo_estado': 'Pagada'
    }, follow_redirects=True)
    assert res_pagar_deuda.status_code == 200

    # 9. Exonerar la Multa
    res_exonerar_multa = client.post(f'/multas/{multa_id}/cambiar-estado', data={
        'nuevo_estado': 'Exonerada'
    }, follow_redirects=True)
    assert res_exonerar_multa.status_code == 200

    # 10. Verificación Final de Estados e Integridad
    with app.app_context():
        d_final = db.session.get(Deuda, deuda_id)
        m_final = db.session.get(Multa, multa_id)
        assert d_final.estado == 'Pagada'
        assert m_final.estado == 'Exonerada'

        # Verificar relaciones en casa
        c_final = db.session.get(Casa, casa_id)
        assert len(c_final.vecinos) == 2

        # Verificar integrantes en familia
        f_final = db.session.get(Familia, fam_id)
        assert len(f_final.integrantes) == 2

        # Verificar parentesco registrado
        rel_final = VecinoParentesco.query.filter_by(
            id_vecino=padre_id,
            id_relacionado=hijo_id
        ).first()
        assert rel_final is not None
        assert rel_final.parentesco.nombre == 'Padre'

    # 11. Verificar que las vistas respondan correctamente
    assert client.get(f'/casas/{casa_id}').status_code == 200
    assert client.get(f'/familias/{fam_id}').status_code == 200
    assert client.get(f'/vecinos/{padre_id}').status_code == 200
    assert client.get('/deudas/').status_code == 200
    assert client.get('/multas/').status_code == 200
    assert client.get('/').status_code == 200
