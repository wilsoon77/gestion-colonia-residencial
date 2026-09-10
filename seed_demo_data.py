import os
from decimal import Decimal
from datetime import date, timedelta
from app import create_app, db
from app.models.auth import Rol, Usuario
from app.models.residencia import Casa, Familia, Vecino, Parentesco, VecinoParentesco
from app.models.finanzas import Deuda, Multa


def seed_data():
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    with app.app_context():
        print("Iniciando inserción de datos de prueba en la base de datos...")

        # 1. Asegurar Roles
        roles_dict = {}
        for r_name in ['Administrador', 'Administrador de Colonia', 'Usuario de Consulta']:
            rol = Rol.query.filter_by(nombre=r_name).first()
            if not rol:
                rol = Rol(nombre=r_name)
                db.session.add(rol)
                db.session.flush()
            roles_dict[r_name] = rol

        # 2. Asegurar Catálogo de Parentescos
        parentescos_dict = {}
        for p_name in ['Padre', 'Madre', 'Hijo', 'Hija', 'Cónyuge', 'Encargado', 'Hermano(a)', 'Otro']:
            p = Parentesco.query.filter_by(nombre=p_name).first()
            if not p:
                p = Parentesco(nombre=p_name)
                db.session.add(p)
                db.session.flush()
            parentescos_dict[p_name] = p

        # 3. Casas de Prueba
        casas_data = [
            {'numero_casa': '101-A', 'manzana': 'Mz 1', 'calle_avenida': 'Calle Los Pinos', 'estado': 'Ocupada'},
            {'numero_casa': '102-B', 'manzana': 'Mz 1', 'calle_avenida': 'Calle Los Pinos', 'estado': 'Ocupada'},
            {'numero_casa': '103-C', 'manzana': 'Mz 1', 'calle_avenida': 'Calle Los Pinos', 'estado': 'Desocupada'},
            {'numero_casa': '201-A', 'manzana': 'Mz 2', 'calle_avenida': 'Avenida Las Flores', 'estado': 'Ocupada'},
            {'numero_casa': '202-B', 'manzana': 'Mz 2', 'calle_avenida': 'Avenida Las Flores', 'estado': 'En Construcción'},
            {'numero_casa': '301-A', 'manzana': 'Mz 3', 'calle_avenida': 'Boulevard Central', 'estado': 'Ocupada'},
            {'numero_casa': '302-B', 'manzana': 'Mz 3', 'calle_avenida': 'Boulevard Central', 'estado': 'Ocupada'},
            {'numero_casa': '401-A', 'manzana': 'Mz 4', 'calle_avenida': 'Callejón El Roble', 'estado': 'Mantenimiento'},
        ]

        casas_dict = {}
        for c_data in casas_data:
            casa = Casa.query.filter_by(numero_casa=c_data['numero_casa']).first()
            if not casa:
                casa = Casa(**c_data)
                db.session.add(casa)
                db.session.flush()
            casas_dict[c_data['numero_casa']] = casa

        # 4. Familias de Prueba
        familias_data = [
            'Familia Gómez Estrada',
            'Familia Morales Castillo',
            'Familia Rodríguez Marroquín',
            'Familia Álvarez Soto'
        ]

        familias_dict = {}
        for f_name in familias_data:
            fam = Familia.query.filter_by(nombre=f_name).first()
            if not fam:
                fam = Familia(nombre=f_name)
                db.session.add(fam)
                db.session.flush()
            familias_dict[f_name] = fam

        # 5. Vecinos (Residentes)
        vecinos_data = [
            # Familia Gómez Estrada (Casa 101-A)
            {
                'key': 'carlos_gomez',
                'nombres': 'Carlos Roberto',
                'apellidos': 'Gómez Méndez',
                'telefono': '5521-1101',
                'correo': 'carlos.gomez@colonia.com',
                'casa': casas_dict['101-A'],
                'familia': familias_dict['Familia Gómez Estrada']
            },
            {
                'key': 'laura_estrada',
                'nombres': 'Laura Patricia',
                'apellidos': 'Estrada de Gómez',
                'telefono': '5521-1102',
                'correo': 'laura.estrada@colonia.com',
                'casa': casas_dict['101-A'],
                'familia': familias_dict['Familia Gómez Estrada']
            },
            {
                'key': 'mateo_gomez',
                'nombres': 'Mateo',
                'apellidos': 'Gómez Estrada',
                'telefono': None,
                'correo': None,
                'casa': casas_dict['101-A'],
                'familia': familias_dict['Familia Gómez Estrada']
            },
            {
                'key': 'sofia_gomez',
                'nombres': 'Sofía',
                'apellidos': 'Gómez Estrada',
                'telefono': None,
                'correo': None,
                'casa': casas_dict['101-A'],
                'familia': familias_dict['Familia Gómez Estrada']
            },
            # Familia Morales Castillo (Casa 102-B)
            {
                'key': 'fernando_morales',
                'nombres': 'Fernando José',
                'apellidos': 'Morales Santos',
                'telefono': '5532-2201',
                'correo': 'fernando.morales@colonia.com',
                'casa': casas_dict['102-B'],
                'familia': familias_dict['Familia Morales Castillo']
            },
            {
                'key': 'maria_castillo',
                'nombres': 'María Elena',
                'apellidos': 'Castillo de Morales',
                'telefono': '5532-2202',
                'correo': 'maria.castillo@colonia.com',
                'casa': casas_dict['102-B'],
                'familia': familias_dict['Familia Morales Castillo']
            },
            {
                'key': 'diego_morales',
                'nombres': 'Diego',
                'apellidos': 'Morales Castillo',
                'telefono': '5532-2203',
                'correo': 'diego.morales@colonia.com',
                'casa': casas_dict['102-B'],
                'familia': familias_dict['Familia Morales Castillo']
            },
            # Familia Rodríguez Marroquín (Casa 201-A)
            {
                'key': 'ricardo_rodriguez',
                'nombres': 'Ricardo Alberto',
                'apellidos': 'Rodríguez Fuentes',
                'telefono': '5543-3301',
                'correo': 'ricardo.rodriguez@colonia.com',
                'casa': casas_dict['201-A'],
                'familia': familias_dict['Familia Rodríguez Marroquín']
            },
            {
                'key': 'ana_marroquin',
                'nombres': 'Ana Lucía',
                'apellidos': 'Marroquín de Rodríguez',
                'telefono': '5543-3302',
                'correo': 'ana.marroquin@colonia.com',
                'casa': casas_dict['201-A'],
                'familia': familias_dict['Familia Rodríguez Marroquín']
            },
            {
                'key': 'valeria_rodriguez',
                'nombres': 'Valeria',
                'apellidos': 'Rodríguez Marroquín',
                'telefono': None,
                'correo': None,
                'casa': casas_dict['201-A'],
                'familia': familias_dict['Familia Rodríguez Marroquín']
            },
            # Familia Álvarez Soto (Casa 301-A)
            {
                'key': 'hector_alvarez',
                'nombres': 'Héctor Manuel',
                'apellidos': 'Álvarez Lima',
                'telefono': '5554-4401',
                'correo': 'hector.alvarez@colonia.com',
                'casa': casas_dict['301-A'],
                'familia': familias_dict['Familia Álvarez Soto']
            },
            {
                'key': 'carmen_soto',
                'nombres': 'Carmen Elisa',
                'apellidos': 'Soto de Álvarez',
                'telefono': '5554-4402',
                'correo': 'carmen.soto@colonia.com',
                'casa': casas_dict['301-A'],
                'familia': familias_dict['Familia Álvarez Soto']
            },
            # Propietaria Independiente (Casa 302-B)
            {
                'key': 'gabriela_ramos',
                'nombres': 'Gabriela Patricia',
                'apellidos': 'Ramos Pineda',
                'telefono': '5565-5501',
                'correo': 'gabriela.ramos@colonia.com',
                'casa': casas_dict['302-B'],
                'familia': None
            }
        ]

        vecinos_dict = {}
        for v_item in vecinos_data:
            vecino = Vecino.query.filter_by(
                nombres=v_item['nombres'],
                apellidos=v_item['apellidos']
            ).first()
            if not vecino:
                vecino = Vecino(
                    nombres=v_item['nombres'],
                    apellidos=v_item['apellidos'],
                    telefono=v_item['telefono'],
                    correo=v_item['correo'],
                    id_casa=v_item['casa'].id_casa if v_item['casa'] else None,
                    id_familia=v_item['familia'].id_familia if v_item['familia'] else None
                )
                db.session.add(vecino)
                db.session.flush()
            vecinos_dict[v_item['key']] = vecino

        # 6. Relaciones de Parentesco
        relaciones_data = [
            (vecinos_dict['carlos_gomez'], vecinos_dict['mateo_gomez'], parentescos_dict['Padre']),
            (vecinos_dict['carlos_gomez'], vecinos_dict['sofia_gomez'], parentescos_dict['Padre']),
            (vecinos_dict['laura_estrada'], vecinos_dict['mateo_gomez'], parentescos_dict['Madre']),
            (vecinos_dict['laura_estrada'], vecinos_dict['sofia_gomez'], parentescos_dict['Madre']),
            (vecinos_dict['carlos_gomez'], vecinos_dict['laura_estrada'], parentescos_dict['Cónyuge']),
            (vecinos_dict['mateo_gomez'], vecinos_dict['sofia_gomez'], parentescos_dict['Hermano(a)']),

            (vecinos_dict['fernando_morales'], vecinos_dict['diego_morales'], parentescos_dict['Padre']),
            (vecinos_dict['maria_castillo'], vecinos_dict['diego_morales'], parentescos_dict['Madre']),
            (vecinos_dict['fernando_morales'], vecinos_dict['maria_castillo'], parentescos_dict['Cónyuge']),

            (vecinos_dict['ricardo_rodriguez'], vecinos_dict['valeria_rodriguez'], parentescos_dict['Padre']),
            (vecinos_dict['ana_marroquin'], vecinos_dict['valeria_rodriguez'], parentescos_dict['Madre']),
            (vecinos_dict['ricardo_rodriguez'], vecinos_dict['ana_marroquin'], parentescos_dict['Cónyuge']),

            (vecinos_dict['hector_alvarez'], vecinos_dict['carmen_soto'], parentescos_dict['Cónyuge']),
        ]

        for v_orig, v_rel, p_tipo in relaciones_data:
            rel_exist = VecinoParentesco.query.filter_by(
                id_vecino=v_orig.id_vecino,
                id_relacionado=v_rel.id_vecino,
                id_parentesco=p_tipo.id_parentesco
            ).first()
            if not rel_exist:
                nueva_rel = VecinoParentesco(
                    id_vecino=v_orig.id_vecino,
                    id_relacionado=v_rel.id_vecino,
                    id_parentesco=p_tipo.id_parentesco
                )
                db.session.add(nueva_rel)

        # 7. Usuarios del Sistema
        usuarios_data = [
            {'usuario': 'admin', 'pass': 'admin123', 'rol': roles_dict['Administrador'], 'vecino': None},
            {'usuario': 'admin_colonia', 'pass': 'colonia123', 'rol': roles_dict['Administrador de Colonia'], 'vecino': None},
            {'usuario': 'carlos_gomez', 'pass': 'vecino123', 'rol': roles_dict['Usuario de Consulta'], 'vecino': vecinos_dict['carlos_gomez']},
            {'usuario': 'maria_castillo', 'pass': 'vecino123', 'rol': roles_dict['Usuario de Consulta'], 'vecino': vecinos_dict['maria_castillo']},
        ]

        for u_item in usuarios_data:
            usr = Usuario.query.filter_by(usuario=u_item['usuario']).first()
            if not usr:
                usr = Usuario(
                    usuario=u_item['usuario'],
                    id_rol=u_item['rol'].id_rol,
                    id_vecino=u_item['vecino'].id_vecino if u_item['vecino'] else None,
                    estado='Activo'
                )
                usr.set_password(u_item['pass'])
                db.session.add(usr)
            else:
                usr.set_password(u_item['pass'])
                usr.estado = 'Activo'

        # 8. Deudas de Prueba
        hoy = date.today()
        hace_un_mes = hoy - timedelta(days=30)
        hace_dos_meses = hoy - timedelta(days=60)

        deudas_data = [
            {'vecino': vecinos_dict['carlos_gomez'], 'concepto': 'Cuota Mantenimiento y Seguridad - Agosto 2026', 'monto': Decimal('250.00'), 'fecha': hoy, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['carlos_gomez'], 'concepto': 'Cuota Mantenimiento y Seguridad - Julio 2026', 'monto': Decimal('250.00'), 'fecha': hace_un_mes, 'estado': 'Pagada'},
            {'vecino': vecinos_dict['fernando_morales'], 'concepto': 'Cuota Mantenimiento y Seguridad - Agosto 2026', 'monto': Decimal('250.00'), 'fecha': hoy, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['fernando_morales'], 'concepto': 'Servicio Extra de Agua Potable', 'monto': Decimal('125.50'), 'fecha': hace_un_mes, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['ricardo_rodriguez'], 'concepto': 'Cuota Mantenimiento y Seguridad - Agosto 2026', 'monto': Decimal('250.00'), 'fecha': hoy, 'estado': 'Pagada'},
            {'vecino': vecinos_dict['ricardo_rodriguez'], 'concepto': 'Extracción Extraordinaria de Desechos', 'monto': Decimal('75.00'), 'fecha': hace_dos_meses, 'estado': 'Pagada'},
            {'vecino': vecinos_dict['hector_alvarez'], 'concepto': 'Cuota Mantenimiento y Seguridad - Agosto 2026', 'monto': Decimal('250.00'), 'fecha': hoy, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['hector_alvarez'], 'concepto': 'Aporte Proyecto Pavimentación Calle Principal', 'monto': Decimal('500.00'), 'fecha': hace_un_mes, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['gabriela_ramos'], 'concepto': 'Cuota Mantenimiento y Seguridad - Agosto 2026', 'monto': Decimal('250.00'), 'fecha': hoy, 'estado': 'Pagada'},
        ]

        for d_item in deudas_data:
            d_exist = Deuda.query.filter_by(
                id_vecino=d_item['vecino'].id_vecino,
                concepto=d_item['concepto']
            ).first()
            if not d_exist:
                nueva_deuda = Deuda(
                    id_vecino=d_item['vecino'].id_vecino,
                    concepto=d_item['concepto'],
                    monto=d_item['monto'],
                    fecha=d_item['fecha'],
                    estado=d_item['estado']
                )
                db.session.add(nueva_deuda)

        # 9. Multas de Prueba
        multas_data = [
            {'vecino': vecinos_dict['carlos_gomez'], 'motivo': 'Música a alto volumen después de medianoche en fin de semana', 'monto': Decimal('150.00'), 'fecha': hace_dos_meses, 'estado': 'Pagada'},
            {'vecino': vecinos_dict['fernando_morales'], 'motivo': 'Mascota suelta sin correa en áreas comunes y jardines', 'monto': Decimal('100.00'), 'fecha': hace_un_mes, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['ricardo_rodriguez'], 'motivo': 'Estacionamiento indebido obstruyendo paso peatonal y rampa', 'monto': Decimal('200.00'), 'fecha': hoy, 'estado': 'Pendiente'},
            {'vecino': vecinos_dict['hector_alvarez'], 'motivo': 'Depósito no autorizado de escombros de remodelación en la vía pública', 'monto': Decimal('150.00'), 'fecha': hace_un_mes, 'estado': 'Exonerada'},
        ]

        for m_item in multas_data:
            m_exist = Multa.query.filter_by(
                id_vecino=m_item['vecino'].id_vecino,
                motivo=m_item['motivo']
            ).first()
            if not m_exist:
                nueva_multa = Multa(
                    id_vecino=m_item['vecino'].id_vecino,
                    motivo=m_item['motivo'],
                    monto=m_item['monto'],
                    fecha=m_item['fecha'],
                    estado=m_item['estado']
                )
                db.session.add(nueva_multa)

        db.session.commit()
        print("Datos de prueba insertados y confirmados con éxito en la base de datos!")


if __name__ == '__main__':
    seed_data()
