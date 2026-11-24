"""VALIDADOR PRODUCTIVO R3 (S2/S3) bajo S6 (candidato; NO OFICIAL). Reutiliza SIN CAMBIOS las comprobaciones del validador histórico de los
lotes R3 (codigo/validar_detallado.py de lima1533, sha256 871b1d7f…, copiado byte a byte como validar_detallado_lima1533.py):
procedencia de la definición, IDENTIDAD por contenido (ω reconstruido desde el prefijo L0 o la tarea, regla B de vértice y de estado,
celda externa de la grilla autenticada, ids recalculados con las fórmulas del núcleo, claves estructural y macro con su carga y las HUELLAS
TÉCNICAS del contexto), NÚMEROS (λ_π desde el estado nacional, K_comp_1, C_2 de techo y confrontación, G, veredicto, techo complete con
error <= 1e-7), EVIDENCIAS (fila de G recalculada, R1/INV coherentes, E12 re-verificada con e12_celda, ruta no aplicable) y ESQUEMA del
contrato v3, más el checker del núcleo con los contratos del contexto.
Único cambio: el contexto. El histórico construía ContextoS5 en __init__; aquí se INYECTAN el ContextoS6 y la Referencia ya autenticados
(la MISMA identidad inmutable con la que produjo el trabajador), y regla_b_v2 / e12_celda fijados por sha256 desde la raíz S6.
No calcula techos ni celdas: reconstruye identidad y relaciones (Runs de prefijo, estados, grilla) y verifica lo producido.
  VR = ValidadorR3S6(ctx, ref, SP, raiz_proyecto); VR.celda(definicion, doc, filas, contrato_exigido="v3") -> {clasificacion, motivos, ...}
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HISTORICO = ("validar_detallado_lima1533.py", "871b1d7f2923c2aa7ca2dbe9dfaf3b9eeb36debad02ee3c40fceee10bb840c2c")


def _historico():
    p = AQUI / HISTORICO[0]
    if hashlib.sha256(p.read_bytes()).hexdigest() != HISTORICO[1]:
        raise RuntimeError("VALIDADOR_HISTORICO_DISTINTO_DEL_FIJADO")
    if "vd_lima1533" not in sys.modules:
        sp = importlib.util.spec_from_file_location("vd_lima1533", p)
        m = importlib.util.module_from_spec(sp)
        sys.modules["vd_lima1533"] = m
        sp.loader.exec_module(m)
    return sys.modules["vd_lima1533"]


VD = _historico()


class ValidadorR3S6(VD.Validador):
    """Validador histórico con el contexto S6 INYECTADO (réplica exacta de Validador.__init__ salvo la construcción de ContextoS5)."""

    def __init__(self, ctx, ref, SP, raiz_proyecto):
        sys.path.insert(0, str(AQUI))
        import productor_r3 as PR
        _ = PR.ProductorR3(ctx, ref, SP.GC, raiz_proyecto)          # carga y exige el sha256 de regla_b_v2 y e12_celda de la raíz S6
        self.ctx, self.ref, self.t_ctx, self.t_ref = ctx, ref, 0.0, 0.0
        self.SP, self.GC = SP, SP.GC
        self.CE = SP.GC.CE
        self.RB, self.E12 = sys.modules["r3_regla_b_v2"], sys.modules["r3_e12_celda"]
        from paper2b import claves_condicionales as CK
        from paper2b import contrato_paquete as CP
        from paper2b import convergencia as CV
        from paper2b import external as X
        from paper2b import inversion as INV
        from paper2b import keys as K
        from paper2b import macro as MC
        from paper2b import model as M
        from paper2b import run as RUN
        self.CK, self.CV, self.X, self.INV, self.K, self.MC, self.RUN = CK, CV, X, INV, K, MC, RUN
        self.CP, self.M = CP, M
        self.P2 = SP.P2
        self.r1_tol = float(self.ctx.cfg.r1_geometry_tol)
        self.xtol = float(self.ctx.cfg.endogenous_xtol)
        self._estados = {}
        self.gen = self.GC.Generador(self.ctx, self.ref, self.GC.Compartido(activo=False))
        self.runs = {}
        assert abs(float(self.ctx.cfg.sup.tol_converge) - VD.TOL_CONVERGE) == 0.0 and abs(float(CV.T2_G) - VD.T2_G) == 0.0, "TOLERANCIAS"
        self.authority_kind = getattr(ctx.authority, "kind", None)


def identidad():
    """sha256 de este módulo y del histórico (registro productivo y pin del comparador)."""
    return {"modulo": "herramientas/b/validador_r3.py", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "historico": {"archivo": HISTORICO[0],
            "sha256": HISTORICO[1], "procedencia": "remanente_detallado_h4_paso4_3_7_2026-10-10_lima1533/codigo/validar_detallado.py"}}
