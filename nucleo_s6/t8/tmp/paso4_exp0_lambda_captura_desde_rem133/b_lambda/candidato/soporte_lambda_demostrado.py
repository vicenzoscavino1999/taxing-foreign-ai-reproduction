"""rem133 — CANDIDATO AISLADO (no incorporado): SOPORTE λ DERIVADO POR DEMOSTRACIÓN. No modifica soporte_global.py ni su contrato.
- No fabrica resúmenes de unidades: plan_unidades no se enumera como ejecutado; el documento declara run_id, plan_sha256 y las FUENTES de la demostración.
- C2 en tres estados explícitos: «no_evaluado» (único admitido aquí), «vacio_demostrado» y «con_soporte» (solo por la ruta global vigente).
- cerrar_lambda finaliza SOLO filas lambda_required provisionales con clave demostrada; las de captura y las demás vuelven SIN cambios.
Criterio de cierre: el de unidades._finalize (se inyecta). Diferencial frente a la ruta vigente: respaldo nuevo «derivado_por_demostracion»."""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction

ESQUEMA = "soporte-lambda-derivado-por-demostracion-v1"
C2_ESTADOS = ("no_evaluado", "vacio_demostrado", "con_soporte")


class SoporteLambdaError(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo = codigo


def need(t, c, d=""):
    if not t:
        raise SoporteLambdaError(c, d)


def _sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def claves_demostradas(eq, b1):
    """Claves con TODAS las premisas: E1–E3 de la equivalencia (rem132) y universo nacional igual (B1, rem133)."""
    out = {}
    for k, r in eq["por_clave"].items():
        u = b1["claves"].get(k, {})
        if r.get("E1_cubierta_y_alcanzada") and r.get("E2_dominio_igual_a_D7") and r.get("E3_testigos_en_reticula_L0") and u.get("universo_igual") is True:
            e = r["envolvente"]
            out[k] = [float(Fraction(e["lambda_min"])), float(Fraction(e["lambda_max"]))]
    return dict(sorted(out.items()))


def construir(eq, b1, *, run_id, plan_sha256, fuentes):
    need(isinstance(run_id, str) and run_id.startswith("BRUN-"), "RUN_ID")
    need(isinstance(plan_sha256, str) and len(plan_sha256) == 64, "PLAN_SHA256")
    need(isinstance(fuentes, dict) and fuentes and all(isinstance(v, str) and len(v) == 64 for v in fuentes.values()), "FUENTES")
    lam = claves_demostradas(eq, b1)
    need(lam, "SIN_CLAVES_DEMOSTRADAS")
    doc = {"esquema": ESQUEMA, "respaldo": "derivado_por_demostracion", "run_id": run_id, "plan_sha256": plan_sha256, "plan_unidades": None,
           "unidades_ejecutadas": None, "lambda": lam, "c2": None, "c2_estado": "no_evaluado", "fuentes": dict(sorted(fuentes.items()))}
    doc["sha256"] = _sha(doc)
    return doc


def validar(doc, eq, b1, *, run_id, plan_sha256, fuentes):
    need(isinstance(doc, dict) and doc.get("esquema") == ESQUEMA and doc.get("respaldo") == "derivado_por_demostracion", "ESQUEMA")
    need(doc.get("c2_estado") in C2_ESTADOS, "C2_ESTADO_DESCONOCIDO")
    need(doc.get("c2_estado") == "no_evaluado" and doc.get("c2") is None, "PROMOCION_C2_NO_EVALUADO", doc.get("c2_estado"))
    need(doc.get("plan_unidades") is None and doc.get("unidades_ejecutadas") is None, "UNIDADES_FABRICADAS")
    need(doc.get("run_id") == run_id, "RUN_DISTINTO", doc.get("run_id"))
    need(doc.get("plan_sha256") == plan_sha256, "PLAN_DISTINTO")
    need(doc.get("fuentes") == dict(sorted(fuentes.items())), "FUENTES_DISTINTAS")
    esperado = construir(eq, b1, run_id=run_id, plan_sha256=plan_sha256, fuentes=fuentes)
    need(json.loads(json.dumps(doc, sort_keys=True)) == json.loads(json.dumps(esperado, sort_keys=True)), "NO_DERIVADO", str(doc.get("sha256"))[:16])
    return esperado


def cerrar_lambda(filas, doc, finalizar, eq, b1, *, run_id, plan_sha256, fuentes):
    s = validar(doc, eq, b1, run_id=run_id, plan_sha256=plan_sha256, fuentes=fuentes)
    lam = {k: tuple(v) for k, v in s["lambda"].items()}
    out = []
    for i, r in enumerate(filas):
        r = json.loads(json.dumps(r))
        prov = r.get("inversion_id") == "lambda_required" and r.get("result_status") in ("computed", "outside_support")
        if prov:
            fin = r.pop("_fin", None)
            need(isinstance(fin, dict) and fin.get("k") == "lambda", "FILA_MALFORMADA", i)
            clave = fin["set"] + "|" + fin["country"]
            need(clave in lam, "CLAVE_NO_DEMOSTRADA", clave)
            finalizar(r, fin, lam, (math.inf, -math.inf))
        out.append(r)
    return out
