"""Perfil de DESARROLLO explícito del presupuesto por inversión (bloque 2, subpaso 2.6).

`config()` devuelve una RunConfig con inversion_budget_seconds = 10 800 s. Es el valor con el que la inversión completa
phi_total del caso de control (estado V, diseño G, menú df, barras 0.6/0.6, dominio [0, 1], xtol 1e-10) terminó
`computed` con cobertura certificada en 6369.7 s de búsqueda (entrega bloque2_candidato_r1_encierros_phidf_2026-09-29,
logs/phi_df/medicion_xtol1e-10_presupuesto10800.jsonl).

Alcance: reproduce ese caso de DESARROLLO. NO acredita que 10 800 s basten para las inversiones nacionales ni fija el
presupuesto de una corrida oficial: su adecuación a escala se mide en los pilotos del bloque 3 y el valor oficial se
declara (y queda sellado por el freeze-run) antes de cualquier corrida. No cambia tolerancias, dominio ni criterios.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from paper2b import run as RUN  # noqa: E402

NOMBRE = "desarrollo_phi_df_control_10800"
INVERSION_BUDGET_SECONDS = 10800.0
ALCANCE = ("perfil de desarrollo: reproduce la inversión phi_total del caso de control df (6369.7 s con 10 800 s); no "
           "acredita suficiencia para inversiones nacionales (bloque 3)")


def config(**overrides) -> RUN.RunConfig:
    """RunConfig del perfil. El presupuesto por inversión es el del perfil y no se puede sustituir aquí: para otro valor
    se construye una RunConfig explícita (otra configuración, otra identidad)."""
    if "inversion_budget_seconds" in overrides:
        raise ValueError("PERFIL_DESARROLLO_FIJA_EL_PRESUPUESTO_POR_INVERSION")
    return RUN.RunConfig(inversion_budget_seconds=INVERSION_BUDGET_SECONDS, **overrides)


def descriptor() -> dict:
    return {"perfil": NOMBRE, "clase": "desarrollo", "inversion_budget_seconds": INVERSION_BUDGET_SECONDS,
            "alcance": ALCANCE}
