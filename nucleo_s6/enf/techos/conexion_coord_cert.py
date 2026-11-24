"""rem121 — CONEXIÓN AISLADA PROPUESTA para recuperar techos COORD por la ruta CERTIFICADA existente (no se ejecuta con claves reales en
rem121). Cambio mínimo frente a calc_coord de tarea_lote.py (dca9d79b): la llamada del techo pasa de FR.capture_ceiling (búsqueda flotante
multinivel; error_kind 'convergence_estimate', que no es cota) a model.capture_ceiling con model = RUN.provider_for(cfg) (ModeloTeorico:
rama y cota con encierros, sup_max_boxes y jump_budget por defecto, misma SupConfig), que es el motor que produjo los techos padre de las
celdas dependientes. Además, cada techo guarda su detalle completo (clave, parámetros, identidad de código, configuración, valor, testigo,
valores de nivel, error_kind, cotas y error en las dos escalas).
Reglas: una sola llamada por clave, sin reintentos, sin cambiar tolerancias y sin respaldo flotante. ModeloTeorico.capture_ceiling cae a la
ruta flotante si la plataforma no es certificada; aquí se comprueba antes (certified y garantia) y después (error_kind == 'certified_bound'):
si falla, el techo queda incompleto. Cada techo se persiste en cuanto termina, para que una detención por tope conserve los anteriores."""
import hashlib
import json
import math
import os
import time
from dataclasses import asdict
from pathlib import Path

TOL_CONVERGE = 1e-7         # SupConfig.tol_converge: el modelo certificado compara con él su error NORMALIZADO por B_pot (escala de C2)
GARANTIA = "ieee754_binary64_rn"
MOTOR = ("modelos.py", "encierros_modelo.py", "supremum.py", "elementales.py", "intervalos.py", "frontier.py", "model.py")


def identidad_codigo(src_paper2b):
    return {n: hashlib.sha256((Path(src_paper2b) / n).read_bytes()).hexdigest() for n in MOTOR}


def configuracion(model, sup):
    return {"proveedor": getattr(model, "kind", None), "sup_max_boxes": getattr(model, "sup_max_boxes", None),
            "jump_budget": getattr(model, "jump_budget", None), "sup": sup.as_dict(),
            "tol_rama_y_cota": "0.5*tol_converge*B_pot.lo (unidades de R)", "criterio_cierre": "error_normalizado <= tol_converge y sin caja viva en curva de salto"}


def _finito(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def techo(model, cl, sup, clave, identidad, configuracion_esperada):
    """Un techo por la ruta certificada, con su detalle completo. Nunca devuelve 'complete' sin cota certificada."""
    fila = {"clave_transformada_sha256": clave, "parametros": cl["clave"], "diseno": cl["diseno"], "j": cl["j"], "tau": cl["tau"],
            "codigo": identidad, "configuracion": configuracion(model, sup), "garantia": getattr(model, "garantia", None),
            "C_2": None, "estado": "incomplete", "motivo": None, "error_kind": None}
    if fila["configuracion"] != configuracion_esperada:
        fila["motivo"] = "CONFIGURACION_DISTINTA_DE_LA_DECLARADA"
        return fila
    if getattr(model, "certified", False) is not True or fila["garantia"] != GARANTIA:
        fila["motivo"] = "PROVEEDOR_NO_CERTIFICADO"        # sin respaldo flotante
        return fila
    st = model.state({p: float(x) for p, x in cl["clave"].items()})
    t0 = time.time()
    ce = model.capture_ceiling(st, cl["diseno"], cl["j"], float(cl["tau"]["tau_d_upper"]), float(cl["tau"]["tau_f_upper"]), True, sup)
    s = ce.sup
    fila.update(C_2=ce.C2, B_pot=ce.B_pot, valor_R=s.sup, error_normalizado=ce.numerical_error, error_R=s.numerical_error,
                error_kind=s.error_kind, lower_R=s.lower, upper_R=s.upper, level_values=list(s.level_values), final_n=s.final_n,
                attained=s.attained, testigo={"tau_d": s.tau_d, "tau_f": s.tau_f}, testigos_laterales=[asdict(w) for w in s.witnesses],
                estado=ce.status, motivo=ce.reason, segundos=round(time.time() - t0, 3))
    fila["cierre_por_escala"] = {"normalizada": _finito(ce.numerical_error) and ce.numerical_error <= TOL_CONVERGE,
                                 "R": _finito(s.numerical_error) and s.numerical_error <= TOL_CONVERGE}
    if s.error_kind != "certified_bound":
        fila.update(estado="incomplete", motivo="RUTA_NO_CERTIFICADA:%s" % s.error_kind)    # un error flotante (aunque sea 0) no es cota
    return fila


def persistir(fila, ruta):
    with Path(ruta).open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def comparaciones(celdas, por_clave):
    """Idéntica a la de calc_coord: G_COORD = C2' − K1 solo con techo completo; K1 es el reutilizado del manifiesto (no cambia)."""
    out = []
    for c in celdas:
        t = por_clave.get(c["clave_transformada_sha256"]) or {"C_2": None, "estado": "ausente"}
        out.append({"unidad": c["unidad"], "cell_id": c["cell_id"], "K1_reutilizado": c["K1_reutilizado"], "G_padre": c["G_padre"], "C2_coord": t["C_2"],
                    "G_coord": (t["C_2"] - c["K1_reutilizado"]) if t["C_2"] is not None and t["estado"] == "complete" else None,
                    "estado_techo": t["estado"], "clave_transformada_sha256": c["clave_transformada_sha256"]})
    return out


def ejecutar(model, co, sup, identidad, configuracion_esperada, ruta_techos):
    """Recorre las claves a recuperar en el orden del manifiesto, una llamada por clave; persiste cada techo al terminar."""
    por_clave = {}
    for k in co["orden_recuperacion"]:
        fila = techo(model, co["claves_a_recuperar"][k], sup, k, identidad, configuracion_esperada)
        persistir(fila, ruta_techos)
        por_clave[k] = fila
    return por_clave, comparaciones(co["celdas_dependientes"], por_clave)
