from app import db
from app.models.auth import Usuario, Rol
from app.models.residencia import Vecino, Parentesco, VecinoParentesco


def _login_as_admin(client, app):
    with app.app_context():
        rol = Rol.query.filter_by(nombre='Administrador').first()
        admin = Usuario(usuario='admin_parentesco', id_rol=rol.id_rol, estado='Activo')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'usuario': 'admin_parentesco', 'password': 'pass123'})


def test_crear_parentesco_catalogo(client, app):
    """Verifica la creación de un nuevo tipo de parentesco en el catálogo."""
    _login_as_admin(client, app)

    response = client.post('/parentescos/crear', data={
        'nombre': 'Abuelo(a)'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Abuelo(a)' in response.data

    with app.app_context():
        p = Parentesco.query.filter_by(nombre='Abuelo(a)').first()
        assert p is not None


def test_asignar_parentesco(client, app):
    """Verifica la asignación de una relación de parentesco entre dos vecinos."""
    _login_as_admin(client, app)

    with app.app_context():
        v1 = Vecino(nombres='Mario', apellidos='Gomez')
        v2 = Vecino(nombres='Mateo', apellidos='Gomez')
        p = Parentesco.query.filter_by(nombre='Padre').first()
        db.session.add_all([v1, v2])
        db.session.commit()
        v1_id = v1.id_vecino
        v2_id = v2.id_vecino
        p_id = p.id_parentesco

    response = client.post('/parentescos/asignar', data={
        'id_vecino': v1_id,
        'id_relacionado': v2_id,
        'id_parentesco': p_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Relaci\xc3\xb3n establecida' in response.data

    with app.app_context():
        rel = VecinoParentesco.query.filter_by(
            id_vecino=v1_id,
            id_relacionado=v2_id,
            id_parentesco=p_id
        ).first()
        assert rel is not None
        assert rel.vecino_origen.nombres == 'Mario'
        assert rel.vecino_relacionado.nombres == 'Mateo'
        assert rel.parentesco.nombre == 'Padre'


def test_no_asignar_parentesco_consigo_mismo(client, app):
    """Verifica que un vecino no pueda asignarse como familiar de sí mismo."""
    _login_as_admin(client, app)

    with app.app_context():
        v = Vecino(nombres='Lucas', apellidos='Perez')
        p = Parentesco.query.filter_by(nombre='Hijo').first()
        db.session.add(v)
        db.session.commit()
        v_id = v.id_vecino
        p_id = p.id_parentesco

    response = client.post('/parentescos/asignar', data={
        'id_vecino': v_id,
        'id_relacionado': v_id,
        'id_parentesco': p_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'No se puede asignar una relaci\xc3\xb3n de parentesco de una persona consigo misma' in response.data

    with app.app_context():
        rel = VecinoParentesco.query.filter_by(id_vecino=v_id, id_relacionado=v_id).first()
        assert rel is None


def test_eliminar_parentesco(client, app):
    """Verifica la eliminación de una relación de parentesco."""
    _login_as_admin(client, app)

    with app.app_context():
        v1 = Vecino(nombres='Elena', apellidos='Ruiz')
        v2 = Vecino(nombres='Sofia', apellidos='Ruiz')
        p = Parentesco.query.filter_by(nombre='Madre').first()
        db.session.add_all([v1, v2])
        db.session.commit()

        rel = VecinoParentesco(
            id_vecino=v1.id_vecino,
            id_relacionado=v2.id_vecino,
            id_parentesco=p.id_parentesco
        )
        db.session.add(rel)
        db.session.commit()

        v1_id = v1.id_vecino
        v2_id = v2.id_vecino
        p_id = p.id_parentesco

    response = client.post('/parentescos/eliminar', data={
        'id_vecino': v1_id,
        'id_relacionado': v2_id,
        'id_parentesco': p_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'eliminada correctamente' in response.data

    with app.app_context():
        assert VecinoParentesco.query.filter_by(
            id_vecino=v1_id,
            id_relacionado=v2_id,
            id_parentesco=p_id
        ).first() is None
