"""rem140 — C3 TESTIGO ALTO v3 (derivado de la pieza común v2 de rem139, 9d36aa03…; la corrección de autoridad aceptada no cambia).
Corrige P4-T8-TESTIGO-ESTADO-MOTOR: la clasificación ya no lee solo la cabecera y la validación liga los estados duplicados (cabecera =
Ceiling, sup_campos = SupResult), las causas y la convergencia con el esquema REAL del motor del núcleo fijado: Ceiling copia status y reason
del SupResult (frontier.py capture_ceiling; modelos.py ModeloTeorico.capture_ceiling) y solo lleva SupResult con el instrumento disponible;
en las tres rutas que fijan el estado (supremum.py: status/reason por converged; modelos.py: salto vivo, cota no cerrada, cierre) rige
status == "complete" ⟺ converged ⟺ reason is None, y la causa de salto vivo implica attained = False. complete exige instrumento
disponible, convergencia y cierre coherentes en los dos niveles, con campos presentes y tipos exactos; cualquier campo que niegue el cierre
hace la clase incomplete (nunca complete por el resumen). validar_bytes aplica la misma validación a bytes ya leídos (lo usa el lector).
rem139 — C3 TESTIGO ALTO v2: piezas COMUNES del paquete mínimo (manifiesto v2 de una clave, fijaciones, clave, puerta de alcance/decisión,
clasificación y validación). Lo usan trabajador_testigo.py, validar_testigo.py, emitir_alcance_testigo.py y las pruebas.
Corrige P4-T8-TESTIGO-AUTORIDAD: el alcance se coteja campo a campo con el documento ESPERADO (plan, operación, tareas, asignaciones,
despliegue y acta con huella completa y bytes, C0, límites, banderas y entradas: manifiesto, clave, grupo, núcleo, módulos requeridos,
controles, puente, D7 y la lista COMPLETA de piezas) y las piezas con los bytes REALMENTE ejecutados (este módulo leído al importarse, el
script que llama, la receta y el emisor), antes de calcular o crear resultados; en fixture también se exige un alcance FIXTURE.
Corrige P4-T8-TESTIGO-GARANTIA: B_pot y su intervalo desde las primitivas binary64 con el núcleo histórico (EM.IParams/Iv, convención del
motor y del validador COORD), error que cubre los dos extremos normalizados con redondeo dirigido y en Fraction exacto, coherencia
valor/testigo/dominio y de los campos reales del motor, sin la holgura 1e-12·(|C2|+1), C2 + err >= L_b64 (puente) y evidencia de módulos
no vacía que cubre los módulos requeridos de la ruta real; el entorno histórico declarado va aparte de la evidencia real.
No importa el modelo: el trabajador (produccion, tras la puerta) y la validación (solo IParams/Iv para Bi) cargan paper2b del núcleo fijado.
Clasificación (no promueve nada): complete | incomplete | sup_not_attained | sin_resultado."""
import csv
import datetime as dt
import hashlib
import json
import math
import sys
from decimal import Decimal
from fractions import Fraction as Fr
from pathlib import Path

sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: sha(Path(p).read_bytes())  # noqa: E731
canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")  # noqa: E731
H = lambda v: sha(canon(v))  # noqa: E731
AQUI = Path(__file__).resolve().parent
PROPIO = HF(__file__)                       # bytes de ESTE módulo al importarse (los que se ejecutan)
OPERACION = "TESTIGO_ALTO_C3"
TAREAS = ["TESTIGO-ALTO-TRABAJO", "TESTIGO-ALTO-VALIDAR"]
LIMITES = {"procesos": 1, "tope_s": 600.0, "intentos": 1, "union_s": 10800.0}
ASIGNACIONES = {TAREAS[0]: {"procesos": 1, "tope_s": 600.0, "trabajador": "trabajador_testigo.py"},
                TAREAS[1]: {"procesos": 1, "tope_s": 600.0, "validador": "validar_testigo.py"}}
ROL_TAREA = {"trabajador": TAREAS[0], "validador": TAREAS[1]}
PIEZAS = ("testigo_comun.py", "trabajador_testigo.py", "validar_testigo.py", "receta_testigo.sh", "emitir_alcance_testigo.py")
FIXTURE = "FIXTURE — documento de prueba rem140, NO productivo: "
KIND_MANIFIESTO = "manifiesto-testigo-alto-c3-v2"
B64_06 = Fr(0.6)
ERR_MAX = Fr(1, 10 ** 7)
C0 = "tmp/paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
C0_ID = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
DESPLIEGUE = "tmp/paso4_continuacion_p3_desde_rem89/p3/despliegue_operativo.json"
ACTA = "tmp/paso4_continuacion_p3_desde_rem89/p3/acta_p3.json"
AUTORIDAD = {DESPLIEGUE: "f293a0a62d2cb6bf3517e72a0bfc589ee703685d4434c2cdae4b4cd1b5085d6c",
             ACTA: "8e59ea4870c987ecca4ea1e5a8cb3f95581fcc1a64b3e7aa61c035a9b8e0dcfc"}
PLATAFORMA = "ieee754_binary64_rn"
CAMPOS_SUP = ("sup", "attained", "tau_d", "tau_f", "lateral_low", "lateral_high", "witnesses", "level_values", "numerical_error", "converged",
              "status", "reason", "evaluations", "lateral_axis", "final_n", "error_kind", "upper", "lower", "n_jump_points")
CAMPOS_CEIL = ("instrument_available", "sup", "C2", "B_pot", "numerical_error", "status", "reason")
# rem140 — vocabulario de estado del motor (núcleo lima1855): SupResult.status por converged (supremum.py, dos rutas) y los tres desenlaces de
# ModeloTeorico.capture_ceiling (modelos.py); las pruebas lo derivan por AST del núcleo y lo cotejan con estas constantes.
ESTADOS_SUP = ("complete", "incomplete")
CAUSAS_SUP = ("SUP_NOT_CONVERGED", "CERTIFIED_BOUND_NOT_CLOSED", "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE")
CAUSA_SALTO = "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE"
TIPOS_ESTADO_CAB = {"instrument_available": (bool,), "computation_status": (str,), "reason_code": (str, type(None)), "converged": (bool,),
                    "attained": (bool,), "sup_not_attained": (bool,)}
TIPOS_ESTADO_SUP = {"status": (str,), "reason": (str, type(None)), "converged": (bool,), "attained": (bool,)}


class Rechazo(RuntimeError):
    def __init__(self, codigo, detalle=""):
        super().__init__("%s: %s" % (codigo, detalle))
        self.codigo, self.detalle = codigo, detalle


def need(c, codigo, detalle=""):
    if not c:
        raise Rechazo(codigo, detalle)


def escribir_x(path, doc):
    with Path(path).open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")


# ------------------------------------------------------------------------------------------------- manifiesto y fuentes
def cargar_manifiesto(raiz, ruta):
    """Manifiesto v2 + comprobación de TODAS sus fijaciones contra los bytes reales (fuentes, autoridad, núcleo, módulos requeridos, D7)."""
    raiz, raw = Path(raiz), Path(ruta).read_bytes()
    m = json.loads(raw)
    need(m.get("kind") == KIND_MANIFIESTO, "MANIFIESTO_KIND")
    need(H(m["payload"]) == m["clave"], "CLAVE_AJENA", "la clave no es sha256(canon(payload))")
    for nombre, f in m["fuentes"].items():
        need(HF(raiz / f["ruta"]) == f["sha256"], "FUENTE_AJENA", nombre)
    need(m.get("autoridad") == AUTORIDAD, "AUTORIDAD_AJENA")
    for rel, h in AUTORIDAD.items():
        need(HF(raiz / rel) == h, "AUTORIDAD_AJENA", rel)
    inv = json.loads((raiz / m["nucleo"]["inventario"]["ruta"]).read_bytes())["files"]
    need(HF(raiz / m["nucleo"]["inventario"]["ruta"]) == m["nucleo"]["inventario"]["sha256"], "FUENTE_AJENA", "inventario del núcleo")
    base = raiz / m["nucleo"]["raiz"]
    for rel, h in m["nucleo"]["archivos"].items():
        need(HF(base / rel) == h and inv.get(m["nucleo"]["prefijo_inventario"] + rel, {}).get("sha256") == h, "IDENTIDAD_DISTINTA", rel)
    reales = sorted(p.relative_to(base).as_posix() for p in (base / "paper2b").glob("*.py"))
    need(reales == sorted(m["nucleo"]["archivos"]), "IDENTIDAD_DISTINTA", "archivos del núcleo distintos de los fijados")
    req = (m.get("modulos_ruta_real") or {}).get("archivos") or {}
    need(req and all(m["nucleo"]["archivos"].get(k) == v for k, v in req.items()), "MODULOS_REQUERIDOS_AJENOS")
    d7 = raiz / m["d7"]["ruta"]
    man = json.loads((d7 / "d7_manifest.json").read_bytes())
    need(HF(d7 / "d7_manifest.json") == m["d7"]["manifiesto_sha256"] and man["tree_sha256"] == m["d7"]["arbol"], "FUENTE_AJENA", "D7")
    for f in man["files"]:
        need(HF(d7 / f["path"]) == f["sha256"], "FUENTE_AJENA", "D7:" + f["path"])
    return m, sha(raw)


def valores_d7(raiz, m):
    """Valores de la celda desde los nodos L0 de D7 (Decimal(repr(float)), como D7View.nodes) en TODOS los conjuntos del manifiesto."""
    d7 = Path(raiz) / m["d7"]["ruta"]
    with open(d7 / "support_set.csv", encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    with open(d7 / "parameter_bindings.csv", encoding="utf-8", newline="") as fh:
        bind = {(r["support_set_id"], r["parameter_id"], r["scope_id"]): r for r in csv.DictReader(fh)}
    sup = {}
    for r in filas:
        sup.setdefault((r["support_set_id"], r["parameter_id"]), {})[r["variant_id"]] = r
    vistos = None
    for set_id, idx in m["indices_por_conjunto"].items():
        vals = {}
        for pid in list(m["celda"]) + list(m["fijos"]):
            v = sup[(set_id, pid)]
            s = next(iter(v.values())) if len(v) == 1 else next(x for x in v.values() if x["support_id"] == bind[(set_id, pid, "global")]["support_id"])
            ns = [Decimal(repr(x)) if isinstance(x, float) else Decimal(str(x)) for x in json.loads(s["level0_nodes"])]
            vals[pid] = ns[idx[pid]] if pid in idx else ns[0]
            need(vals[pid] == Decimal(m["celda"].get(pid, m["fijos"].get(pid))), "CELDA_DISTINTA", "%s/%s" % (set_id, pid))
        need(vistos is None or vals == vistos, "CELDA_DISTINTA", "valores distintos entre conjuntos")
        vistos = vals
    return vistos


def payload_desde_valores(m, vals, canon_dec):
    unidades = {r["parameter_id"]: r["value_unit"] for r in m["payload"]["values"]}     # STRUCT + FIXED (sin barras: van en tau_domain)
    need(set(unidades) <= set(vals), "CELDA_DISTINTA", "primitivas de la clave ausentes")
    p = dict(m["payload"], values=[{"parameter_id": k, "value": canon_dec(vals[k]), "value_unit": unidades[k]} for k in sorted(unidades)])
    return p, H(p)


# ------------------------------------------------------------------------------------------------- alcance esperado y puerta
def entradas_esperadas(m, msha, piezas):
    return {"manifiesto_testigo": msha, "clave": m["clave"], "grupo": m["grupo"], "nucleo_inventario": m["nucleo"]["inventario"]["sha256"],
            "nucleo_archivos_sha256": H(m["nucleo"]["archivos"]), "modulos_ruta_real_sha256": H(m["modulos_ruta_real"]["archivos"]),
            "controles": m["fuentes"]["controles"]["sha256"], "puente": m["fuentes"]["puente"]["sha256"], "piezas": piezas, "d7_arbol": m["d7"]["arbol"]}


def documento_esperado(raiz, m, msha, piezas, AA):
    """Todos los campos del alcance salvo emitida_utc y etiqueta (los usa el emisor para construir y la puerta para cotejar)."""
    return {"kind": AA.KIND_ALCANCE, "plan_sha256": m["plan_sha256"], "operaciones": [OPERACION], "tareas": list(TAREAS),
            "asignaciones": json.loads(json.dumps(ASIGNACIONES)), "despliegue_sha256": AUTORIDAD[DESPLIEGUE],
            "entradas": entradas_esperadas(m, msha, piezas), "limites": dict(LIMITES), "repetir": [], "excepciones": [],
            "instalacion_identidad": C0_ID, "congelamiento_p3_sha256": AUTORIDAD[ACTA], "b_official_run_authorized": False,
            "freeze_run_authorized": False, "official_export_authorized": False}


def cargar_c0(raiz):
    sys.path.insert(0, str(Path(raiz) / C0 / "herramientas/b"))
    import aprobacion_alcance as AA
    need(Path(AA.__file__).resolve() == (Path(raiz) / C0 / "herramientas/b/aprobacion_alcance.py").resolve(), "C0_NO_FIJADO")
    return AA


def puerta(raiz, modo, alcance, decision, m, manifiesto_sha, rol, script, script_sha):
    """Puerta común (trabajador y validador), ANTES de calcular o crear resultados. <script>/<script_sha>: el archivo que llama y la huella de
    los bytes que leyó al importarse. produccion: alcance v3 TESTIGO_ALTO_C3 igual al esperado + decisión humana nativa (C0, sin cambios);
    fixture: alcance FIXTURE igual al esperado y nunca una decisión. Devuelve la evidencia de la puerta."""
    raiz, script = Path(raiz), Path(script).resolve()
    need(modo in ("produccion", "fixture"), "MODO_INVALIDO", modo)
    need(rol in ROL_TAREA, "ROL_INVALIDO", rol)
    AA = cargar_c0(raiz)
    if modo == "produccion":
        need(alcance is not None and decision is not None, "DECISION_REFERENCIA_AUSENTE")
    need(alcance is not None, "ALCANCE_AUSENTE")
    raw = Path(alcance).read_bytes()
    al = json.loads(raw)
    try:
        AA.verificar_documento(al)
    except AA.Rechazo as e:
        raise Rechazo("ALCANCE_NO_VERIFICABLE", e.codigo)
    need(al.get("operaciones") == [OPERACION] and al.get("tareas") == TAREAS, "ALCANCE_DE_OTRA_OPERACION", str(al.get("operaciones")))
    ent = al.get("entradas") or {}
    need(ent.get("manifiesto_testigo") == manifiesto_sha, "MANIFIESTO_AJENO")
    piezas = ent.get("piezas")
    need(isinstance(piezas, dict) and tuple(sorted(piezas)) == tuple(sorted(PIEZAS)), "PIEZAS_AUSENTES_O_INCOMPLETAS", str(sorted(piezas or {})))
    need(all(isinstance(h, str) and len(h) == 64 and all(c in "0123456789abcdef" for c in h) for h in piezas.values()), "HUELLA_NO_COMPLETA")
    esperado = documento_esperado(raiz, m, manifiesto_sha, piezas, AA)
    need(ent == esperado["entradas"], "ENTRADAS_DISTINTAS", ",".join(sorted(k for k in set(ent) | set(esperado["entradas"]) if ent.get(k) != esperado["entradas"].get(k))))
    claves = (set(esperado) | set(al)) - {"emitida_utc", "etiqueta"}
    distintos = sorted(k for k in claves if al.get(k, "<ausente>") != esperado.get(k, "<ajeno>"))
    need(not distintos, "ALCANCE_DISTINTO_DEL_ESPERADO", ",".join(distintos))
    need(isinstance(al.get("etiqueta"), str) and isinstance(al.get("emitida_utc"), str), "ALCANCE_DISTINTO_DEL_ESPERADO", "etiqueta/emitida_utc")
    for rel, h in AUTORIDAD.items():
        need(HF(raiz / rel) == h, "AUTORIDAD_AJENA", rel)
    need(AA.identidad_instalacion(raiz / C0) == C0_ID, "C0_IDENTIDAD")
    # bytes ejecutados: este módulo (al importarse), el script que llama (al importarse), la receta y el emisor del mismo paquete
    asig = al["asignaciones"][ROL_TAREA[rol]]
    need(script.parent == AQUI and script.name == asig.get(rol), "ASIGNACION_INCOMPATIBLE", "%s como %s" % (script.name, rol))
    need(asig.get("procesos") == 1 and asig.get("tope_s") == 600.0, "ASIGNACION_INCOMPATIBLE", "procesos/tope")
    ejecutado = {"testigo_comun.py": PROPIO, script.name: script_sha}
    for n in PIEZAS:                        # las piezas no cargadas en este proceso (receta, emisor y el otro script) por sus bytes en disco
        ejecutado.setdefault(n, HF(AQUI / n))
    need(HF(AQUI / "testigo_comun.py") == PROPIO and HF(script) == script_sha, "CODIGO_CAMBIADO_DURANTE_LA_EJECUCION")
    distintas = sorted(n for n, h in ejecutado.items() if piezas.get(n) != h)
    need(not distintas, "CODIGO_DISTINTO_DEL_ALCANCE", ",".join(distintas))
    fixture = str(al.get("etiqueta", "")).startswith("FIXTURE")
    ev = {"modo": modo, "alcance_sha256": sha(raw), "fixture": fixture, "decision": None, "rol": rol, "ejecutado": ejecutado, "piezas_alcance": piezas}
    if modo == "produccion":
        need(not fixture, "ALCANCE_FIXTURE_EN_PRODUCCION")
        try:
            ev["decision"] = AA.decision_humana(str(decision), sha(raw), al["emitida_utc"])
        except AA.Rechazo as e:
            raise Rechazo("DECISION_NO_VALIDA", e.codigo)
        ev["decision_ref_sha256"] = HF(decision)
    else:
        need(fixture, "FIXTURE_REQUERIDO")
        need(decision is None, "DECISION_EN_FIXTURE")
    return ev


# ------------------------------------------------------------------------------------------------- clasificación y validación
def clasificar(r):
    """rem140 — clase conservadora desde TODOS los campos de estado (cabecera = Ceiling y sup_campos = SupResult), nunca solo desde la
    cabecera: complete solo si el instrumento está disponible y los dos niveles dicen complete, converged = True y sin causa; cualquier campo
    que niegue el cierre (o falte) ⇒ incomplete; cerrado sin alcanzar ⇒ sup_not_attained; sin RESULTADO (o ilegible como objeto) ⇒ sin_resultado."""
    if not isinstance(r, dict):
        return "sin_resultado"
    s = r.get("sup_campos") if isinstance(r.get("sup_campos"), dict) else {}
    cerrado = (r.get("instrument_available") is True and r.get("computation_status") == "complete" and s.get("status") == "complete"
               and r.get("converged") is True and s.get("converged") is True and "reason_code" in r and r["reason_code"] is None
               and "reason" in s and s["reason"] is None)
    if not cerrado:
        return "incomplete"
    if r.get("sup_not_attained") is not False or r.get("attained") is not True or s.get("attained") is not True:
        return "sup_not_attained"
    return "complete"


def comprobar_estado(r):
    """rem140 — estado del motor del RESULTADO: presencia y tipos EXACTOS de los campos de estado en los dos niveles; duplicados iguales
    (computation_status/status, reason_code/reason, converged, attained); en cada nivel la invariante del motor status == "complete" ⟺
    converged ⟺ reason is None, estado y causa del vocabulario del motor y causa de salto vivo ⇒ attained = False; instrumento disponible
    (el motor no entrega SupResult sin instrumento). Devuelve (fallos, niveles leídos)."""
    s = r.get("sup_campos")
    if not isinstance(s, dict) or any(k not in r or type(r[k]) not in t for k, t in TIPOS_ESTADO_CAB.items()) \
            or any(k not in s or type(s[k]) not in t for k, t in TIPOS_ESTADO_SUP.items()):
        return ["ESTADO_DEL_MOTOR_AUSENTE_O_DE_TIPO_INVALIDO"], None
    cab = {"status": r["computation_status"], "reason": r["reason_code"], "converged": r["converged"], "attained": r["attained"]}
    sup = {k: s[k] for k in ("status", "reason", "converged", "attained")}
    fallos = []
    if cab != sup:
        fallos.append("ESTADO_DUPLICADO_INCOHERENTE")
    for nivel in (cab, sup):
        if nivel["status"] not in ESTADOS_SUP:
            fallos.append("ESTADO_DESCONOCIDO")
        if nivel["reason"] is not None and nivel["reason"] not in CAUSAS_SUP:
            fallos.append("CAUSA_DESCONOCIDA")
        cierre = nivel["status"] == "complete"
        if nivel["converged"] is not cierre or (nivel["reason"] is None) is not cierre:
            fallos.append("ESTADO_DEL_MOTOR_INCOHERENTE")
        if nivel["reason"] == CAUSA_SALTO and nivel["attained"] is not False:
            fallos.append("ESTADO_DEL_MOTOR_INCOHERENTE")
    if r["instrument_available"] is not True:
        fallos.append("INSTRUMENTO_NO_DISPONIBLE")
    return list(dict.fromkeys(fallos)), {"cabecera": cab, "sup_campos": sup, "instrument_available": r["instrument_available"]}


def primitivas_b64(m):
    """Primitivas binary64 de la celda (las del motor: float(Decimal)) para IParams/state_from_primitives."""
    return {p: float(Decimal(v)) for p, v in list(m["celda"].items()) + [(k, m["fijos"][k]) for k in ("c_legal", "gamma", "t", "z_m")]}


def intervalo_bpot(raiz, m):
    """Bi = EM.IParams.from_state(M.state_from_primitives(primitivas binary64)).B_pot del núcleo histórico fijado (= validador COORD)."""
    base = str((Path(raiz) / m["nucleo"]["raiz"]).resolve())
    if base not in sys.path:
        sys.path.insert(0, base)
    from paper2b import encierros_modelo as EM
    from paper2b import model as M
    from paper2b.intervalos import Iv
    need(Path(EM.__file__).resolve().parent == (Path(base) / "paper2b").resolve(), "IDENTIDAD_DISTINTA", EM.__file__)
    for mod in (EM, M, sys.modules["paper2b.intervalos"]):
        rel = Path(mod.__file__).resolve().relative_to(Path(base).resolve()).as_posix()
        need(HF(mod.__file__) == m["nucleo"]["archivos"].get(rel), "IDENTIDAD_DISTINTA", rel)
    return EM.IParams.from_state(M.state_from_primitives(primitivas_b64(m))).B_pot, Iv


def _float(r, k):
    v = r[k]
    need(isinstance(v, float) and math.isfinite(v), "CAMPOS_DEL_MOTOR_AUSENTES", k)
    return v


def comprobar_numeros(raiz, m, r):
    """Coherencia numérica del RESULTADO (sin holgura). Devuelve la lista de fallos y el detalle."""
    fallos, det = [], {}
    try:
        C2f, errf, Bf = _float(r, "C2"), _float(r, "numerical_error_share"), _float(r, "B_pot")
        lof, hif, supf, eRf = _float(r, "sup_lower"), _float(r, "sup_upper"), _float(r, "sup_R"), _float(r, "numerical_error_R")
        tdf, tff = _float(r, "tau_d_at_sup"), _float(r, "tau_f_at_sup")
        need(isinstance(r["level_values"], list) and isinstance(r["final_n"], int) and not isinstance(r["final_n"], bool)
             and isinstance(r["attained"], bool) and isinstance(r["sup_campos"], dict), "CAMPOS_DEL_MOTOR_AUSENTES", "level_values/final_n/attained")
    except (KeyError, Rechazo) as e:
        return ["CAMPOS_DEL_MOTOR_AUSENTES"], {"detalle": str(e)}
    C2, err, B, lo, hi, sR, eR = map(Fr, (C2f, errf, Bf, lof, hif, supf, eRf))
    td, tf = Fr(tdf), Fr(tff)
    s = r["sup_campos"]
    if any(s.get(a) != b for a, b in (("sup", supf), ("lower", lof), ("upper", hif), ("numerical_error", eRf), ("tau_d", tdf), ("tau_f", tff),
                                      ("level_values", r["level_values"]), ("final_n", r["final_n"]), ("attained", r["attained"]),
                                      ("error_kind", r.get("error_kind")))) or set(s) != set(CAMPOS_SUP):
        fallos.append("CAMPOS_DEL_MOTOR_INCOHERENTES")
    if r.get("sup_not_attained") is not (not r["attained"]):
        fallos.append("CAMPOS_DEL_MOTOR_INCOHERENTES")
    if not (0 <= td <= B64_06 and 0 <= tf <= B64_06):
        fallos.append("TESTIGO_FUERA_DEL_DOMINIO")
    if td == 0 and tf == 0 and sR > 0:
        fallos.append("TESTIGO_TASA_CERO_CON_VALOR_POSITIVO")
    if not (lo <= sR <= hi) or err < 0:
        fallos.append("VALOR_O_COTA_INCONSISTENTE")
    if r["level_values"] != [supf] or r["final_n"] < 1:
        fallos.append("SUP_R_DESVINCULADO")
    try:
        Bi, Iv = intervalo_bpot(raiz, m)
    except Rechazo as e:
        return fallos + [e.codigo], det
    det["Bi"] = [Bi.lo, Bi.hi]
    if not (Fr(Bi.lo) <= B <= Fr(Bi.hi)):
        fallos.append("NORMALIZACION_AJENA")
    q = Iv.point(supf) / Iv.point(Bf)
    if not (Fr(q.lo) <= C2 <= Fr(q.hi)):
        fallos.append("SUP_R_DESVINCULADO")
    e = Iv.point(errf) * Iv.point(Bf)
    if not (Fr(e.lo) <= eR <= Fr(e.hi)):
        fallos.append("ERROR_R_INCOHERENTE")
    lo_s, hi_s = (Iv.point(lof) / Bi).lo, (Iv.point(hif) / Bi).hi
    c2 = Iv.point(C2f)
    exigido = max(0.0, (Iv.point(hi_s) - c2).hi, (c2 - Iv.point(lo_s)).hi)
    exacto = max(Fr(0), hi / Fr(Bi.lo) - C2 if hi >= 0 else hi / Fr(Bi.hi) - C2, C2 - (lo / Fr(Bi.hi) if lo >= 0 else lo / Fr(Bi.lo)))
    det.update(exigido_coord=exigido, exigido_exacto=float(exacto), extremos_normalizados=[lo_s, hi_s])
    if not (err >= Fr(exigido) and err >= exacto):
        fallos.append("ERROR_NO_CUBRE_EXTREMOS")
    L = Fr(m["dominio"]["cota_inferior_b64"])
    if C2 + err < L:
        fallos.append("BAJO_LA_COTA_INFERIOR_B64")
    return fallos, det


def comprobar_modulos(m, r, modo):
    """Evidencia real de módulos: no vacía, cubre los módulos REQUERIDOS de la ruta real con su huella y todo módulo listado es un archivo
    fijado del núcleo con su huella. El entorno histórico declarado se compara aparte con el manifiesto (no es evidencia)."""
    fallos = []
    ev = r.get("evidencia_real") or {}
    mods = ev.get("modulos")
    req = m["modulos_ruta_real"]["archivos"]
    if not isinstance(mods, dict) or not mods or any(mods.get(k) != v for k, v in req.items()):
        fallos.append("MODULOS_INSUFICIENTES")
    elif any(m["nucleo"]["archivos"].get(k) != v for k, v in mods.items()):
        fallos.append("IDENTIDAD_DISTINTA")
    if r.get("entorno_historico_declarado") != m["payload"]["technical"]:
        fallos.append("ENTORNO_DECLARADO_DISTINTO")
    if modo == "produccion" and ev.get("garantia_plataforma") != PLATAFORMA:
        fallos.append("PLATAFORMA_NO_CERTIFICADA")
    if (ev.get("origen_modulos") == "sys.modules") != (modo == "produccion"):
        fallos.append("EVIDENCIA_DE_MODULOS_DE_OTRO_MODO")
    return fallos


def validar_resultado(raiz, m, manifiesto_sha, salida, modo, puerta_ev):
    """Valida RESULTADO.json de <salida> contra el manifiesto v2; nunca promueve. Devuelve (doc, fallos). rem140: lee los bytes UNA vez y
    delega en validar_bytes (la misma validación que aplica el lector a los bytes que incorpora)."""
    salida = Path(salida)
    resultados = sorted(p.name for p in salida.glob("RESULTADO*.json")) if salida.is_dir() else []
    rp = salida / "RESULTADO.json"
    raw = rp.read_bytes() if rp.exists() else None
    sp = salida / "RESULTADO.json.sha256"
    sello = sp.read_text(encoding="utf-8").split()[0] if sp.exists() and sp.read_text(encoding="utf-8").split() else None
    return validar_bytes(raiz, m, manifiesto_sha, raw, sello, len(resultados), modo, puerta_ev)


def validar_bytes(raiz, m, manifiesto_sha, raw, sello, n_resultados, modo, puerta_ev):
    """rem140 — validación común sobre los BYTES de un RESULTADO (o None si no hay), su sello y el número de RESULTADO* de la salida."""
    fallos, r, det = [], None, {}
    if n_resultados > 1:
        fallos.append("DUPLICADO")
    niveles = None
    if raw is not None:
        if sello != sha(raw):
            fallos.append("RESULTADO_ALTERADO")
        try:
            r = json.loads(raw)
        except ValueError:
            r = None
            fallos.append("RESULTADO_FUERA_DE_FORMATO")
        if r is not None and not isinstance(r, dict):
            r = None
            fallos.append("RESULTADO_FUERA_DE_FORMATO")
    clase = clasificar(r)
    if r is not None:
        fe, niveles = comprobar_estado(r)
        fallos += fe
        if r.get("clave") != m["clave"] or r.get("payload_sha256") != m["clave"]:
            fallos.append("CLAVE_AJENA")
        if r.get("manifiesto_sha256") != manifiesto_sha:
            fallos.append("MANIFIESTO_AJENO")
        if (r.get("puerta") or {}).get("alcance_sha256") != (puerta_ev or {}).get("alcance_sha256"):
            fallos.append("ALCANCE_AJENO")
        ejec, pa = (r.get("puerta") or {}).get("ejecutado") or {}, (puerta_ev or {}).get("piezas_alcance") or {}
        if not pa or any(ejec.get(n) != pa.get(n) for n in ("trabajador_testigo.py", "testigo_comun.py", "receta_testigo.sh")):
            fallos.append("TRABAJADOR_DISTINTO_DEL_ALCANCE")
        if modo == "produccion" and (r.get("modo") != "produccion" or r.get("proveedor_kind") != m["config"]["proveedor"] or r.get("sintetico")):
            fallos.append("NO_PRODUCTIVO")
        if modo == "fixture" and not r.get("sintetico"):
            fallos.append("FIXTURE_SIN_DOBLE")
        if (r.get("evidencia_real") or {}).get("archivos_fijados_sha256") != H(m["nucleo"]["archivos"]):
            fallos.append("IDENTIDAD_DISTINTA")
        fallos += comprobar_modulos(m, r, modo)
        fn, det = comprobar_numeros(raiz, m, r)
        fallos += fn
    garantia = (clase == "complete" and r is not None and r.get("error_kind") == "certified_bound" and isinstance(r.get("numerical_error_share"), float)
                and math.isfinite(r["numerical_error_share"]) and Fr(r["numerical_error_share"]) <= ERR_MAX)
    if clase == "complete" and not garantia:
        fallos.append("ERROR_INSUFICIENTE" if r.get("error_kind") == "certified_bound" else "ERROR_NO_CERTIFICADO")
    if clase in ("incomplete", "sup_not_attained", "sin_resultado"):
        fallos.append("NO_COMPLETO:" + clase)
    fallos = list(dict.fromkeys(fallos))
    cubre = []
    if garantia and not fallos:
        c = Fr(r["C2"]) - Fr(r["numerical_error_share"])
        cubre = [f["fila"] for f in m["cobertura_prevista"]["filas"] if Fr(f["v_exacto"]) <= c]
    doc = {"kind": "validacion-testigo-alto-c3-v3", "modo": modo, "clave": m["clave"], "manifiesto_sha256": manifiesto_sha, "clase": clase,
           "cumple_garantia": bool(garantia and not fallos), "fallos": fallos, "promueve": False, "detalle_numerico": det, "estado_motor": niveles,
           "evidencia_modulos": "sys.modules del proceso real" if modo == "produccion" else "declarada por el doble SINTÉTICO (fixture)",
           "filas_cuya_mitad_superior_cubriria": cubre,
           "nota": "solo la mitad superior (v <= C2 - err); la inferior exige el testigo inferior aceptado de la enmienda v2; ninguna fila se suma a "
                   "producción ni a C2 sin enmienda de autoridad de fuentes, alcance, acto y dictamen",
           "resultado_sha256": sha(raw) if raw is not None else None,
           "validada_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    return doc, fallos
