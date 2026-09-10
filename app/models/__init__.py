from app.models.auth import Rol, Usuario
from app.models.residencia import Casa, Familia, Vecino, Parentesco, VecinoParentesco, vecino_parentesco
from app.models.finanzas import Deuda, Multa

__all__ = [
    'Rol',
    'Usuario',
    'Casa',
    'Familia',
    'Vecino',
    'Parentesco',
    'VecinoParentesco',
    'vecino_parentesco',
    'Deuda',
    'Multa'
]
