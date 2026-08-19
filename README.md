# Sistema Web para la Gestión Administrativa de una Colonia Residencial

**Universidad Mariano Gálvez de Guatemala**  
**Facultad de Ingeniería en Sistemas de Información**  
**Curso:** Aseguramiento de la Calidad de Software (10° Ciclo)

---

## 👥 Integrantes del Equipo

* **Wincer Daniel Córdova Marroquín** - 1990-22-8308
* **Daniel Angel Ambrocio Coj** - 1990-22-13443
* **Wilson Adolfo Coc Avila** - 1990-22-1148

---

## 📋 Descripción del Proyecto

Aplicación web diseñada para la administración integral de una colonia residencial (~500 viviendas), facilitando:
* Control de viviendas (manzanas, lotes, calles y números de casa).
* Registro y gestión de vecinos, familias y relaciones de parentesco.
* Control financiero de deudas y registro de multas por residente.
* Control de acceso basado en roles (RBAC: Administrador, Administrador de Colonia, Consulta).

---

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.10+ / Flask
* **Base de Datos:** PostgreSQL / SQLAlchemy ORM
* **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Jinja2
* **Seguridad:** Flask-Login, Flask-WTF (CSRF), Werkzeug Password Hashing
* **Aseguramiento de Calidad (QA):** pytest, Flake8, GitHub Actions CI

---

## 📁 Estructura del Proyecto

```text
proyecto-colonia/
├── app/
│   ├── __init__.py            # Application Factory (create_app)
│   ├── config.py              # Configuraciones por entorno
│   ├── models/                # Modelos de Base de Datos (SQLAlchemy)
│   ├── routes/                # Controladores / Blueprints
│   ├── templates/             # Plantillas Jinja2 / Bootstrap 5
│   └── static/                # Archivos estáticos (CSS, JS, imágenes)
├── tests/                     # Suite de pruebas automatizadas (QA)
├── .github/workflows/         # Pipeline de Integración Continua (CI)
├── .env.example               # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt           # Dependencias de Python
└── run.py                     # Punto de entrada de la aplicación
```

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el repositorio y acceder a la carpeta
```bash
git clone <url-del-repositorio>
cd proyecto-colonia
```

### 2. Crear y activar el entorno virtual
```bash
# En Windows:
python -m venv venv
venv\Scripts\activate

# En Linux/macOS:
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar el archivo `.env.example` a `.env` y configurar las credenciales de PostgreSQL:
```bash
copy .env.example .env
```

### 5. Ejecutar la aplicación
```bash
python run.py
```
La aplicación estará disponible en `http://127.0.0.1:5000`.

### 6. Ejecutar pruebas automatizadas (QA)
```bash
pytest
```
