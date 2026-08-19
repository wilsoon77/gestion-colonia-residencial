import pytest
from app import create_app, db
from app.models.auth import Rol, Usuario

@pytest.fixture
def app():
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        # Sembrar roles iniciales
        rol_admin = Rol(nombre='Administrador')
        rol_admin_col = Rol(nombre='Administrador de Colonia')
        rol_consulta = Rol(nombre='Usuario de Consulta')
        db.session.add_all([rol_admin, rol_admin_col, rol_consulta])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
