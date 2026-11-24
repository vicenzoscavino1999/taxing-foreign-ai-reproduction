"""rem66 — QUIEBRES-D4 (E16, opción (a)) CONDICIONADA y DESACTIVADA por defecto. Solo la aplica quien la encuentra sellada EXACTAMENTE en el plan
(plan["decisiones"] == {QUIEBRES-D4: sha256 del texto}) y, al ejecutar, declarada en la autorización admitida por el mecanismo vigente
(campo documental «decisiones_firmadas»: id, texto_sha256 y referencia de la firma; el revisor verifica la firma antes de emitirla).
Alcance literal del texto 0494f042…: una búsqueda de quiebres que termina en incomplete_search con EXPANSION_LADDER_LIMIT_WITHOUT_BOUNDARY se
CONSERVA como resultado declarado (computation_status = incomplete, motivo y expansión alcanzada), nunca como completa ni como «sin quiebre».
Lo que el texto no cubre (reutilización entre corridas, dependencias, publicación E15) queda como propuesta explícita, no implementada."""
import math

D4_ID = "QUIEBRES-D4"
D4_SHA = "0494f0425574f8626017a1854ce2a5d1d0a48cfa81744e226060d5537c6035d5"
D4_MOTIVO = "EXPANSION_LADDER_LIMIT_WITHOUT_BOUNDARY"
ESTADO_TAREA = "incompleta_declarada_D4"          # estado del diario, distinto de completa_verificada
CAMPOS_FIRMA = ("transcripcion", "linea", "uuid", "mensaje_sha256")


def admitida_en_plan(decisiones):
    """None (desactivada) o EXACTAMENTE {QUIEBRES-D4: sha256}; cualquier otro valor es un error del plan."""
    if decisiones is None:
        return False
    if decisiones != {D4_ID: D4_SHA}:
        raise ValueError("DECISION_DEL_PLAN_NO_ADMITIDA: %s" % sorted(decisiones.items()) if isinstance(decisiones, dict) else "DECISION_DEL_PLAN_NO_ADMITIDA")
    return True


def activa(plan):
    return admitida_en_plan(plan.get("decisiones"))


def declarada_en_autorizacion(aut):
    return any(isinstance(d, dict) and d.get("id") == D4_ID and d.get("texto_sha256") == D4_SHA and isinstance(d.get("firma"), dict)
               and all(d["firma"].get(k) not in (None, "") for k in CAMPOS_FIRMA) for d in (aut.get("decisiones_firmadas") or []))


def elegible(filas):
    """La unidad es una búsqueda de quiebres incompleta EXACTAMENTE por agotamiento de la escalera declarada, con su expansión alcanzada."""
    rows = filas.get("support_breakdown_result") or []
    if len(rows) != 1 or filas.get("external_requirement_sensitivity_result"):
        return False
    r = rows[0]; x = r.get("reached_expansion_factor")
    return (r.get("status") == "incomplete_search" and r.get("computation_status") == "incomplete" and r.get("reason_code") == D4_MOTIVO
            and r.get("r_critical") is None and r.get("witness_set_id") is None and type(x) in (int, float) and math.isfinite(x) and x >= 1)


def nota(filas):
    r = filas["support_breakdown_result"][0]
    return "Sin quiebre hasta r = %s de la escalera declarada; fuera de ella no se afirma nada (QUIEBRES-D4; incomplete_search, %s)" % (r["reached_expansion_factor"], D4_MOTIVO)
