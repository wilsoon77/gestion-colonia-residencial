import os
import logging
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_image_file(filename):
    """Verifica si el archivo tiene una extensión de imagen permitida."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def get_cloudinary_config():
    """Obtiene las credenciales de Cloudinary desde la app o variables de entorno."""
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME') or os.getenv('cloudinary.cloud-name')
    api_key = os.getenv('CLOUDINARY_API_KEY') or os.getenv('cloudinary.api-key')
    api_secret = os.getenv('CLOUDINARY_API_SECRET') or os.getenv('cloudinary.api-secret')

    try:
        from flask import current_app
        if current_app:
            cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME') or cloud_name
            api_key = current_app.config.get('CLOUDINARY_API_KEY') or api_key
            api_secret = current_app.config.get('CLOUDINARY_API_SECRET') or api_secret
    except Exception:
        pass

    return cloud_name, api_key, api_secret


def is_cloudinary_configured():
    """Verifica si las credenciales de Cloudinary están completas."""
    cloud_name, api_key, api_secret = get_cloudinary_config()
    return bool(cloud_name and api_key and api_secret)


def configure_cloudinary():
    """Configura el cliente global de Cloudinary."""
    cloud_name, api_key, api_secret = get_cloudinary_config()
    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        return True
    return False


def subir_imagen(file_storage, folder='residencial/multas'):
    """Sube un archivo de imagen (FileStorage) a Cloudinary.

    Retorna un diccionario con:
        - url: URL pública segura de la imagen.
        - public_id: Identificador en Cloudinary para gestión posterior.
        - nombre_archivo: Nombre sanitizado original del archivo.
    O None si ocurre un error o el archivo no es válido.
    """
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    if not allowed_image_file(filename):
        logger.warning(f"Extensión no permitida para el archivo: {filename}")
        return None

    if not configure_cloudinary():
        logger.error("Cloudinary no está configurado correctamente con credenciales válidas.")
        return None

    try:
        # Asegurar puntero al inicio si ya fue leído
        if hasattr(file_storage, 'seek'):
            file_storage.seek(0)

        upload_result = cloudinary.uploader.upload(
            file_storage,
            folder=folder,
            resource_type='image'
        )

        return {
            'url': upload_result.get('secure_url') or upload_result.get('url'),
            'public_id': upload_result.get('public_id'),
            'nombre_archivo': filename,
            'formato': upload_result.get('format'),
            'bytes': upload_result.get('bytes')
        }
    except Exception as e:
        logger.error(f"Error al subir imagen a Cloudinary ({filename}): {e}", exc_info=True)
        return None


def eliminar_imagen(public_id):
    """Elimina una imagen de Cloudinary usando su public_id.

    Retorna True si fue eliminada exitosamente, False en caso contrario.
    """
    if not public_id:
        return False

    if not configure_cloudinary():
        logger.error("Cloudinary no está configurado para eliminar imagen.")
        return False

    try:
        result = cloudinary.uploader.destroy(public_id, resource_type='image')
        return result.get('result') in ['ok', 'not found']
    except Exception as e:
        logger.error(f"Error al eliminar imagen de Cloudinary ({public_id}): {e}", exc_info=True)
        return False
