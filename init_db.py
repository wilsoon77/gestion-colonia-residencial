import os
from app import create_app, db
from app.models.auth import Rol, Usuario
from app.models.residencia import Parentesco


def init_database():
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    with app.app_context():
        print("Creando tablas en la base de datos...")
        db.create_all()

        print("Verificando roles iniciales...")
        roles_iniciales = [
            'Administrador',
            'Administrador de Colonia',
            'Usuario de Consulta'
        ]
        for nombre_rol in roles_iniciales:
            if not Rol.query.filter_by(nombre=nombre_rol).first():
                db.session.add(Rol(nombre=nombre_rol))
                print(f" -> Rol '{nombre_rol}' creado.")

        print("Verificando catálogo de parentescos...")
        parentescos_iniciales = [
            'Padre',
            'Madre',
            'Hijo',
            'Hija',
            'Cónyuge',
            'Encargado',
            'Hermano(a)',
            'Otro'
        ]
        for nombre_parentesco in parentescos_iniciales:
            if not Parentesco.query.filter_by(nombre=nombre_parentesco).first():
                db.session.add(Parentesco(nombre=nombre_parentesco))
                print(f" -> Parentesco '{nombre_parentesco}' creado.")

        db.session.commit()

        print("Verificando usuario administrador por defecto...")
        admin_rol = Rol.query.filter_by(nombre='Administrador').first()
        usuario_admin = Usuario.query.filter_by(usuario='admin').first()
        if not usuario_admin:
            admin_user = Usuario(
                usuario='admin',
                id_rol=admin_rol.id_rol,
                estado='Activo'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print(" -> Usuario 'admin' (password: admin123) creado exitosamente.")
        else:
            # Asegurar que la contraseña esté actualizada con el hash correcto
            usuario_admin.set_password('admin123')
            usuario_admin.estado = 'Activo'
            db.session.commit()
            print(" -> Contraseña del usuario 'admin' (admin123) actualizada y verificada.")

        print("\n¡Base de datos inicializada y poblada con éxito!")


if __name__ == '__main__':
    init_database()
