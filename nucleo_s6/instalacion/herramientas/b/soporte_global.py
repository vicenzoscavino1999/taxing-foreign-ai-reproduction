"""SOPORTE GLOBAL de los despejes provisionales (INTEGRACION H4 3.7, NO OFICIAL; copia candidata, no incorporada).

Semántica del NÚCLEO (paper2b.run.Run.unit_summary, herramientas/b/unidades.Executor.global_phase y assemble/_finalize):
  - por unidad: lambda = {"<conjunto>|<país>": [mín, máx] de λ_π de las macros ADMISIBLES}, c2 = [mín, máx] de los C_2
    no nulos de sus techos, o null si la unidad no tiene ninguno;
  - global: unión EXACTA de los resúmenes de TODAS las unidades del plan de la corrida (mismo run_id).
Una fila provisional (lambda_required / capture_required en computed u outside_support, con `_fin`) pertenece a la
corrida: su clave conjunto|país DEBE estar en el soporte global y, si su C2 está definido, el soporte de C2 también.

Este módulo es la ÚNICA implementación candidata de la familia; herramientas/b/unidades.py solo delega aquí:
  construir(resumenes_de_unidad, plan_unidades, run_id, plan_sha256) -> documento canónico con sha256 propio
      (respaldo «resumenes_de_unidad»: el consumidor re-deriva la unión y compara);
  desde_resumen_global(resumen, plan_unidades, run_id) -> soporte normalizado del formato GLOBAL/resumen.json
      (respaldo «resumen_global»: sin desglose por unidad; validación estricta, pero vínculo más débil, declarado);
  validar(soporte, ...) -> re-validación COMPLETA (nunca confía en un booleano «completo»);
  cerrar(filas, soporte, finalizar, ...) -> valida soporte y filas, exige claves/C2/contención derivados de las filas
      y SOLO entonces aplica `finalizar` (el criterio único del núcleo, unidades._finalize).
Toda entrada malformada termina en SoporteError con código (nunca IndexError/TypeError); nada se finaliza si falla algo.
Un soporte vacío o indefinido se representa con un ESTADO explícito (c2_estado = «vacio_demostrado», derivable de los
resúmenes), nunca con un intervalo artificial por defecto.
"""
from __future__ import annotations

import hashlib
import json
import math

ESQUEMA = "soporte-global-candidato-v1"
CAMPOS_FIN = {"k", "set", "country", "value", "c2_defined"}
PROVISIONALES = {"lambda_required": "lambda", "capture_required": "C2"}


class SoporteError(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo, self.detalle = codigo, str(detalle)[:300]


def need(t, codigo, detalle=""):
    if not t:
        raise SoporteError(codigo, detalle)


def _canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(o) -> str:
    return hashlib.sha256(_canon(o)).hexdigest()


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _intervalo(x, ruta):
    need(isinstance(x, (list, tuple)) and len(x) == 2, "SOPORTE_INTERVALO_INVALIDO", "%s: se exige [lo, hi] (cardinalidad 2): %r" % (ruta, x))
    lo, hi = x
    need(_num(lo) and _num(hi), "SOPORTE_INTERVALO_INVALIDO", "%s: extremos no finitos o no numéricos: %r" % (ruta, x))
    need(lo <= hi, "SOPORTE_INTERVALO_INVALIDO", "%s: invertido: %r" % (ruta, x))
    return [float(lo), float(hi)]


def _clave(k, ruta):
    need(isinstance(k, str) and k.count("|") == 1 and all(k.split("|")), "SOPORTE_CLAVE_INVALIDA", "%s: %r" % (ruta, k))
    return k


def _plan(plan_unidades):
    need(isinstance(plan_unidades, (list, tuple)) and plan_unidades and all(isinstance(u, str) and u for u in plan_unidades),
         "SOPORTE_PLAN_INVALIDO", "plan de unidades vacío o mal formado")
    need(len(set(plan_unidades)) == len(plan_unidades), "SOPORTE_PLAN_INVALIDO", "unidades repetidas en el plan")
    return sorted(plan_unidades)


def _lambda(d, ruta):
    need(isinstance(d, dict), "SOPORTE_ESQUEMA", "%s: lambda no es objeto" % ruta)
    return {_clave(k, ruta): _intervalo(v, "%s.lambda[%s]" % (ruta, k)) for k, v in d.items()}


def _c2(x, ruta):
    return None if x is None else _intervalo(x, ruta + ".c2")


def resumen_unidad(u, ruta="$"):
    """Resumen de UNA unidad, estricto: {unit_id, run_id, lambda, c2}."""
    need(isinstance(u, dict) and set(u) == {"unit_id", "run_id", "lambda", "c2"}, "SOPORTE_ESQUEMA",
         "%s: resumen de unidad con campos %s" % (ruta, sorted(u) if isinstance(u, dict) else type(u).__name__))
    need(isinstance(u["unit_id"], str) and u["unit_id"] and isinstance(u["run_id"], str) and u["run_id"], "SOPORTE_ESQUEMA", "%s: unit_id/run_id" % ruta)
    return {"unit_id": u["unit_id"], "run_id": u["run_id"], "lambda": _lambda(u["lambda"], ruta), "c2": _c2(u["c2"], ruta)}


def _union(unidades):
    lam, c2 = {}, None
    for u in unidades:
        for k, (lo, hi) in u["lambda"].items():
            a, b = lam.get(k, (math.inf, -math.inf))
            lam[k] = [min(a, lo), max(b, hi)]
        if u["c2"] is not None:
            c2 = [min(c2[0], u["c2"][0]), max(c2[1], u["c2"][1])] if c2 else list(u["c2"])
    return dict(sorted(lam.items())), c2


def construir(resumenes, plan_unidades, run_id, plan_sha256):
    """Documento CANÓNICO del soporte global desde los resúmenes de TODAS las unidades del plan (misma corrida)."""
    plan = _plan(plan_unidades)
    need(isinstance(run_id, str) and run_id, "SOPORTE_ESQUEMA", "run_id")
    need(isinstance(plan_sha256, str) and len(plan_sha256) == 64, "SOPORTE_ESQUEMA", "plan_sha256")
    need(isinstance(resumenes, (list, tuple)), "SOPORTE_ESQUEMA", "resúmenes no es una lista")
    us = [resumen_unidad(u, "$unidades[%d]" % i) for i, u in enumerate(resumenes)]
    ids = [u["unit_id"] for u in us]
    need(len(set(ids)) == len(ids), "SOPORTE_UNIDAD_DUPLICADA", sorted({i for i in ids if ids.count(i) > 1})[:5])
    need(all(u["run_id"] == run_id for u in us), "SOPORTE_RUN_DISTINTO", sorted({u["run_id"] for u in us if u["run_id"] != run_id})[:3])
    ajenas, faltan = sorted(set(ids) - set(plan)), sorted(set(plan) - set(ids))
    need(not ajenas, "SOPORTE_UNIDAD_AJENA", ajenas[:5])
    need(not faltan, "SOPORTE_GLOBAL_INCOMPLETO", faltan[:5])
    lam, c2 = _union(us)
    doc = {"esquema": ESQUEMA, "respaldo": "resumenes_de_unidad", "run_id": run_id, "plan_sha256": plan_sha256, "plan_unidades": plan,
           "unidades": sorted(us, key=lambda u: u["unit_id"]), "lambda": lam, "c2": c2, "c2_estado": "definido" if c2 is not None else "vacio_demostrado"}
    doc["sha256"] = _sha(doc)
    return doc


def desde_resumen_global(resumen, plan_unidades, run_id):
    """Formato GLOBAL/resumen.json del núcleo + unidades cubiertas: validación estricta; respaldo «resumen_global»."""
    plan = _plan(plan_unidades)
    need(isinstance(resumen, dict) and set(resumen) >= {"run_id", "unidades_cubiertas", "lambda", "c2"} and set(resumen) <= {"run_id", "unidades_cubiertas", "lambda", "c2", "completo"},
         "SOPORTE_ESQUEMA", "resumen global con campos %s" % (sorted(resumen) if isinstance(resumen, dict) else type(resumen).__name__))
    need(resumen["run_id"] == run_id, "SOPORTE_RUN_DISTINTO", resumen.get("run_id"))
    cub = resumen["unidades_cubiertas"]
    need(isinstance(cub, (list, tuple)) and all(isinstance(u, str) for u in cub), "SOPORTE_ESQUEMA", "unidades_cubiertas")
    need(len(set(cub)) == len(cub), "SOPORTE_UNIDAD_DUPLICADA", "unidades cubiertas repetidas")
    need(not (set(cub) - set(plan)), "SOPORTE_UNIDAD_AJENA", sorted(set(cub) - set(plan))[:5])
    need(not (set(plan) - set(cub)), "SOPORTE_GLOBAL_INCOMPLETO", sorted(set(plan) - set(cub))[:5])
    lam, c2 = _lambda(resumen["lambda"], "$"), _c2(resumen["c2"], "$")
    doc = {"esquema": ESQUEMA, "respaldo": "resumen_global", "run_id": run_id, "plan_sha256": None, "plan_unidades": plan, "unidades": None,
           "lambda": dict(sorted(lam.items())), "c2": c2, "c2_estado": "definido" if c2 is not None else "vacio_declarado"}
    doc["sha256"] = _sha(doc)
    return doc


def validar(soporte, *, run_id, plan_unidades, plan_sha256=None):
    """Re-validación COMPLETA del soporte que llega al consumidor (no confía en ningún campo declarado)."""
    try:
        need(isinstance(soporte, dict), "SOPORTE_ESQUEMA", "el soporte no es un objeto")
        need(soporte.get("esquema") == ESQUEMA and soporte.get("respaldo") in ("resumenes_de_unidad", "resumen_global"), "SOPORTE_ESQUEMA", "esquema o respaldo")
        if soporte["respaldo"] == "resumenes_de_unidad":
            esperado = construir(soporte.get("unidades"), plan_unidades, run_id, plan_sha256 if plan_sha256 is not None else soporte.get("plan_sha256"))
        else:
            esperado = desde_resumen_global({"run_id": soporte.get("run_id"), "unidades_cubiertas": soporte.get("plan_unidades"),
                                             "lambda": soporte.get("lambda"), "c2": soporte.get("c2")}, plan_unidades, run_id)
        need(json.loads(_canon(soporte)) == json.loads(_canon(esperado)), "SOPORTE_NO_DERIVADO",
             "el soporte no es el derivado de sus resúmenes, su plan y su corrida (hash %s)" % str(soporte.get("sha256"))[:16])
        return esperado
    except SoporteError:
        raise
    except (TypeError, ValueError, KeyError, AttributeError) as e:      # entrada malformada: siempre error controlado
        raise SoporteError("SOPORTE_ESQUEMA", "%s: %s" % (type(e).__name__, e))


def requisitos(filas):
    """(claves λ exigidas, ¿exige C2?, filas provisionales) derivados de las filas; filas mal formadas -> error."""
    need(isinstance(filas, (list, tuple)), "SOPORTE_FILA_MALFORMADA", "las filas no son una lista")
    claves, exige_c2, prov = set(), False, []
    for i, r in enumerate(filas):
        need(isinstance(r, dict) and isinstance(r.get("inversion_id"), str), "SOPORTE_FILA_MALFORMADA", "fila %d" % i)
        fin = r.get("_fin")
        es_prov = r["inversion_id"] in PROVISIONALES and r.get("result_status") in ("computed", "outside_support")
        if not es_prov:
            need(fin is None, "SOPORTE_FILA_MALFORMADA", "fila %d: _fin no exigido" % i)
            continue
        need(isinstance(fin, dict) and set(fin) == CAMPOS_FIN and fin["k"] == PROVISIONALES[r["inversion_id"]] and _num(fin["value"])
             and isinstance(fin["set"], str) and isinstance(fin["country"], str) and isinstance(fin["c2_defined"], bool),
             "SOPORTE_FILA_MALFORMADA", "fila %d: _fin %r" % (i, fin))
        if fin["k"] == "lambda":
            claves.add(fin["set"] + "|" + fin["country"])
        elif fin["c2_defined"]:
            exige_c2 = True
        prov.append(i)
    return claves, exige_c2, prov


def cerrar(filas, soporte, finalizar, *, run_id, plan_unidades, plan_sha256=None, contenidos=()):
    """Cierra los estados provisionales SOLO con un soporte global válido y suficiente para ESTAS filas; si algo falla,
    error controlado y ninguna fila se finaliza. `contenidos`: valores propios de la corrida que el soporte debe contener
    ((«lambda», clave, λ_π) de macros admisibles y («C2», C_2) de techos de las celdas validadas)."""
    s = validar(soporte, run_id=run_id, plan_unidades=plan_unidades, plan_sha256=plan_sha256)
    claves, exige_c2, prov = requisitos(filas)
    faltan = sorted(claves - set(s["lambda"]))
    need(not faltan, "SOPORTE_SIN_CLAVE", "claves conjunto|país de filas provisionales ausentes del soporte: %s" % faltan[:5])
    need(not exige_c2 or s["c2"] is not None, "SOPORTE_C2_VACIO", "hay filas con C2 definido y el soporte declara C2 %s" % s["c2_estado"])
    for c in contenidos:
        try:
            if c[0] == "lambda":
                lo, hi = s["lambda"].get(c[1], (math.inf, -math.inf))
                need(_num(c[2]) and lo <= c[2] <= hi, "SOPORTE_NO_CONTIENE", "λ_π %r de %s fuera de %r" % (c[2], c[1], (lo, hi)))
            elif c[0] == "C2":
                need(s["c2"] is not None and _num(c[1]) and s["c2"][0] <= c[1] <= s["c2"][1], "SOPORTE_NO_CONTIENE", "C_2 %r fuera de %r" % (c[1], s["c2"]))
            else:
                raise SoporteError("SOPORTE_ESQUEMA", "contenido %r" % (c,))
        except (TypeError, IndexError) as e:
            raise SoporteError("SOPORTE_ESQUEMA", "contenido mal formado %r: %s" % (c, e))
    lam = {k: tuple(v) for k, v in s["lambda"].items()}
    c2 = tuple(s["c2"]) if s["c2"] is not None else (math.inf, -math.inf)     # solo se usa si ninguna fila exige C2
    out = []
    for i, r in enumerate(filas):
        r = dict(r)
        fin = r.pop("_fin", None)
        if i in prov:
            finalizar(r, fin, lam, c2)
        out.append(r)
    return out
