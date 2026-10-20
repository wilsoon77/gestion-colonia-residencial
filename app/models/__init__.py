from app.models.auth import Rol, Usuario
from app.models.residencia import Casa, FotoCasa, Familia, Vecino, Parentesco, VecinoParentesco, vecino_parentesco
from app.models.finanzas import Deuda, ComprobanteDeuda, Multa, EvidenciaMulta

__all__ = [
    'Rol',
    'Usuario',
    'Casa',
    'FotoCasa',
    'Familia',
    'Vecino',
    'Parentesco',
    'VecinoParentesco',
    'vecino_parentesco',
    'Deuda',
    'ComprobanteDeuda',
    'Multa',
    'EvidenciaMulta'
]
