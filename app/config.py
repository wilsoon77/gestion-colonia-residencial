import os
from dotenv import load_dotenv

load_dotenv()

raw_db_url = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/colonia'
)
if raw_db_url and raw_db_url.startswith('postgres://'):
    raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-colonia-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = raw_db_url

    # Cloudinary Storage Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME') or os.getenv('cloudinary.cloud-name')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY') or os.getenv('cloudinary.api-key')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET') or os.getenv('cloudinary.api-secret')

    # Uploads limit (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
