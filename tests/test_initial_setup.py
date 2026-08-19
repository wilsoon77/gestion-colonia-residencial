from app.models.auth import Rol, Usuario
from app.models.residencia import Casa, Familia, Vecino, Parentesco
from app.models.finanzas import Deuda, Multa

def test_app_is_testing(app):
    """Verifica que la app se ejecute en modo Testing."""
    assert app.config['TESTING'] is True

def test_roles_creation(app):
    """Verifica que los roles iniciales se creen correctamente."""
    with app.app_context():
        roles = Rol.query.all()
        nombres = [r.nombre for r in roles]
        assert 'Administrador' in nombres
        assert 'Administrador de Colonia' in nombres
        assert 'Usuario de Consulta' in nombres

def test_login_page_loads(client):
    """Verifica que la página de login responda con código 200."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Acceso al Sistema' in response.data

def test_dashboard_redirects_unauthenticated(client):
    """Verifica que el dashboard redirija a login a usuarios no autenticados."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
