"""rem163 — PIEZA COMÚN del paquete B1 (PROD4.5.6, doce COV). Deriva en forma de paquete_p7/comun_p7.py (rem153, 3702da39…, aceptado
por el dictamen rem154 b83ddf7c… y usado en la producción aceptada por rem155 6e75b350…). Sin cálculo científico propio. Contiene:
- FUENTES fijadas por ruta y sha256 (leer() autentica los bytes que entrega, una sola lectura);
- la raíz D7 EXACTA de los tres conjuntos ABL-COV en decimal y su encierro binary64 HACIA AFUERA (la caja binaria contiene la decimal; un
  decimal representable queda igual): no se cambia el dominio al redondear;
- construir_manifiesto(): reconstrucción completa del manifiesto B1 desde las fuentes (afirmaciones, grupos, K1_testigo, raíz, fijos, menú,
  C0, configuración auténtica y contrato de salida); validar_manifiesto() exige igualdad canónica EXACTA en producción;
- cargar_cierre_c0(): carga los once archivos del cierre C0 desde SUS BYTES autenticados (leídos una vez, compilados desde esos mismos bytes),
  rechaza cualquier paper2b ya presente en sys.modules (un módulo precargado de otra ruta no puede prevalecer), deja el paquete sin __path__
  (ningún submódulo fuera del cierre puede importarse) y comprueba la identidad de cada objeto registrado;
- espias(): contador de la ÚNICA solicitud a c2_normalizado, espía de EM.sup_bound (pasa sin cambiar argumentos ni resultado) y bloqueadores
  que lanzan excepción en toda otra entrada científica (fallback c2_struct_enclosure, capture_ceiling, cobertura, supremos, frontier…);
- validar_evidencia(): VALIDACIÓN ÚNICA de la evidencia del trabajo (la misma para validador, conductor y cotejos);
- lectura(): regla exacta con eps = 1/100 sobre los seis K1_testigo, una fila por grupo y correspondencia con las doce.
rem164 (corrección P4-B1-CONTINUIDAD-PROCEDENCIA): procedencia() es la ÚNICA comprobación de origen, compartida por el validador (entrada
directa) y por la continuación del conductor. Autentica primero la FUENTE DE EJECUCIÓN y después entrega exactamente los bytes ligados a ella;
validar_evidencia() (contenido) no cambia. Fuentes: «lanzamiento» (ronda en curso: registro p3ctl del área y salida del trabajador copiada por
el supervisor) y «previo» (entre rondas: SOLO una fuente fijada por autoridad independiente del llamador; en producción no existe todavía y se
rechaza; en sintético la autoridad es un FIXTURE de ruta fija que nunca habilita producción).
rem165 (residuo de P4-B1-CONTINUIDAD-PROCEDENCIA): la comprobación de la ejecución del trabajo y la de la directa propia del validador ya no
buscan un token con el nombre del script en cualquier posición del argv. _invocacion() exige la ORDEN COMPLETA registrada por p3ctl, con el
mismo criterio para ambos: intérprete autorizado por ruta e identidad, -B -I -X utf8 en su posición, el script de este paquete en posición de
programa y después solo los argumentos de la operación (sin prefijos, envoltorios, -c, -m, stdin ni opciones de más), con el cwd autenticado y
una normalización de rutas Windows declarada (ruta_windows). El resto de la procedencia y la validación de contenido no cambian.
Importable; no escribe nada."""
import csv
import datetime as dt
import hashlib
import importlib.machinery
import io
import json
import math
import sys
import types
from fractions import Fraction
from pathlib import Path

AQUI = Path(__file__).resolve().parent
Y = AQUI.parent
R = AQUI.parents[2]
T = R / "tmp"
W = Path(r"@@W_WIN@@")
H = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
HF = lambda p: H(Path(p).read_bytes())  # noqa: E731


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


C0 = T / "paso4_raices_impacto_desde_rem116/candidato_c0/instalacion"
C0_SRC = C0 / "src"
C0_IDENTIDAD = "d0bf5cd6e413ae4dcdd18eafb0bf7269cac22a487b4d46cb6b1737b5e5c971ae"
C0_INVENTARIO_SHA = "609c6e4dc98cbb8e900e9fe5441feeaf506e22957947c927fb6073cec1cdba4a"
AA_SHA = "631003ca87989ccd0189b33c9bd35e338a6f16fe4a0d50cbc2ccef0ee6f96467"      # C0 herramientas/b/aprobacion_alcance.py
P3CTL_SHA = "546271b057a9635ab39ca3f94e0fd79da46cc7091a4bff873ab8c54e6d875841"
L = T / "paso4_puerta_continuidad_cov_desde_rem150/paquete_cov_i5"
REFDEC_SHA = "039f6f6b490c81bd553f1a5c07fec848f15a8cdf0f6c70e6782511140abe7446"   # paquete_cov_i5/referencia_decision.py
X162 = T / "paso4_preparacion_precisa_doce_cov_desde_rem162"
X161 = T / "paso4_dimensionamiento_doce_cov_desde_rem161"
D7 = R / "salidas_s6/d7/versions/2a25893b09c097b2af22ed2e5be9a4014851faf55bbaaf380c7a078f1a740591"
# Cierre de importación de la pieza B1 en C0 (X/preparacion/PREPARACION_B1_B2.json cc734652…; inventario rem116 609c6e4d…).
CIERRE_C0 = {
    "c2_normalizado.py": "31d247eeb0368a38aa90ea8c262e3ea55cdfa62d312fe68024969b54670ab785",
    "encierros_modelo.py": "549228d005ec77888ff467259b9846c0213d667923559e2e020706194e3acb53",
    "model.py": "b8541045ce2db793e3acfba5e84053edc185a7f8cdfc5c1b535d1452ebde9b04",
    "elementales.py": "c71faf35370fa2329db69802f03f52d9bc72566a2d9fa50a9ca8dbea1eb6f82b",
    "intervalos.py": "2607d0cf3f879316c699ec4cd73021bff9ae8f680f7c7c01facb84dfb65aa891",
    "supremum.py": "2c246c8be6d4437892cd951cc0acaaac6e5d8ea7a921de2e13f560caf8dfebbb",
    "numeric.py": "4b19f4cb45a637c3a3370ca95059bc4f94feb71649a9f54fd5ac8c33c941c98e",
    "modelos.py": "7f0dd31cacf431fb421e2c5047aa5b750cbecfc1064e3374c4247dcd40c93fda",
    "frontier.py": "709f51b21188ff8d4638d7eadf535dd3f8307f2e1ce995a49539fe7bfcd36ed2",
    "cobertura.py": "d6be53db849fbfaa1d11c3213cc25a0f86a990ef6b3198e36e6b56607f5d9381",
    "__init__.py": "89f7210e7c118c83eec9d73323491e0d8c778b76d1297f703dfca2b86069c72a",
}
# Orden de carga compatible con las importaciones de cada archivo (todas resueltas desde sys.modules, nunca desde disco).
ORDEN_CARGA = ("numeric", "intervalos", "elementales", "model", "supremum", "frontier", "encierros_modelo", "modelos", "cobertura", "c2_normalizado")
FUENTES = {
    "dictamen_rem163": (W / "review_20261107_rem163_dictamen.txt", "39a59bd7b9097962bfed21a42b98650142bdc250ad8a17e33262215424abc6e0"),
    "hallazgos_rem163": (W / "review_20261107_rem163_findings.json", "93b32afdb309799988b8d7ac10fa9693a5228614f7fb3d30ba40c00627c68cf9"),
    "libro_exp8_rem161": (W / "review_20261106_rem161_EXP8_sintesis_aceptada.json", "0d84eb80d10ad530f222ca4b38c5e5ef86be1fcf7afde604243012a3cdd7e707"),
    "cov_aceptada_rem152": (W / "review_20261105_rem152_COV_aceptada.json", "accdf8abd212e41ea34719853ec36ba09f3a0f1e54b3309ec6925a018eb1490c"),
    "x162_inventario": (X162 / "audit/entrega.json", "0ac16b19b91deda3c302f9c82b3be08a653576af20e998a07230cc0b2b026ab7"),
    "x162_preparacion_b1_b2": (X162 / "preparacion/PREPARACION_B1_B2.json", "cc73465290d490f14a2b896ad89f6e4e42ca24480c182ea25958d4a2db0dd416"),
    "x162_contexto_col": (X162 / "soporte/CONTEXTO_COL_POR_GRUPO.json", "5821bb3dae7d4c4dc93e8e956da8984dfeec931587b16b8e7329231c8819d810"),
    "x162_conexion_b1": (X162 / "preparacion/CONEXION_B1.py", "43c1dfceef2910ff72664c0bbd308d1c7215791eee84cc36db8b839db59d882f"),
    "x161_inventario": (X161 / "audit/entrega.json", "a43d361e894adc1fd69960d188b8b387922bdd5a955270fe60ce4d1d4d9f188c"),
    "x161_plan": (X161 / "dimensionamiento/PLAN_MINIMO_PROPUESTO.json", "233053d01c7a262a9d326a014b45477f2be345916c2b02899e4561b32fe2cf1c"),
    "entrega_rem151": (T / "paso4_produccion_cov_desde_rem151/audit/entrega.json", "8b5b5202f85a01768a0eb27e85172e691e811f3a3ca491f7d0991ddedb6a5570"),
    "cov_conciliacion_rem151": (T / "paso4_produccion_cov_desde_rem151/cov_REM151_COV/CONCILIACION/CONCILIACION_COV.jsonl",
                                "5ba0142304deb949777ad3ae3443556250f2237d214cb4e4fb0d427aa5ea049f"),
    "d7_manifest": (D7 / "d7_manifest.json", "9faf63c3ce96ec0e18b7cbf6235bdf21fc6e8bd18ce2ed054e3eb7f7b3a04ff9"),
    "d7_support_set": (D7 / "support_set.csv", "91716f572a85dae4e57290efb3dad03ada588d7a6cfe037fd2e1ae5d40bd61c6"),
    "d7_tau_domains": (D7 / "tau_domains.csv", "c39aa30fc0fdb44fb9d0c32d66bc001d901fdeae9fb6f3c27874c21a1d0b0e6f"),
    "c0_inventario_rem116": (T / "paso4_raices_impacto_desde_rem116/audit/entrega.json", C0_INVENTARIO_SHA),
    "c0_run_py": (C0_SRC / "paper2b/run.py", "18abae7000d727c88dc7693db59c75a20ea79db7031b0c2e510d2b3af0058360"),
    "cov_i5_tarea_lote": (L / "tarea_lote.py", "9ba4ce357423167dc34a2ae1c15517b053fd3e33f7fef3720d14f9941bd8d1b1"),
    "cov_i5_preparar_manifiesto": (L / "preparar_manifiesto_cov.py", "185ec1b26459dfa37d4bcc6dfb48b796824e2fe0db528e8913550d0d1d6d0681"),
}
CONJUNTOS_COV = ("CMP-E1.macro.ABL-COV", "COL-E2-2023.2023p.macro.ABL-COV", "COL-E2-2023.2024p.macro.ABL-COV")
STRUCT = ("a", "beta_tilde", "eta_d", "eta_f", "kappa_tilde", "phi", "rho", "u_theta", "z_cost")
FIJOS = ("c_legal", "gamma", "t", "z_m")
COTAS = ("bar_tau_d", "bar_tau_f")
RAIZ_ESPERADA = {"a": ("1.1", "2.5"), "beta_tilde": ("0.25", "4"), "eta_d": ("0.1", "4"), "eta_f": ("0.1", "8"), "kappa_tilde": ("0.005", "0.2"),
                 "phi": ("0", "0.5"), "rho": ("0.4", "1"), "u_theta": ("0.1", "0.9"), "z_cost": ("1", "100")}
FIJOS_ESPERADOS = {"c_legal": "1", "gamma": "1", "t": "0", "z_m": "1"}
COTAS_ESPERADAS = {"bar_tau_d": "0.6", "bar_tau_f": "0.6"}
MENU, DISENO, EPS = "f", "G", Fraction(1, 100)
GARANTIA = "ieee754_binary64_rn"
CONFIG_ESPERADA = {"proveedor": "modelo_teorico_v2_2", "param_budget_s": 3600.0, "struct_tol": 1e-4, "struct_max_boxes": 400,
                   "sup_max_boxes": 20000, "jump_budget_modelo": 600, "jump_budget_encierro": 0, "certificado": True, "garantia": GARANTIA}
TAREA_TRABAJO, TAREA_VALIDACION = "B1-TRABAJO", "B1-VALIDACION"
KIND_MAN = "manifiesto-b1-doce-cov-rem163"


class B1Error(RuntimeError):
    pass


def leer(nombre):
    """Lee UNA vez los bytes de una fuente fijada y los autentica; devuelve (bytes, sha)."""
    p, h = FUENTES[nombre]
    b = Path(p).read_bytes()
    if H(b) != h:
        raise B1Error("FUENTE_NO_AUTENTICA:%s:%s" % (nombre, H(b)[:16]))
    return b, h


def jsonl(b):
    return [json.loads(x) for x in b.decode("utf-8").splitlines() if x.strip()]


# ------------------------------------------------------------------------------------------------ convención decimal → binary64
def binario_afuera(dec, lado):
    """Extremo binary64 dirigido HACIA AFUERA del decimal exacto: lado 'lo' → mayor binary64 <= decimal; 'hi' → menor binary64 >= decimal."""
    q = Fraction(dec)
    f = float(q)
    if lado == "lo" and Fraction(f) > q:
        f = math.nextafter(f, -math.inf)
    if lado == "hi" and Fraction(f) < q:
        f = math.nextafter(f, math.inf)
    assert (Fraction(f) <= q) if lado == "lo" else (Fraction(f) >= q)
    return f


def iv_bin(lo, hi):
    a, b = binario_afuera(lo, "lo"), binario_afuera(hi, "hi")
    return {"lo": a, "hi": b, "lo_hex": float.hex(a), "hi_hex": float.hex(b), "lo_exacto": Fraction(lo) == Fraction(a), "hi_exacto": Fraction(hi) == Fraction(b)}


def caja_de(man):
    """Caja, fijos y cotas BINARIAS que fija el manifiesto (la única autoridad de la solicitud)."""
    rb = man["raiz"]["binario"]
    caja = {p: (rb[p]["lo"], rb[p]["hi"]) for p in STRUCT}
    fijos = {k: man["fijos"]["binario"][k] for k in FIJOS}
    bd, bf = man["cotas_tasas"]["binario"]["bar_tau_d"], man["cotas_tasas"]["binario"]["bar_tau_f"]
    return caja, fijos, bd, bf


def iguales_bits(a, b):
    return isinstance(a, float) and isinstance(b, float) and float.hex(a) == float.hex(b)


# ------------------------------------------------------------------------------------------------ manifiesto desde fuentes
def _filas_d7():
    b, _ = leer("d7_support_set")
    filas = {}
    for r in csv.DictReader(io.StringIO(b.decode("utf-8"))):
        if r["support_set_id"] in CONJUNTOS_COV:
            filas.setdefault((r["support_set_id"], r["parameter_id"]), []).append(r)
    return filas


def _menu_d7():
    b, _ = leer("d7_tau_domains")
    out = {}
    for r in csv.DictReader(io.StringIO(b.decode("utf-8"))):
        if r["support_set_id"] in CONJUNTOS_COV and r["instrument_j"] == MENU:
            out[r["support_set_id"]] = r
    return out


def _lineas(nombre, esperadas):
    b, h = leer(nombre)
    ls = b.decode("utf-8").splitlines()
    ev = {}
    for n, txt in esperadas.items():
        if ls[n - 1].strip() != txt:
            raise B1Error("LINEA_DE_CONFIGURACION_DISTINTA:%s:%d" % (nombre, n))
        ev[str(n)] = txt
    return {"fuente": nombre, "sha256": h, "lineas": ev}


def construir_manifiesto():
    """Manifiesto B1 REAL reconstruido desde las fuentes fijadas. Lanza B1Error si una fuente no es auténtica o no concuerda."""
    fuentes = {k: {"ruta": str(p), "sha256": h} for k, (p, h) in sorted(FUENTES.items())}
    for k in FUENTES:
        leer(k)
    # 1. raíz D7 exacta, idéntica en los tres conjuntos ABL-COV
    filas = _filas_d7()
    d7 = {}
    for cj in CONJUNTOS_COV:
        d7[cj] = {}
        for p in STRUCT + FIJOS + COTAS:
            rs = [r for r in filas.get((cj, p), []) if r["variant_id"] in ("primary", "fixed")]
            if len(rs) != 1:
                raise B1Error("FILA_D7_NO_UNICA:%s:%s" % (cj, p))
            r = rs[0]
            if r["lower_closed"] != "true" or r["upper_closed"] != "true":
                raise B1Error("EXTREMO_D7_ABIERTO:%s:%s" % (cj, p))
            d7[cj][p] = {"support_id": r["support_id"], "domain_kind": r["domain_kind"], "lower": r["lower"], "upper": r["upper"],
                         "variant_id": r["variant_id"], "fila_sha256": H(canon(r))}
    ref = {p: (d7[CONJUNTOS_COV[0]][p]["lower"], d7[CONJUNTOS_COV[0]][p]["upper"]) for p in STRUCT + FIJOS + COTAS}
    for cj in CONJUNTOS_COV:
        for p in STRUCT + FIJOS + COTAS:
            if (d7[cj][p]["lower"], d7[cj][p]["upper"]) != ref[p]:
                raise B1Error("RAIZ_DISTINTA_ENTRE_CONJUNTOS:%s:%s" % (cj, p))
    for p in STRUCT:
        if d7[CONJUNTOS_COV[0]][p]["domain_kind"] != "continuous" or Fraction(ref[p][0]) != Fraction(RAIZ_ESPERADA[p][0]) \
                or Fraction(ref[p][1]) != Fraction(RAIZ_ESPERADA[p][1]):
            raise B1Error("RAIZ_D7_DISTINTA_DE_LA_ENCARGADA:" + p)
    for k, v in list(FIJOS_ESPERADOS.items()) + list(COTAS_ESPERADAS.items()):
        if ref[k] != (v, v):
            raise B1Error("FIJO_O_COTA_D7_DISTINTO:" + k)
    menu = _menu_d7()
    if sorted(menu) != sorted(CONJUNTOS_COV):
        raise B1Error("MENU_F_AUSENTE_EN_D7")
    menu_rows = {}
    for cj, r in menu.items():
        zs = [x for x in filas.get((cj, "tau_d"), []) if x["support_id"] == r["tau_d_support_id"]]
        fs = [x for x in filas.get((cj, "tau_f"), []) if x["support_id"] == r["tau_f_support_id"]]
        if len(zs) != 1 or len(fs) != 1 or (zs[0]["lower"], zs[0]["upper"]) != ("0", "0") or (fs[0]["lower"], fs[0]["upper"]) != ("0", "0.6") \
                or fs[0]["lower_closed"] != "true" or fs[0]["upper_closed"] != "true":
            raise B1Error("MENU_F_D7_DISTINTO:" + cj)
        menu_rows[cj] = {"tau_domain_id": r["tau_domain_id"], "tau_d": {"support_id": zs[0]["support_id"], "lower": "0", "upper": "0"},
                         "tau_f": {"support_id": fs[0]["support_id"], "lower": "0", "upper": "0.6"}, "fila_sha256": H(canon(r))}
    # premisas de dominio de B1, exactas sobre la raíz decimal (no cambian el dominio)
    q = {p: (Fraction(ref[p][0]), Fraction(ref[p][1])) for p in STRUCT}
    premisas = {"a_lo_mayor_1": q["a"][0] > 1, "rho_en_0_1": q["rho"][0] > 0 and q["rho"][1] <= 1, "a_lo_mayor_rho_hi": q["a"][0] > q["rho"][1],
                "u_theta_en_0_1_abierto": q["u_theta"][0] > 0 and q["u_theta"][1] < 1,
                "kappa_beta_z_eta_positivos": all(q[p][0] > 0 for p in ("kappa_tilde", "beta_tilde", "z_cost", "eta_d", "eta_f")),
                "phi_en_0_un_medio": q["phi"] == (Fraction(0), Fraction(1, 2)), "gamma_z_m_puntuales_positivos": True,
                "normalizado_aplicable": q["a"][0] > 1}
    binario = {p: iv_bin(*ref[p]) for p in STRUCT}
    bq = {p: (Fraction(binario[p]["lo"]), Fraction(binario[p]["hi"])) for p in STRUCT}
    premisas_bin = {"a_lo_mayor_1": bq["a"][0] > 1, "rho_hi_le_1": bq["rho"][1] <= 1, "a_lo_mayor_rho_hi": bq["a"][0] > bq["rho"][1],
                    "u_theta_hi_lt_1": bq["u_theta"][1] < 1, "positivos": all(bq[p][0] > 0 for p in ("kappa_tilde", "beta_tilde", "z_cost", "eta_d", "eta_f")),
                    "contiene_decimal": all(bq[p][0] <= q[p][0] and bq[p][1] >= q[p][1] for p in STRUCT)}
    if not all(premisas.values()) or not all(premisas_bin.values()):
        raise B1Error("PREMISAS_DE_DOMINIO_B1_NO_SE_CUMPLEN")
    # 2. afirmaciones (CONTEXTO_COL_POR_GRUPO rem162), grupos (PLAN rem161) y K1_testigo (CONCILIACION_COV rem151 aceptada por rem152)
    ctx = json.loads(leer("x162_contexto_col")[0])
    plan = json.loads(leer("x161_plan")[0])
    prep = json.loads(leer("x162_preparacion_b1_b2")[0])
    filas_cov = {x["afirmacion"]: x for x in jsonl(leer("cov_conciliacion_rem151")[0])}
    k1_prep = prep["B1"]["lectura_futura"]["K1_testigo_por_grupo"]
    grupos_plan = plan["deduplicacion"]["grupos_K1"] if "deduplicacion" in plan else plan["grupos_K1"]
    por_af = {}
    for e in ctx["por_afirmacion"]:
        por_af[e["afirmacion"]] = sorted({(c["conjunto_COV"], c.get("edicion")) for c in e["conjuntos"]})
    grupos, afirmaciones = [], []
    for g in sorted(grupos_plan, key=lambda x: x["grupo"]):
        vals = list(g["K1_testigo_sup"])
        if len(vals) != 1 or len(g["afirmaciones"]) != 2 or vals != list(g["K1_minimo_guardado"]):
            raise B1Error("GRUPO_K1_NO_UNIVOCO:" + g["grupo"])
        k1 = vals[0]
        if not (isinstance(k1, float) and k1_prep.get(g["grupo"]) == k1):
            raise B1Error("K1_TESTIGO_DISTINTO_DE_REM162:" + g["grupo"])
        disenos = []
        for a in sorted(g["afirmaciones"]):
            fr = filas_cov.get(a)
            if fr is None or fr["sup"]["K1"] != k1 or a not in por_af:
                raise B1Error("AFIRMACION_SIN_FUENTE_O_K1_DISTINTO:" + a)
            d = a.split(":")[7]
            disenos.append(d)
            afirmaciones.append({"afirmacion": a, "grupo": g["grupo"], "diseno": d, "pid": g["pid"], "kind": g["kind"], "cota": g["cota"],
                                 "conjuntos_COV": [{"conjunto": c, "edicion": ed} for c, ed in por_af[a]],
                                 "K1_testigo": k1, "K1_testigo_hex": float.hex(k1),
                                 "fuente_K1": {"fuente": "cov_conciliacion_rem151", "lado": "sup", "cell_id": fr["sup"]["cell_id"],
                                               "clave_cov": fr["sup"]["clave_cov"], "unidad": fr["sup"]["unidad"], "K1": fr["sup"]["K1"]}})
        if sorted(disenos) != ["G", "N"]:
            raise B1Error("GRUPO_SIN_PAR_G_N:" + g["grupo"])
        grupos.append({"grupo": g["grupo"], "afirmaciones": sorted(g["afirmaciones"]), "K1_testigo": k1, "K1_testigo_hex": float.hex(k1),
                       "K1_testigo_exacto": str(Fraction(k1)), "umbral_exacto": str(Fraction(k1) - EPS), "cota": g["cota"], "kind": g["kind"],
                       "pid": g["pid"], "estados_nacionales": list(g["estados_nacionales"])})
    if len(afirmaciones) != 12 or len({a["afirmacion"] for a in afirmaciones}) != 12 or len(grupos) != 6 or set(por_af) != {a["afirmacion"] for a in afirmaciones}:
        raise B1Error("NO_SON_DOCE_AFIRMACIONES_Y_SEIS_GRUPOS")
    # 3. configuración auténtica del ModeloTeorico: RunConfig() por defecto de la ruta aceptada (COV i5) → provider_for → ModeloTeorico
    config_ev = [_lineas("c0_run_py", {57: "INVERSION_BUDGET_DEFAULT_S = 3600.0", 109: "inversion_budget_seconds: float = INVERSION_BUDGET_DEFAULT_S",
                                       127: "return ModeloTeorico(param_budget_s=cfg.inversion_budget_seconds)"}),
                 _lineas("cov_i5_tarea_lote", {136: "cfg = RUN.RunConfig()", 137: "model = RUN.provider_for(cfg)"}),
                 _lineas("cov_i5_preparar_manifiesto", {48: "cfg = RUN.RunConfig()", 49: "prov = RUN.provider_for(cfg)"})]
    man = {
        "kind": KIND_MAN, "modo": "produccion",
        "naturaleza": "MANIFIESTO REAL DOCUMENTAL del paquete B1 (rem163): fija UNA solicitud futura; no es un alcance ni una autorización",
        "operacion": "B1",
        "solicitud": {"funcion": "paper2b.c2_normalizado.c2_normalizado", "diseno": DISENO, "comparten": ["G", "N"], "j": MENU,
                      "clase_c2": "GN (cobertura.clase_c2, menu f)", "solicitudes": 1, "segunda_llamada_N": False, "B2_encadenado": False,
                      "contrato": "c2_normalizado(model, box, 'G', 'f', bar_tau_d, bar_tau_f, fixed=fijos, stats=...) como cobertura.c2_encierro (cobertura.py:142-155)"},
        "afirmaciones": afirmaciones, "grupos": grupos,
        "raiz": {"decimal": {p: list(ref[p]) for p in STRUCT}, "binario": binario, "filas_D7": d7, "conjuntos": list(CONJUNTOS_COV),
                 "premisas_decimal": premisas, "premisas_binario": premisas_bin,
                 "box_admissible_ingenuo": "cobertura.box_admissible es falso en la raiz porque q_pot ingenuo da q.hi = 3 (a dos veces); "
                                           "condiciona g_enclosure/B2, no c2_normalizado; el rango exacto [1/1400, 1/5] es de rem162"},
        "fijos": {"decimal": dict(FIJOS_ESPERADOS), "binario": {k: float(Fraction(v)) for k, v in FIJOS_ESPERADOS.items()}},
        "cotas_tasas": {"decimal": dict(COTAS_ESPERADAS), "binario": {k: binario_afuera(v, "hi") for k, v in COTAS_ESPERADAS.items()},
                        "binario_hex": {k: float.hex(binario_afuera(v, "hi")) for k, v in COTAS_ESPERADAS.items()}},
        "menu": {"j": MENU, "tau_d": "0", "tau_f": ["0", "0.6"], "filas_D7": menu_rows,
                 "dominio_motor": "supremum.axes('f', bd, bf) = ((0,0),(0,bf)); bf = binary64 hacia afuera de 0.6"},
        "convencion": {"autoridad": "los decimales D7 son el dominio exacto; nunca se redondea hacia dentro",
                       "binario": "cada extremo inferior es el mayor binary64 <= decimal y cada superior el menor binary64 >= decimal; un decimal "
                                  "representable queda igual; la caja binaria CONTIENE la raiz decimal (sup sobre la caja >= sup sobre el dominio)",
                       "cotas": "bar_tau_f entra solo por supremum.axes (dominio de tau_f): su extremo superior se dirige hacia afuera igual",
                       "fijos": "1, 1, 0, 1 son exactos en binary64",
                       "diferencia_con_rem162": "CONEXION_B1.caja_raiz_desde_ejes usaba float() (al mas cercano), que estrecha a, kappa_tilde, eta_d, "
                                                "eta_f, rho y u_theta en su lado; aqui se corrige hacia afuera sin cambiar el dominio decimal"},
        "c0": {"ruta": str(C0), "identidad": C0_IDENTIDAD, "inventario_rem116_sha256": C0_INVENTARIO_SHA, "cierre": dict(CIERRE_C0),
               "orden_carga": list(ORDEN_CARGA), "lector_aprobacion_sha256": AA_SHA,
               "nota": "model.py de C0 (b8541045…) no es el de la instalacion (24af1c42…); se usa SOLO el de C0"},
        "modelo": {"clase": "paper2b.modelos.ModeloTeorico", "construccion": "ModeloTeorico(param_budget_s=3600.0) = run.provider_for(run.RunConfig())",
                   "configuracion": dict(CONFIG_ESPERADA), "evidencia_configuracion": config_ev,
                   "tolerancia_encierro": "max(struct_tol*gamma, ancho(c0)) en unidades de R/mu (c2_normalizado.py:97-98)",
                   "tope": "EM.sup_bound(..., max_boxes=struct_max_boxes=400, jump_budget=0): tope determinista de cajas de tasas; la cota superior "
                           "de las cajas vivas sigue siendo demostrada aunque se alcance el tope"},
        "plataforma": {"garantia": GARANTIA, "comprobacion": "paper2b.elementales.PLATAFORMA al importar (controles binary64, redondeo, division, "
                                                            "subnormales, nextafter); sin ella model.certified es falso y no hay resultado valido"},
        "escala": "normalizada: C2 = sup_tau Rn / gamma, Rn = R/mu (c2_normalizado); stats['normalizado'] debe ser True",
        "contrato_salida": {"evidencia": "EVIDENCIA_B1.json (trabajo)", "salida_derivada": "LECTURA_B1.json (validador)",
                            "verificacion": "VALIDACION_B1.json (validador)", "U_C2": "extremo superior EXACTO del intervalo normalizado devuelto",
                            "valido": "intervalo finito y ordenado, normalizado, una solicitud, un sup_bound, sin llamadas bloqueadas",
                            "invalido": "None, NaN, infinito, invertido, plataforma no conforme, excepcion, tiempo agotado o cierre no conforme"},
        "lectura": {"eps": "1/100", "regla_detener": "U_C2 > K1_testigo - 1/100: la cota separable de raiz no puede certificar el grupo; se detiene esta via",
                    "regla_candidato": "U_C2 <= K1_testigo - 1/100: candidato a B2; falta una cota inferior global K1 valida",
                    "invalido": "sin lectura cientifica valida", "no_clasifica": True},
        "prohibido": ["centro/hijas estructurales", "ranking", "refinamiento", "cobertura M4/M5", "busqueda de testigos", "cobertura_compartida completo",
                      "transferir valor/universo/aceptacion de cobertura5", "S6", "estado nacional", "bridge", "Q", "K1 nuevo", "B2"],
        "fuentes": fuentes,
    }
    return man


_CONSTRUIDO = {}


def diferencias(a, b, ruta="", n=12):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(ruta + "/" + str(k))
            else:
                out += diferencias(a[k], b[k], ruta + "/" + str(k), n)
            if len(out) >= n:
                break
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diferencias(x, y, "%s[%d]" % (ruta, i), n)
            if len(out) >= n:
                break
    elif a != b or type(a) is not type(b):
        out.append(ruta or "/")
    return out[:n]


def es_fixture(man):
    k = str(man.get("kind", ""))
    return k.endswith("-SINTETICO") or "FIXTURE" in k


def validar_manifiesto(man):
    """Lista de fallos (vacía = conforme). Producción real: igualdad canónica EXACTA con construir_manifiesto(). Sintético: kind …-SINTETICO,
    modo sintetico, doble declarado y el MISMO contenido documental que el real (salvo kind/modo/naturaleza/doble). Puerta (kind con FIXTURE,
    modo producción): solo estructura; la puerta común lo rechaza en producción aunque hubiese decisión."""
    f = []
    k = str(man.get("kind", ""))
    sint = k.endswith("-SINTETICO")
    if (man.get("modo") == "sintetico") != sint or man.get("modo") not in ("produccion", "sintetico"):
        return ["MANIFIESTO_MEZCLA_REAL_SINTETICO"]
    try:
        if "doc" not in _CONSTRUIDO:
            _CONSTRUIDO["doc"] = construir_manifiesto()
        exp = _CONSTRUIDO["doc"]
    except (B1Error, OSError, KeyError, ValueError, TypeError, AssertionError) as ex:
        return ["FUENTES_DEL_MANIFIESTO_NO_AUTENTICAS: %s" % str(ex)[:160]]
    if not sint and "FIXTURE" not in k:
        if canon(man) != canon(exp):
            f.append(("PROCEDENCIA_DISTINTA_DE_LAS_FUENTES", diferencias(man, exp)))
        return f
    fijo = {x: v for x, v in exp.items() if x not in ("kind", "modo", "naturaleza")}
    for x, v in fijo.items():
        if canon(man.get(x)) != canon(v):
            f.append(("CONTENIDO_DISTINTO_DEL_REAL", x))
    extra = sorted(set(man) - set(exp) - {"doble"})
    if extra:
        f.append(("CAMPO_INESPERADO", extra))
    if sint:
        d = man.get("doble") or {}
        if not (k == KIND_MAN + "-SINTETICO" and isinstance(d.get("sha256"), str) and d.get("ruta") == "pruebas/doble_b1.py"
                and isinstance(d.get("comportamiento"), str)):
            f.append("DOBLE_NO_DECLARADO")
    elif "doble" in man:
        f.append("DOBLE_EN_MANIFIESTO_DE_PUERTA")
    return f


# ------------------------------------------------------------------------------------------------ cierre C0 con identidad de módulos
def cargar_cierre_c0(src=None, cierre=None):
    """Carga paper2b desde los bytes AUTENTICADOS de los once archivos del cierre (src/paper2b), sin sys.path. Devuelve (modulos, identidad)."""
    src = Path(src or C0_SRC) / "paper2b"
    cierre = dict(cierre or CIERRE_C0)
    pre = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if pre:
        raise B1Error("MODULO_PRECARGADO:%s" % pre[:4])
    nombres_std = {"BuiltinImporter", "FrozenImporter", "PathFinder"}
    mp = [getattr(x, "__name__", type(x).__name__) for x in sys.meta_path]
    if not set(mp) <= nombres_std:
        raise B1Error("META_PATH_AJENO:%s" % mp)
    if sorted(cierre) != sorted([n + ".py" for n in ORDEN_CARGA] + ["__init__.py"]):
        raise B1Error("CIERRE_INCOMPLETO")
    datos = {}
    for n, h in cierre.items():
        b = (src / n).read_bytes()
        if H(b) != h:
            raise B1Error("CIERRE_C0_DISTINTO:%s" % n)
        datos[n] = b
    creados = {}

    def nuevo(nombre, archivo, paquete):
        m = types.ModuleType(nombre)
        m.__file__ = str(src / archivo)
        m.__package__ = "paper2b"
        m.__spec__ = importlib.machinery.ModuleSpec(nombre, None, origin=str(src / archivo), is_package=paquete)
        if paquete:
            m.__path__ = []           # sin ruta: ningún submódulo fuera del cierre puede cargarse desde disco
            m.__spec__.submodule_search_locations = []
        sys.modules[nombre] = m
        creados[nombre] = m
        exec(compile(datos[archivo], str(src / archivo), "exec", dont_inherit=True), m.__dict__)
        return m
    try:
        pkg = nuevo("paper2b", "__init__.py", True)
        for n in ORDEN_CARGA:
            setattr(pkg, n, nuevo("paper2b." + n, n + ".py", False))
    except Exception:
        for k in creados:
            sys.modules.pop(k, None)
        raise
    actuales = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if actuales != sorted(creados) or any(sys.modules[k] is not v for k, v in creados.items()):
        raise B1Error("IDENTIDAD_DE_MODULOS_DISTINTA")
    ident = {k: {"archivo": "src/paper2b/" + Path(v.__file__).name, "sha256": cierre[Path(v.__file__).name], "registrado_es_el_cargado": True}
             for k, v in sorted(creados.items())}
    return {k.split(".")[-1] if "." in k else k: v for k, v in creados.items()}, {"modulos": ident, "meta_path": mp, "precargados": pre,
                                                                                   "fuente_bytes": "compilados desde los bytes autenticados"}


def comprobar_identidad(mods, ident):
    """Re-comprueba, después de usar la pieza, que las funciones efectivas pertenecen a los módulos cargados y que nada nuevo de paper2b apareció."""
    f = []
    act = sorted(m for m in sys.modules if m == "paper2b" or m.startswith("paper2b."))
    if act != sorted(ident["modulos"]):
        f.append(("MODULOS_PAPER2B_DISTINTOS", act))
    for k, v in ident["modulos"].items():
        if sys.modules.get(k) is None or Path(sys.modules[k].__file__).name != Path(v["archivo"]).name:
            f.append(("MODULO_SUSTITUIDO", k))
    return f


class Bloqueo(RuntimeError):
    pass


def espias(mods, preflight=False):
    """Instala contadores y bloqueadores. preflight=True bloquea TODA entrada científica (incluida la pieza y sup_bound)."""
    reg = {"c2_normalizado": 0, "sup_bound": [], "bloqueadas": {}, "permitidas": ["c2_normalizado (contada)", "EM.sup_bound (espiada)",
                                                                                  "EM.Engine/MotorNormalizado internos"]}

    def bloq(nombre):
        def f(*a, **k):
            reg["bloqueadas"][nombre] = reg["bloqueadas"].get(nombre, 0) + 1
            raise Bloqueo("ENTRADA_CIENTIFICA_BLOQUEADA:" + nombre)
        return f
    EM, MO, CO, SU, FR, C2N = (mods[x] for x in ("encierros_modelo", "modelos", "cobertura", "supremum", "frontier", "c2_normalizado"))
    for cls in (MO.ModeloTeorico, MO.ModeloTeoricoSinEncierros):
        for n, v in list(vars(cls).items()):
            if callable(v) and not n.startswith("__") and not isinstance(v, (property, staticmethod, classmethod)):
                setattr(cls, n, bloq("%s.%s" % (cls.__name__, n)))
    for n in [x for x in vars(CO) if not x.startswith("_")]:
        v = getattr(CO, n)
        if callable(v) and not isinstance(v, type) and n != "clase_c2":
            setattr(CO, n, bloq("cobertura." + n))
    for n in ("certified_supremum", "supremum"):
        if hasattr(SU, n):
            setattr(SU, n, bloq("supremum." + n))
    for n in [x for x in vars(FR) if not x.startswith("_")]:
        v = getattr(FR, n)
        if callable(v) and not isinstance(v, type) and getattr(v, "__module__", "") == FR.__name__:
            setattr(FR, n, bloq("frontier." + n))
    for n in ("sup_bound_shear",):
        setattr(EM, n, bloq("encierros_modelo." + n))
    setattr(C2N, "c2_original_con_estadisticas", bloq("c2_normalizado.c2_original_con_estadisticas"))
    if preflight:
        for n in ("sup_bound",):
            setattr(EM, n, bloq("encierros_modelo." + n))
        for n in ("R", "R_box_g"):
            setattr(EM.Engine, n, bloq("Engine." + n))
        EM.IParams.from_primitive_box = classmethod(lambda cls, *a, **k: bloq("IParams.from_primitive_box")())
        pieza = bloq("c2_normalizado.c2_normalizado")
        setattr(C2N, "c2_normalizado", pieza)
        return reg, pieza
    sb0 = EM.sup_bound

    def sup_bound_espia(eng, instrument, bar_d, bar_f, **kw):
        r = sb0(eng, instrument, bar_d, bar_f, **kw)
        reg["sup_bound"].append({"instrument": instrument, "bar_d": bar_d, "bar_f": bar_f, "tol": kw.get("tol"), "max_boxes": kw.get("max_boxes"),
                                 "jump_budget": kw.get("jump_budget"), "otros": sorted(k for k in kw if k not in ("tol", "max_boxes", "jump_budget")),
                                 "lower": r.lower, "upper": r.upper, "approx": r.approx, "point": list(r.point), "boxes": r.boxes,
                                 "jump_live": bool(r.jump_live), "live": len(r.live)})
        return r
    EM.sup_bound = sup_bound_espia
    p0 = C2N.c2_normalizado

    def pieza(*a, **k):
        reg["c2_normalizado"] += 1
        if reg["c2_normalizado"] > 1:
            raise Bloqueo("SOLICITUD_EXTRA")
        return p0(*a, **k)
    return reg, pieza


# ------------------------------------------------------------------------------------------------ validación única y lectura
def _finito(x):
    return isinstance(x, float) and math.isfinite(x)


CAMPOS_EVIDENCIA = {"kind", "tarea", "modo", "sintetico", "manifiesto_sha256", "alcance_sha256", "puerta_nativa", "indice_sha256", "inicio_utc",
                    "raiz_binaria", "raiz_binaria_hex", "fijos", "cotas", "cotas_hex", "diseno", "j", "no_medido", "pieza", "plataforma",
                    "configuracion_efectiva", "solicitud", "sup_bound", "bloqueadas", "prohibidas_cargadas", "estadisticas", "intervalo_normalizado",
                    "U_C2", "U_C2_hex", "parada_motor", "precision_real", "estado", "motivo", "fin_utc"}


def piezas_cambiadas(idx_p=None):
    """Piezas del índice congelado cuyos bytes en disco difieren (lista vacía = conforme); índice ilegible = no conforme."""
    idx_p = Path(idx_p or AQUI / "PAQUETE_B1.json")
    try:
        idx = json.loads(idx_p.read_bytes())
        return [n for n, h in idx["piezas"].items() if HF(AQUI / n) != h]
    except (OSError, ValueError, KeyError, TypeError) as ex:
        return ["INDICE_ILEGIBLE:%r" % (ex,)]


# ------------------------------------------------------------------------------------------------ rem164: procedencia única
# Autoridad de la continuación ENTRE RONDAS. Producción: no existe ninguna fuente sellada y aceptada (rem164); el valor None hace que toda
# continuación productiva se rechace de forma explícita. Fijarla exige una enmienda revisada de este paquete (nuevo índice, nuevo alcance,
# nuevo acto); ni el llamador ni un documento aportado pueden designarla. Sintético: FIXTURE de ruta fija dentro del área del paquete, que el
# código solo lee en modo sintético; un origen sintético nunca se reetiqueta como producción.
AUTORIDAD_CONTINUACION_PRODUCTIVA = None
AUTORIDAD_SINTETICA = Y / "pruebas/autoridad_sintetica/AUTORIDAD_FIXTURE_SINTETICA_B1.json"
KIND_AUTORIDAD_SINTETICA = "autoridad-continuacion-b1-FIXTURE-SINTETICA-rem164"
KIND_INVENTARIO_SINTETICO = "inventario-fuente-b1-FIXTURE-SINTETICO-rem164"
ARGS_TRABAJO = ("--modo", "--manifiesto", "--salida", "--alcance", "--decision")

# ------------------------------------------------------------------------------------------------ rem165: invocación registrada completa
# Invocación ADMITIDA del trabajador y del validador. La fija este paquete, nunca quien presenta un registro: el intérprete autorizado por ruta e
# identidad (dato fijado por el encargo rem165), las opciones -B -I -X utf8 en sus posiciones, el script del paquete en posición de programa y
# después solo los argumentos de la operación. conducir_b1.py emite sus órdenes con estas mismas constantes, y p3ctl 546271b0… las registra
# sin cambios en directa_inicio.argv (el mismo cmd que pasa a su supervisor tras «--», con cwd = su RAIZ).
INTERPRETE_AUTORIZADO = Path(r"@@R_WIN@@\tmp\pilotos_b36_b37_2026-10-02\entorno\cpython-3.12.4-amd64\python.exe")
INTERPRETE_SHA256 = "fd5c46d73d29ba21b04c844bbaf9096066136526911230645a2a040d23fb612b"
OPCIONES_INTERPRETE = ("-B", "-I", "-X", "utf8")
_PROHIBIDOS_RUTA = '"<>|?*'


def ruta_windows(x, base=None):
    """rem165 — NORMALIZACIÓN DECLARADA de una ruta Windows de un registro: léxica, determinista y sin tocar el disco. None = no admitida.
    Equivalencias admitidas (un subconjunto de la normalización Win32 de rutas completas): separador «\\» o «/», separadores repetidos,
    segmentos «.» y «..» plegados léxicamente, letra de unidad en mayúscula o minúscula, y ruta relativa SOLO respecto de base (el cwd ya
    autenticado y normalizado). Todo lo demás se compara EXACTO, mayúsculas incluidas. Se rechaza: no texto o vacía, caracteres de control,
    comillas y «<>|?*», «:» fuera de la unidad (flujos alternos), prefijos «\\\\?\\» y «\\\\.\\», UNC, unidad sin raíz («D:x»), raíz sin
    unidad («\\x»), relativa sin base, componente terminado en punto o espacio y «..» por encima de la raíz. Nombres cortos 8.3, uniones,
    enlaces o variantes de mayúsculas fuera de la unidad tampoco se aceptan, aunque Windows los resolviera al mismo archivo: un rechazo de
    más es seguro; una aceptación de más no lo es."""
    if not isinstance(x, str) or not x or any(ord(c) < 32 for c in x) or any(c in _PROHIBIDOS_RUTA for c in x):
        return None
    s = x.replace("/", "\\")
    if s.startswith("\\\\"):
        return None
    if len(s) >= 2 and s[1] == ":":
        if not ("A" <= s[0].upper() <= "Z") or len(s) < 3 or s[2] != "\\":
            return None
        unidad, resto = s[0].upper() + ":", s[3:]
    elif s.startswith("\\") or base is None:
        return None
    else:
        unidad, resto = base[:2], base[3:] + "\\" + s
    if ":" in resto:
        return None
    partes = []
    for c in resto.split("\\"):
        if c in ("", "."):
            continue
        if c == "..":
            if not partes:
                return None
            partes.pop()
            continue
        if c[-1] in ". ":
            return None
        partes.append(c)
    return unidad + "\\" + "\\".join(partes)


def _invocacion(av, cwd, script):
    """rem165 — ÚNICA comprobación de la ORDEN COMPLETA registrada (directa_inicio.argv y cwd de p3ctl) frente a la invocación admitida de
    `script`, pieza de este paquete: [INTERPRETE_AUTORIZADO, -B, -I, -X, utf8, AQUI/script, argumentos...]. La usan el trabajo y la validación
    propia. El prefijo esperado sale de las constantes del paquete, nunca del argv comprobado. El cwd tiene que ser la raíz del proyecto de este
    paquete (p3ctl registra y usa RAIZ = área/../..); las rutas relativas del argv solo se resuelven respecto de él. Devuelve (motivo,
    argumentos): con motivo None la invocación es la admitida y argumentos son los posteriores al script, que cada consumidor sigue
    comprobando como antes. Cualquier otra forma se rechaza: -c, -m, «-» (stdin), shell o envoltorio, otro ejecutable o el mismo nombre en otra
    ruta, opciones de más, de menos o en otra posición, y un script de otra ruta o con bytes distintos de los del índice congelado."""
    if not isinstance(av, list) or not all(isinstance(x, str) for x in av):
        return "ARGV_NO_ES_LISTA_DE_TEXTO", None
    base = ruta_windows(cwd) if isinstance(cwd, str) else None
    if base is None or base != ruta_windows(str(R)):
        return "CWD_NO_AUTENTICADO", None
    n = len(OPCIONES_INTERPRETE)
    if len(av) < n + 2:
        return "INVOCACION_INCOMPLETA", None
    if ruta_windows(av[0], base) != ruta_windows(str(INTERPRETE_AUTORIZADO)):
        return "INTERPRETE_NO_AUTORIZADO", None
    if HF(INTERPRETE_AUTORIZADO) != INTERPRETE_SHA256:
        return "INTERPRETE_DE_OTRA_IDENTIDAD", None
    if tuple(av[1:n + 1]) != OPCIONES_INTERPRETE:
        return "OPCIONES_DEL_INTERPRETE_NO_PREVISTAS", None
    if ruta_windows(av[n + 1], base) != ruta_windows(str(AQUI / script)):
        return "PROGRAMA_DISTINTO_DEL_SCRIPT_FIJADO", None
    if HF(AQUI / script) != json.loads((AQUI / "PAQUETE_B1.json").read_bytes())["piezas"][script]:
        return "SCRIPT_DISTINTO_DEL_INDICE", None
    return None, av[n + 2:]


def _utc(s):
    t = dt.datetime.fromisoformat(str(s))
    return t if t.tzinfo else None


def procedencia(fuente, modo, man_sha, alcance_sha, propia=None):
    """ÚNICA comprobación de procedencia (validador directo y continuación). Devuelve (fallos, bytes_evidencia, info); fallos vacío = auténtica.
    fuente = {"tipo": "lanzamiento", "area": A, "lanzamiento": L[, "evidencia_sha256": h_memoria]} (ronda en curso) o
             {"tipo": "previo", "estado_previo": ruta absoluta de estado_b1.json} (entre rondas).
    propia = {"area": A, "lanzamiento": L, "argv": [...]} cuando llama el validador: su PROPIA directa <L>_VALIDACION debe estar abierta en el
    registro p3ctl de A con la invocación admitida de validar_b1.py (rem165, _invocacion) y exactamente esos argumentos detrás del script
    (fuera de su directa no hay validación). rem165: la ejecución <L>_TRABAJO también exige la invocación admitida de b1_trabajo.py.
    Orden: 1) autoridad (previo: la fijada, nunca la ofrecida); 2) bytes ligados a la autoridad (previo: inventario fijado → estado, registro
    p3ctl, salida del trabajador, evidencia, todos por huella del inventario); 3) ejecución <L>_TRABAJO: un inicio y un fin conformes del
    trabajador de ESTE código, mismo modo, manifiesto y alcance; 4) la huella de la evidencia es la que el trabajador emitió en su salida
    registrada por el supervisor (y la del conductor en memoria, si la hay); 5) solo entonces devuelve esos bytes."""
    info = {"tipo": (fuente or {}).get("tipo"), "modo": modo}
    try:
        return _procedencia(fuente or {}, modo, man_sha, alcance_sha, propia, info)
    except (B1Error, OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as ex:
        return ["PROCEDENCIA_NO_AUTENTICA: %s" % str(ex)[:200]], None, info


def _procedencia(fuente, modo, man_sha, alcance_sha, propia, info):
    tipo = fuente.get("tipo")
    if modo not in ("produccion", "sintetico"):
        return ["MODO_DESCONOCIDO"], None, info
    if tipo == "lanzamiento":
        area, lanz, inv = Path(fuente["area"]), str(fuente["lanzamiento"]), None
    elif tipo == "previo":
        if modo == "produccion":
            if AUTORIDAD_CONTINUACION_PRODUCTIVA is None:
                return ["CONTINUACION_PRODUCTIVA_SIN_FUENTE_ACEPTADA"], None, info
            return ["AUTORIDAD_PRODUCTIVA_NO_IMPLEMENTADA"], None, info       # inalcanzable con None (declarado)
        if not AUTORIDAD_SINTETICA.is_file():
            return ["AUTORIDAD_DE_CONTINUACION_AUSENTE"], None, info
        ab = AUTORIDAD_SINTETICA.read_bytes()
        aut = json.loads(ab)
        info["autoridad"] = {"ruta": str(AUTORIDAD_SINTETICA), "sha256": H(ab)}
        if aut.get("kind") != KIND_AUTORIDAD_SINTETICA or aut.get("sintetico") is not True or aut.get("habilita_produccion") is not False:
            return ["AUTORIDAD_DE_CONTINUACION_NO_SINTETICA_O_AJENA"], None, info
        ep = Path(fuente["estado_previo"])
        if not ep.is_absolute():
            return ["ESTADO_PREVIO_SIN_RUTA_ABSOLUTA"], None, info
        cands = [s for s in aut.get("fuentes") or [] if (Path(s["area"]) / s["estado"]).resolve() == ep.resolve()]
        if len(cands) != 1:
            return ["PREVIO_SIN_FUENTE_ACEPTADA"], None, info
        s = cands[0]
        area = Path(s["area"])
        ib = (area / s["inventario"]).read_bytes()
        info["fuente_fijada"] = dict(s)
        if H(ib) != s["inventario_sha256"]:
            return ["INVENTARIO_DISTINTO_DEL_FIJADO"], None, info
        invd = json.loads(ib)
        if invd.get("kind") != KIND_INVENTARIO_SINTETICO or invd.get("sintetico") is not True:
            return ["INVENTARIO_NO_SINTETICO_O_AJENO"], None, info
        inv = invd["files"]
    else:
        return ["FUENTE_DE_PROCEDENCIA_DESCONOCIDA"], None, info
    raiz_area = area.resolve()

    def leer_b(p):
        """Bytes ligados: en «previo», SOLO los del inventario fijado (ruta relativa al área y huella); en «lanzamiento», el registro vivo."""
        b = Path(p).read_bytes()
        if inv is not None:
            rel = Path(p).resolve().relative_to(raiz_area).as_posix()
            ent = inv.get(rel) or {}
            if ent.get("solo_anexion") is True and rel == "audit/p3ctl/eventos.jsonl":   # registro p3ctl de solo anexión: prefijo fijado
                b = b[:ent.get("bytes", -1)] if isinstance(ent.get("bytes"), int) and len(b) >= ent["bytes"] else b""
            if rel not in inv or H(b) != ent.get("sha256"):
                raise B1Error("BYTES_NO_LIGADOS_A_LA_FUENTE:" + rel)
        return b

    if H(leer_b(area / "codigo/p3ctl.py")) != P3CTL_SHA or not (area / "audit/recepcion.json").is_file():
        return ["AREA_DE_ORIGEN_SIN_CONTENCION"], None, info
    st = None
    if tipo == "previo":
        sb_ = leer_b(Path(fuente["estado_previo"]))
        st = json.loads(sb_)
        lanz = str(st.get("lanzamiento") or "")
        info["estado_previo_sha256"] = H(sb_)
        if not (st.get("kind") == "estado-b1" and st.get("estado_final") == "detenido_por_presupuesto" and (st.get("cierre") or {}).get("conforme") is True
                and st.get("pendientes") == [TAREA_VALIDACION] and lanz):
            return ["PREVIO_NO_PENDIENTE_DE_VALIDACION_O_CIERRE_NO_CONFORME"], None, info
        if st.get("modo") != modo:
            return ["PREVIO_DE_OTRO_MODO"], None, info
        if st.get("manifiesto_sha256") != man_sha:
            return ["PREVIO_DE_OTRO_MANIFIESTO"], None, info
        if st.get("alcance_sha256") != alcance_sha:
            return ["PREVIO_DE_OTRO_ALCANCE"], None, info
        if st.get("indice_sha256") != HF(AQUI / "PAQUETE_B1.json"):
            return ["PREVIO_DE_OTRO_INDICE"], None, info
    evb = leer_b(area / "audit/p3ctl/eventos.jsonl")
    evs = jsonl(evb)
    info.update(area=str(area), lanzamiento=lanz, eventos_sha256=H(evb))
    tid = "%s_TRABAJO" % lanz
    ini = [x for x in evs if x.get("evento") == "directa_inicio" and x.get("id") == tid]
    fin = [x for x in evs if x.get("evento") == "directa_fin" and x.get("id") == tid]
    if len(ini) != 1 or len(fin) != 1:
        return ["EJECUCION_DE_TRABAJO_AUSENTE_O_REPETIDA"], None, info
    ini, fin = ini[0], fin[0]
    info.update(evento_inicio_sha256=H(canon(ini)), evento_fin_sha256=H(canon(fin)))
    if not (fin.get("conforme") is True and fin.get("estado") == "TERMINO" and fin.get("codigo_salida") == 0):
        return ["EJECUCION_DE_TRABAJO_NO_CONFORME"], None, info
    mot, resto = _invocacion(ini.get("argv"), ini.get("cwd"), "b1_trabajo.py")     # rem165: la orden completa, no un token del argv
    if mot:
        return ["INVOCACION_DE_TRABAJO_NO_AUTORIZADA:" + mot], None, info
    op = {resto[j]: resto[j + 1] for j in range(0, len(resto) - 1, 2)}
    if len(resto) % 2 or set(op) - set(ARGS_TRABAJO) or len(op) * 2 != len(resto):
        return ["ARGUMENTOS_DE_TRABAJO_NO_PREVISTOS"], None, info
    cwd = Path(ini.get("cwd") or ".")
    absol = lambda x: Path(x) if Path(x).is_absolute() else cwd / x  # noqa: E731
    if op.get("--modo") != modo:
        return ["EJECUCION_DE_OTRO_MODO"], None, info
    if HF(absol(op["--manifiesto"])) != man_sha:
        return ["EJECUCION_DE_OTRO_MANIFIESTO"], None, info
    if (HF(absol(op["--alcance"])) if op.get("--alcance") else None) != alcance_sha:
        return ["EJECUCION_DE_OTRO_ALCANCE"], None, info
    dT = absol(op["--salida"])
    so = leer_b(area / "logs/p3_directas" / (tid + ".stdout.log"))
    if fin.get("salida_bytes") != len(so):
        return ["SALIDA_DEL_TRABAJADOR_DISTINTA_DE_LA_REGISTRADA"], None, info
    try:
        rw = json.loads(so.decode("utf-8").strip().splitlines()[-1])
    except (ValueError, IndexError):
        return ["SALIDA_DEL_TRABAJADOR_ILEGIBLE"], None, info
    if rw.get("tarea") != TAREA_TRABAJO or rw.get("estado") != "complete" or rw.get("solicitudes") != 1 or not isinstance(rw.get("evidencia_sha256"), str):
        return ["TRABAJADOR_SIN_RESULTADO_COMPLETO"], None, info
    h_rec = rw["evidencia_sha256"]
    info.update(trabajo_id=tid, trabajo_dir=str(dT), salida_trabajador_sha256=H(so), evidencia_sha256=h_rec)
    if tipo == "lanzamiento" and fuente.get("evidencia_sha256") is not None and fuente["evidencia_sha256"] != h_rec:
        return ["EVIDENCIA_DISTINTA_DE_LA_DEL_CONDUCTOR"], None, info
    if st is not None and (st.get("evidencia_sha256") != h_rec or Path((st.get("etapas") or {}).get("trabajo_dir") or "").resolve() != dT.resolve()):
        return ["PREVIO_INCOHERENTE_CON_SU_EJECUCION"], None, info
    leer_b(dT / "SOLICITUD_INICIO.json")
    raw = leer_b(dT / "EVIDENCIA_B1.json")
    if H(raw) != h_rec:
        return ["EVIDENCIA_DISTINTA_DE_LA_EJECUCION"], None, info
    e = json.loads(raw)
    t_ini, t_fin, e_ini, e_fin = _utc(ini.get("utc")), _utc(fin.get("utc")), _utc(e.get("inicio_utc")), _utc(e.get("fin_utc"))
    if None in (t_ini, t_fin, e_ini, e_fin) or not (t_ini <= e_ini <= e_fin <= t_fin):
        return ["EVIDENCIA_FUERA_DE_SU_EJECUCION"], None, info
    if propia is not None:
        pa = Path(propia["area"])
        if H(Path(pa / "codigo/p3ctl.py").read_bytes()) != P3CTL_SHA:
            return ["VALIDACION_FUERA_DE_UN_AREA_CONTENIDA"], None, info
        pevs = jsonl((pa / "audit/p3ctl/eventos.jsonl").read_bytes())
        tv = "%s_VALIDACION" % propia["lanzamiento"]
        pi = [x for x in pevs if x.get("evento") == "directa_inicio" and x.get("id") == tv]
        pf = [x for x in pevs if x.get("evento") == "directa_fin" and x.get("id") == tv]
        if len(pi) != 1 or pf:
            return ["VALIDACION_FUERA_DE_SU_DIRECTA"], None, info
        mot, presto = _invocacion(pi[0].get("argv"), pi[0].get("cwd"), "validar_b1.py")     # rem165: mismo criterio que el trabajo
        if mot:
            return ["INVOCACION_DE_VALIDACION_NO_AUTORIZADA:" + mot], None, info
        if presto != [str(x) for x in propia["argv"]]:
            return ["VALIDACION_FUERA_DE_SU_DIRECTA"], None, info
        if tipo == "lanzamiento" and (pa.resolve() != raiz_area or str(propia["lanzamiento"]) != lanz):
            return ["VALIDACION_DE_OTRO_LANZAMIENTO"], None, info
        info["validacion_id"] = tv
    return [], raw, info


def validar_evidencia(man, man_sha, ev_raw, modo, alcance_sha=None, indice_sha=None, puerta=None):
    """VALIDACIÓN ÚNICA de EVIDENCIA_B1.json (bytes leídos una vez por quien llama). Devuelve (fallos, datos). No llama al encierro, al modelo
    ni a ningún supremo: autentica procedencia, contrato y forma; el valor numérico depende de la garantía del motor productor aceptado."""
    f = []
    try:
        e = json.loads(ev_raw)
    except (ValueError, TypeError):
        return ["EVIDENCIA_JSON_INVALIDA"], None
    if not isinstance(e, dict) or e.get("kind") != "evidencia-b1-rem163":
        return ["EVIDENCIA_DE_OTRO_TIPO"], None
    if set(e) - CAMPOS_EVIDENCIA:     # p. ej. un sup G, una robustez o una clasificación añadidos: B1 solo no puede producirlos
        return [("CAMPO_NO_PREVISTO_EN_LA_EVIDENCIA", sorted(set(e) - CAMPOS_EVIDENCIA))], None
    sint = modo == "sintetico"
    if modo not in ("produccion", "sintetico") or man.get("modo") != modo or e.get("modo") != modo or bool(e.get("sintetico")) != sint:
        return ["MODO_DISTINTO"], None
    fm = validar_manifiesto(man)
    if fm:
        return ["MANIFIESTO_NO_VALIDO"] + [str(x)[:120] for x in fm[:4]], None
    if e.get("tarea") != TAREA_TRABAJO:
        f.append("EVIDENCIA_DE_OTRA_TAREA")
    if e.get("manifiesto_sha256") != man_sha:
        f.append("MANIFIESTO_AJENO")
    if (modo == "produccion" and alcance_sha is None) or e.get("alcance_sha256") != alcance_sha:
        f.append("ALCANCE_AJENO_O_AUSENTE")
    if indice_sha is not None and e.get("indice_sha256") != indice_sha:
        f.append("INDICE_AJENO")
    if modo == "produccion":
        pe, pv = e.get("puerta_nativa") or {}, puerta or {}
        if not pe or pe.get("modo_arnes") is not False or any(pe.get(k) != pv.get(k) for k in ("uuid", "linea", "alcance_sha256", "registro_sha256")):
            f.append("PUERTA_NATIVA_DISTINTA_O_AUSENTE")
    p = e.get("pieza") or {}
    if modo == "produccion":
        mods = (p.get("identidad") or {}).get("modulos") or {}
        esperado = {("paper2b" if n == "__init__.py" else "paper2b." + n[:-3]): h for n, h in CIERRE_C0.items()}
        if p.get("tipo") != "c0" or {k: v.get("sha256") for k, v in mods.items()} != esperado or (p.get("identidad") or {}).get("precargados") \
                or not all(v.get("registrado_es_el_cargado") is True for v in mods.values()) or p.get("identidad_posterior"):
            f.append("PIEZA_O_MODULOS_NO_SON_EL_CIERRE_C0")
    else:
        if p.get("tipo") != "doble_inerte" or p.get("sha256") != (man.get("doble") or {}).get("sha256"):
            f.append("DOBLE_NO_DECLARADO_O_AJENO")
    caja, fijos, bd, bf = caja_de(man)
    rb = e.get("raiz_binaria") or {}
    if sorted(rb) != sorted(STRUCT) or any(not (iguales_bits(rb[k][0], caja[k][0]) and iguales_bits(rb[k][1], caja[k][1])) for k in STRUCT):
        f.append("RAIZ_DISTINTA_DE_LA_FIJADA")
    if e.get("fijos") != fijos or not (iguales_bits((e.get("cotas") or [None, None])[0], bd) and iguales_bits((e.get("cotas") or [None, None])[1], bf)):
        f.append("FIJOS_O_COTAS_DISTINTOS")
    if e.get("diseno") != DISENO or e.get("j") != MENU:
        f.append("DISENO_O_MENU_DISTINTO")
    if e.get("configuracion_efectiva") != man["modelo"]["configuracion"]:
        f.append("CONFIGURACION_EFECTIVA_DISTINTA")
    if (e.get("plataforma") or {}).get("garantia") != GARANTIA:
        f.append("GARANTIA_DE_PLATAFORMA_AUSENTE")
    s = e.get("solicitud") or {}
    sb = e.get("sup_bound") or []
    if s.get("contador") != 1 or len(sb) != 1:
        f.append("NO_ES_UNA_SOLICITUD_CON_UN_SUP_BOUND")
    else:
        b = sb[0]
        if b.get("instrument") != MENU or b.get("max_boxes") != CONFIG_ESPERADA["struct_max_boxes"] or b.get("jump_budget") != 0 or b.get("otros") \
                or not (iguales_bits(b.get("bar_f"), bf) and iguales_bits(b.get("bar_d"), bd)):
            f.append("SUP_BOUND_CON_OTRO_CONTRATO")
    if (e.get("estadisticas") or {}).get("normalizado") is not True:
        f.append("NO_NORMALIZADO")
    if e.get("bloqueadas") or e.get("prohibidas_cargadas"):
        f.append("LLAMADAS_O_MODULOS_PROHIBIDOS")
    if e.get("estado") != "complete":
        f.append("TRABAJO_INCOMPLETO")
    iv = e.get("intervalo_normalizado") or {}
    lo, hi, U = iv.get("lo"), iv.get("hi"), e.get("U_C2")
    if not (_finito(lo) and _finito(hi) and lo <= hi):
        return f + ["INTERVALO_INVALIDO"], None
    if iv.get("lo_hex") != float.hex(lo) or iv.get("hi_hex") != float.hex(hi):
        f.append("HEX_DEL_INTERVALO_NO_COINCIDE")
    if not iguales_bits(U, hi) or e.get("U_C2_hex") != float.hex(hi):
        f.append("U_C2_NO_ES_EL_EXTREMO_SUPERIOR_DEL_MOTOR")
    if len(sb) == 1 and _finito(sb[0].get("lower")) and _finito(sb[0].get("upper")):
        if not (hi >= max(sb[0]["lower"], sb[0]["upper"]) and lo <= sb[0]["lower"]):
            f.append("INTERVALO_NO_ENCIERRA_LA_EVIDENCIA_DE_SUP_BOUND")
    elif len(sb) == 1:
        f.append("SUP_BOUND_NO_FINITO")
    if f:
        return f, None
    parada = "tope_de_cajas" if sb[0]["boxes"] >= CONFIG_ESPERADA["struct_max_boxes"] else "tolerancia_o_caja_no_refinable"
    return [], {"U_C2": hi, "U_C2_hex": float.hex(hi), "intervalo": [lo, hi], "precision_real": hi - lo, "parada": parada,
                "cajas": sb[0]["boxes"], "evaluaciones": (e.get("estadisticas") or {}).get("evaluaciones"),
                "segundos_encierro": (e.get("estadisticas") or {}).get("segundos")}


def regla(U, K1):
    """Regla exacta: 'detener' si U > K1 − 1/100; 'candidato_B2' si U <= K1 − 1/100 (U y K1 como racionales exactos)."""
    return "detener" if Fraction(U) > Fraction(K1) - EPS else "candidato_B2"


def lectura(man, datos):
    """Una fila por grupo (6) y correspondencia completa con las doce. datos None → sin lectura científica válida."""
    if datos is None:
        return {"valida": False, "motivo": "RESULTADO_INVALIDO_O_INCOMPLETO", "grupos": [], "afirmaciones": []}
    U = datos["U_C2"]
    filas, por = [], []
    for g in man["grupos"]:
        r = regla(U, g["K1_testigo"])
        filas.append({"grupo": g["grupo"], "K1_testigo": g["K1_testigo"], "K1_testigo_hex": g["K1_testigo_hex"], "umbral_exacto": g["umbral_exacto"],
                      "U_C2": U, "U_C2_hex": float.hex(U), "comparacion": ">" if r == "detener" else "<=", "lectura": r,
                      "significado": ("la cota separable de raiz no puede certificar este grupo; se detiene esta via para el (no prueba inconclusion ni "
                                      "descarta otro metodo)") if r == "detener" else "candidato a B2: todavia falta una cota inferior global K1 valida",
                      "afirmaciones": list(g["afirmaciones"])})
        for a in g["afirmaciones"]:
            por.append({"afirmacion": a, "grupo": g["grupo"], "lectura": r, "estado_cientifico": "desconocida (sin cambio)"})
    return {"valida": True, "eps": "1/100", "U_C2": U, "U_C2_hex": float.hex(U), "grupos": filas, "afirmaciones": sorted(por, key=lambda x: x["afirmacion"]),
            "no_clasifica": True, "no_robustez": True, "no_inconclusion_preservada": True, "N3A_no_adoptada": True,
            "si_todos_detienen": "se vuelve al autor para decidir el alcance"}
