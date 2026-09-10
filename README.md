# Sistema Web para la Gestión Administrativa de una Colonia Residencial

**Universidad Mariano Gálvez de Guatemala**  
**Facultad de Ingeniería en Sistemas de Información y Ciencias de la Computación**  
**Curso:** Aseguramiento de la Calidad de Software (10° Ciclo)

---

## Integrantes del Equipo

* **Wincer Daniel Córdova Marroquín** - 1990-22-8308
* **Daniel Angel Ambrocio Coj** - 1990-22-13443
* **Wilson Adolfo Coc Avila** - 1990-22-1148

---

## Descripción del Proyecto

Aplicación web integral diseñada bajo la metodología **Scrum** para la administración, supervisión y control operativo de una colonia residencial (~500 viviendas), garantizando altos estándares de calidad de software mediante pruebas automatizadas, análisis estático y arquitectura modular.

### Módulos Principales
1. **Control de Acceso y Usuarios (RBAC)**: Autenticación segura y permisos para tres roles: *Administrador*, *Administrador de Colonia* y *Usuario de Consulta*.
2. **Gestión de Viviendas (Casas)**: Registro de números de casa, manzanas, calles/avenidas y estados de ocupación (*Ocupada, Desocupada, En Construcción, Mantenimiento*).
3. **Gestión de Residentes (Vecinos)**: Directorio con vinculación a vivienda, familia, datos de contacto e historial de deudas y sanciones.
4. **Gestión de Familias**: Organización de grupos familiares y visualización de sus integrantes.
5. **Relaciones Familiares (Parentescos)**: Catálogo y asignación de vínculos de parentesco (Padre, Madre, Hijo, Hija, Encargado, Cónyuge, etc.) con validaciones de negocio.
6. **Control Financiero de Deudas**: Emisión, cálculo de balances financieros en Quetzales (`DECIMAL(10,2)`) y liquidación de cuotas de mantenimiento y servicios.
7. **Control de Sanciones (Multas)**: Aplicación, cobro y exoneración de multas por infracciones residenciales.
8. **Dashboard Administrativo**: Panel interactivo con métricas en tiempo real (KPIs) y accesos rápidos.

---

## Stack Tecnológico

* **Lenguaje Principal:** Python 3.10+
* **Framework Web:** Flask (Arquitectura modular basada en *Application Factory* y *Blueprints*)
* **Base de Datos:** PostgreSQL en la nube (**Neon Serverless PostgreSQL**, BD: `colonia`)
* **ORM:** SQLAlchemy (tablas y modelos estructurados en singular)
* **Frontend:** HTML5, CSS3, Bootstrap 5.3 y Bootstrap Icons (diseño formal sin emojis genéricos)
* **Seguridad:** Flask-Login, Flask-WTF (Protección contra ataques CSRF) y hashing criptográfico de contraseñas (`Werkzeug/scrypt`)
* **Aseguramiento de Calidad (QA):** pytest (37 pruebas unitarias, de integración y E2E), Flake8 (PEP 8) y GitHub Actions CI

---

## Estructura del Proyecto

```text
proyecto-colonia/
├── .github/
│   └── workflows/
│       └── tests.yml          # Pipeline de Integración Continua (CI con GitHub Actions)
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Exclusiones de Git (venv, pycache, .env, etc.)
├── README.md                  # Documentación principal del sistema
├── requirements.txt           # Dependencias de Python
├── run.py                     # Punto de entrada de la aplicación Flask
├── init_db.py                 # Script de inicialización y migración en Neon
├── iniciar_sistema.bat        # Lanzador automático de Windows (doble clic)
├── Plan/
│   └── plan.md                # Documento original de planificación Scrum
├── app/
│   ├── __init__.py            # Application Factory y manejadores de error (403, 404, 500)
│   ├── config.py              # Configuraciones de entorno (Development, Testing, Production)
│   ├── models/                # Modelos ORM SQLAlchemy en singular
│   │   ├── __init__.py
│   │   ├── auth.py            # Modelos Rol y Usuario
│   │   ├── residencia.py      # Modelos Casa, Familia, Vecino, Parentesco y VecinoParentesco
│   │   └── finanzas.py        # Modelos Deuda y Multa con DECIMAL(10,2)
│   ├── routes/                # Controladores modulares (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py            # Login y Logout
│   │   ├── dashboard.py       # Panel de control y métricas
│   │   ├── usuarios.py        # Administración de cuentas y roles (RBAC)
│   │   ├── casas.py           # CRUD y fichas técnicas de viviendas
│   │   ├── familias.py        # CRUD y fichas de núcleos familiares
│   │   ├── vecinos.py         # CRUD y fichas individuales de residentes
│   │   ├── parentescos.py     # Catálogo y asignación de parentescos
│   │   ├── deudas.py          # Control financiero y cobros
│   │   └── multas.py          # Control de sanciones e infracciones
│   ├── utils/
│   │   ├── __init__.py
│   │   └── decorators.py      # Decoradores de seguridad (@role_required, @admin_required)
│   ├── templates/             # Plantillas Jinja2 y Bootstrap 5
│   │   ├── base.html          # Layout principal con navbar y alertas
│   │   ├── auth/              # Vistas de autenticación y gestión de usuarios
│   │   ├── dashboard/         # Vista del panel de control
│   │   ├── casas/             # Vistas de casas
│   │   ├── familias/          # Vistas de familias
│   │   ├── vecinos/           # Vistas de vecinos
│   │   ├── parentescos/       # Vistas de catálogo de parentescos
│   │   ├── deudas/            # Vistas de deudas
│   │   ├── multas/            # Vistas de multas
│   │   └── errors/            # Páginas de error personalizadas (403, 404, 500)
│   └── static/
│       ├── css/style.css      # Estilos CSS personalizados
│       └── js/main.js         # Scripts frontend
└── tests/                     # Suite completa de pruebas de QA
    ├── __init__.py
    ├── conftest.py            # Fixtures de Pytest con base de datos en memoria
    ├── test_auth.py           # Pruebas de autenticación y sesiones
    ├── test_rbac.py           # Pruebas de permisos y control de acceso
    ├── test_usuarios.py       # Pruebas de CRUD de usuarios y contraseñas
    ├── test_casas.py          # Pruebas de viviendas
    ├── test_familias.py       # Pruebas de familias
    ├── test_vecinos.py        # Pruebas de residentes
    ├── test_parentescos.py    # Pruebas de parentescos y vinculación familiar
    ├── test_deudas.py         # Pruebas de cobros y balances financieros
    ├── test_multas.py         # Pruebas de sanciones
    ├── test_flujo_completo.py # Prueba de Integración End-to-End
    └── test_initial_setup.py  # Pruebas de entorno inicial
```

---

## Ejecución Rápida (Windows)

Para iniciar todo el sistema con un solo clic:
1. Haz doble clic en el archivo **`iniciar_sistema.bat`**.
2. El script configurará el entorno, verificará la base de datos y abrirá tu navegador automáticamente en `http://127.0.0.1:5000`.

---

## Ejecución Manual por Consola

### 1. Crear y activar el entorno virtual
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear el archivo `.env` configurando la cadena de conexión de Neon:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_aqui
DATABASE_URL=postgresql://usuario:password@tu-endpoint.neon.tech/neondb?sslmode=require
```

### 4. Inicializar tablas y datos semilla
```powershell
python init_db.py
```

### 5. Iniciar el servidor web
```powershell
python run.py
```

---

## Credenciales de Acceso

* **Usuario:** `admin`
* **Contraseña:** `admin123`
* **Rol:** `Administrador`

---

## Aseguramiento de la Calidad (QA)

### Ejecutar Pruebas Automatizadas
```powershell
pytest -v
```

### Ejecutar Análisis Estático de Código (Linter PEP 8)
```powershell
flake8 app tests --count --max-line-length=127 --statistics
```
