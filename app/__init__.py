from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicialización de extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'

    # Registro de Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.casas import casas_bp
    from app.routes.familias import familias_bp
    from app.routes.vecinos import vecinos_bp
    from app.routes.parentescos import parentescos_bp
    from app.routes.deudas import deudas_bp
    from app.routes.multas import multas_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(casas_bp, url_prefix='/casas')
    app.register_blueprint(familias_bp, url_prefix='/familias')
    app.register_blueprint(vecinos_bp, url_prefix='/vecinos')
    app.register_blueprint(parentescos_bp, url_prefix='/parentescos')
    app.register_blueprint(deudas_bp, url_prefix='/deudas')
    app.register_blueprint(multas_bp, url_prefix='/multas')

    # Manejadores de errores HTTP
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
