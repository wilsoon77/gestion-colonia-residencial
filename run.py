import os
import threading
import webbrowser
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Abre el navegador automáticamente al iniciar (solo en el proceso principal)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.2, open_browser).start()
    app.run(debug=True, host='0.0.0.0', port=5000)
