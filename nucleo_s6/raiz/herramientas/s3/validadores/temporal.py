"""Instantes UTC exactos, sin efectos operativos.

Adaptado de _v2_instant, construir_d6.py:1900 del candidato MEX auditado,
SHA-256 fbb3a6df0f595ca36e393a4374f817e6dc506f90e3689613711e378a658facf5.
Se conserva el algoritmo racional; se cambia únicamente la excepción a ContractError.
No importa ni ejecuta el módulo institucional.
"""
from datetime import datetime, timezone
from fractions import Fraction
import re
from .core import ContractError


def instant(value, field='created_at'):
    try:
        if not isinstance(value, str):
            raise ValueError('missing/null/non-string')
        match = re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:[.,](\d+))?(Z|[+-]\d{2}:\d{2})', value)
        if match is None:
            raise ValueError('ISO timestamp with timezone required')
        whole, fraction, zone = match.groups()
        if zone != 'Z' and (int(zone[1:3]) >= 24 or int(zone[4:6]) >= 60):
            raise ValueError('invalid timezone offset')
        stamp = datetime.fromisoformat(whole + zone).astimezone(timezone.utc)
        seconds = stamp.toordinal()*86400 + stamp.hour*3600 + stamp.minute*60 + stamp.second
        return Fraction(seconds) + (Fraction(int(fraction),10**len(fraction)) if fraction else 0)
    except (ValueError,TypeError,OverflowError) as exc:
        raise ContractError('CA2-10 fecha inválida con zona: '+field) from exc
