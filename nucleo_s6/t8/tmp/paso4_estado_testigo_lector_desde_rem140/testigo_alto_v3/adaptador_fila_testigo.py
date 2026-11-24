"""rem140 — ADAPTADOR MÍNIMO AISLADO de la prueba por fila para un techo alto de FUENTE NUEVA (candidato; no aceptado).
Por qué hace falta: en el esquema aceptado de captura (certificacion_fila.py 4741b4ea…, sin cambios) todo testigo es una fila
capture_ceiling_result de una de las 14 entregas listadas en FUENTES_CAPTURA.json (77d9a10b…); un techo calculado después no puede estar ahí
sin reescribir las fuentes, cosa que la enmienda v2 excluye. Este módulo NO edita ni sustituye certificacion_fila: importa el módulo aceptado
(por huella) y su Contexto, reutiliza `_testigo` para el testigo inferior aceptado y repite, campo a campo, la parte común de `validar` (fila,
destino, celda, valor, escala, plan, grupo, desigualdad exacta); lo único nuevo es el testigo superior, que no se autentica aquí sino que debe
ser IGUAL al objeto que entrega el lector tras autenticar la fuente fijada y revalidar sus bytes. El diferencial frente a `validar` lo
escribe el congelamiento (DIFERENCIAL_v3/adaptador_frente_a_validar.diff).
Tipo nuevo, solo candidato: pertenencia_testigo_alto_candidata ⇒ computed_candidato (nunca computed ni outside_support); si la mitad superior
no cubre v, la fila queda pendiente con MITAD_SUPERIOR_NO_CUBIERTA_POR_ESTE_TECHO (no prueba exclusión ni imposibilidad)."""
import hashlib
import importlib.util
from fractions import Fraction
from pathlib import Path

CAPTURA = "tmp/paso4_emision_lambda_conexion_captura_desde_rem137/c2_conexion/candidato_v3"
CF_SHA256 = "4741b4ea3b72fc2f754cc2d8c79dd9dd718f8e37205bf3e4ee5c0c539be60f4b"
GRUPO = "EQ-TECHO-T8-1"
PLANTILLA = "BRUN-cb33e6b24039acc84fb1a065"
CEI_INF = "CEI:dc4e1ba95f168fdd846cb39a44b404f204efbb47"
TIPO = "pertenencia_testigo_alto_candidata"
RELACION = {True: "destino_es_la_plantilla", False: "destino_equivalente_por_grupo"}
CAMPOS_SUPERIOR = frozenset(("incorporacion_sha256", "fuente_inventario_sha256", "fuente_base", "resultado_sha256", "validacion_recalculada_sha256",
                             "run_origen", "clave", "grupo", "plantilla_equivalencia", "C_2", "numerical_error", "escala", "computation_status",
                             "sup_not_attained", "garantia", "sintetico"))


class Rechazo(Exception):
    pass


def cargar_cf(raiz):
    """certificacion_fila ACEPTADO, cargado desde su sitio y solo si sus bytes son los fijados (no se copia ni se edita)."""
    p = Path(raiz) / CAPTURA / "certificacion_fila.py"
    if hashlib.sha256(p.read_bytes()).hexdigest() != CF_SHA256:
        raise Rechazo("CERTIFICACION_FILA_AJENA")
    s = importlib.util.spec_from_file_location("certificacion_fila_aceptada", p)
    CF = importlib.util.module_from_spec(s)
    s.loader.exec_module(CF)
    return CF


def esquema(CF):
    return frozenset(CF.BASE + ("grupo_equivalencia", "equivalencia_sha256", "relacion_destino", "testigo_inferior", "testigo_superior_nuevo"))


def desigualdades(V, wi, ws):
    """Las dos mitades EXACTAS de la regla aceptada: (C2_inf + err_inf <= V, V <= C2_sup - err_sup)."""
    return (Fraction(wi["C_2"]) + Fraction(wi["numerical_error"]) <= V, V <= Fraction(ws["C_2"]) - Fraction(ws["numerical_error"]))


def prueba_candidata(CF, ctx, i, wi, techo):
    f = ctx.captura[i]
    dest = ctx.run_de.get(f["ref"].split("/", 1)[0])
    return {"tipo": TIPO, "fila": i, "run_destino": dest, "cell_id": f["cell_id"], "ref_fila": f["ref"], "fila_en_unidad": f["fila_en_unidad"],
            "valor_requerido": f["fin_por_unidad"]["value"], "escala": CF.ESCALA, "grupo_equivalencia": ctx.grupo.get(dest),
            "equivalencia_sha256": ctx.eq_sha, "relacion_destino": RELACION[dest == PLANTILLA], "testigo_inferior": wi, "testigo_superior_nuevo": techo}


def validar_candidata(CF, ctx, prueba, techo):
    """Validación de la prueba candidata. Devuelve (True, "computed_candidato") o (False, motivo). Misma parte común que CF.validar."""
    tipo = prueba.get("tipo") if isinstance(prueba, dict) else None
    if tipo != TIPO:
        return False, "TIPO_DESCONOCIDO"
    if set(prueba) != esquema(CF):
        return False, "PRUEBA_FUERA_DE_ESQUEMA"
    i = prueba["fila"]
    f = ctx.captura.get(i) if isinstance(i, int) and not isinstance(i, bool) else None
    if f is None:
        return False, "FILA_NO_ES_CAPTURA_PROVISIONAL"
    dest = ctx.run_de.get(f["ref"].split("/", 1)[0])
    if prueba["run_destino"] != dest or prueba["cell_id"] != f["cell_id"] or prueba["ref_fila"] != f["ref"] or prueba["fila_en_unidad"] != f["fila_en_unidad"]:
        return False, "FILA_NO_COINCIDE"
    v = f["fin_por_unidad"]["value"]
    if prueba["valor_requerido"] != v or not isinstance(v, float) or prueba["escala"] != CF.ESCALA or not f["fin_por_unidad"].get("c2_defined"):
        return False, "VALOR_O_ESCALA_NO_COINCIDE"
    if ctx.plan.get(dest) != CF.PLAN:
        return False, "PLAN_DISTINTO"
    V = Fraction(v)
    # la ejecución nueva nunca es la corrida destino: siempre se apoya en la equivalencia aceptada y en el grupo del destino
    if prueba["equivalencia_sha256"] != ctx.eq_sha:
        return False, "PRUEBA_PROCEDENCIA_DISTINTA:equivalencia_sha256"
    if prueba["grupo_equivalencia"] != ctx.grupo.get(dest) or ctx.grupo.get(dest) != GRUPO or ctx.grupo.get(PLANTILLA) != GRUPO:
        return False, "CORRIDA_DESTINO_NO_EQUIVALENTE"
    if prueba["relacion_destino"] != RELACION[dest == PLANTILLA]:
        return False, "RELACION_CON_LA_PLANTILLA_DISTINTA"
    wi, ws = prueba["testigo_inferior"], prueba["testigo_superior_nuevo"]
    m = CF._testigo(ctx, wi)
    if m:
        return False, "INFERIOR:" + m
    if wi["ceiling_id"] != CEI_INF or wi["run_origen"] != PLANTILLA:
        return False, "TESTIGO_INFERIOR_AJENO"
    if not isinstance(ws, dict) or set(ws) != CAMPOS_SUPERIOR or ws != techo:
        return False, "TESTIGO_SUPERIOR_DISTINTO_DE_LA_FUENTE_LEIDA"
    if ws["run_origen"] == PLANTILLA or ws["run_origen"] in set(ctx.run_de.values()) or not str(ws["run_origen"]).startswith("TRUN-"):
        return False, "PROCEDENCIA_DE_LA_PLANTILLA"
    if ws["computation_status"] != "complete" or ws["sup_not_attained"] is not False or ws["escala"] != CF.ESCALA:
        return False, "TESTIGO_SUPERIOR_NO_COMPLETO"
    inf_ok, sup_ok = desigualdades(V, wi, ws)
    if not inf_ok:
        return False, "DESIGUALDAD_INFERIOR_NO_CUBRE_V"
    if not sup_ok:
        return False, "MITAD_SUPERIOR_NO_CUBIERTA_POR_ESTE_TECHO"
    return True, "computed_candidato"
