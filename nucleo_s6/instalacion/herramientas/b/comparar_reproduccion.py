"""COMPARADOR DE REPRODUCCIÓN POR UNIDAD, v3-S6 (paso 4 desde s6r39; v3 de lima1857 aceptado en rem17 CONECTADO a la autoridad S6 viva;
NO OFICIAL; candidato; no ejecuta el modelo).

CAMBIOS paso 4 (S6), solo de conexión: autoridad A.from_s6 con el ANCLA externa (la ruta S5 ya no verifica tras incorporar S6);
contratos de la autoridad viva (G-NA-1); D7 del Checker = el D7 bajo S6 de la corrida (salidas_s6, directorio y árbol explícitos);
despliegue explícito (--despliegue, claves exactas de seleccion_paso4 en S6); fuentes históricas = raiz_fuentes; selecciones R2/R3
empaquetadas en la instalación con los mismos sha256; validador productivo fijado = el INSTALADO junto a este módulo. Reglas,
capas, validación común y dictámenes SIN cambios.

CAMBIOS lima1857 (dictamen rem16): la evidencia v3 de la corrida nueva ya no se acepta con comprobaciones parciales. Antes de
comparar, toda unidad v3 (nueva u original) pasa las reglas EXISTENTES del núcleo candidato que no necesitan el modelo:
contrato_paquete.verificar_techo (dominio, laterales y testigos, fila C2 de convergencia: valor inicial = C_2, cota superior en
[C_2, C_2 + err], change_bound = numerical_error, tolerancia = tol_converge, cobertura y estado), contrato_paquete.verificar_evidencia
(referencia por contenido, pertenencia a la unidad y al resultado, método, unidad, cota = change_bound, estado; evidencias no
huérfanas; una certificada por sección R2 completa), la convergencia INV de las búsquedas costosas recalculada desde sus hijas
(convergencia.fila_raices, misma llamada que verificar_inversiones) y el Checker del núcleo (contrato_paquete.checker_nucleo con el
D7 autenticado). Lo que EXIGE el modelo o el Run de la corrida (valor del modelo en el punto del supremo, inversiones
recalculables y sus objetivos, geometría con f, identidad y macro derivadas: paquete_seleccion.verificar_celda) es VALIDACIÓN
PRODUCTIVA: la comparación solo da «aceptada» si la correspondencia aporta un registro de esa validación, emitido por el validador
productivo fijado (sha256) y LIGADO a los bytes nuevos (sha256 de documento y filas), autenticado por el inventario de la corrida
nueva. Sin él, el dictamen es «pendiente_validacion_productiva» (nunca «aceptada» ni «validada» por omisión).

  python -B herramientas/b/comparar_reproduccion.py --despliegue <despliegue_S6.json> <correspondencia.json> <salida.json>

Corrige el comparador de lima1426 (dictamen rem15): aquel eximía tablas ENTERAS del diagnóstico cuando una regla especial
comprobaba solo algunos campos, colapsaba duplicados al construir diccionarios, aceptaba identidades contractuales sin ligarlas a
la selección y lanzaba excepciones ante tipos inválidos. Principio de esta versión: TODA diferencia científica, campo a campo, o
está cubierta por una regla explícita ACTIVA o es discrepancia. No hay tablas exentas.

<correspondencia.json>:
  {"seleccion": "R2" | "R3",
   "alcance": {"tipo": "completa"} | {"tipo": "parcial", "contractuales": [...]},
   "corrida_nueva": {"raiz": <dir>, "inventario_sha256": <sha del audit/entrega.json de la corrida nueva>, "run_id": "BRUN-..."},
   "unidades": [{"contractual": <cell_id contractual>, "nuevo": {"doc": <ruta relativa a raiz>, "filas": <ruta relativa>}}],
   "reglas_selladas": [{"id": <id del catálogo>, "sha256": <sha256 del texto de la regla en REGLAS>}],
   "validacion_productiva": {"archivo": <ruta relativa a raiz, en el inventario de la corrida nueva>}   (opcional)}
Registro productivo: {"validador": {"archivo": VALIDADOR_PRODUCTIVO[0], "sha256": VALIDADOR_PRODUCTIVO[1]},
                      "unidades": {<unidad>: {"documento_sha256", "filas_sha256", "estado": "completa_validada" | "no_aplicable_validada" | ...}}}

Tres capas SEPARADAS por unidad:
 1. CORRESPONDENCIA Y AUTORIDAD. El ORIGINAL nunca lo elige la correspondencia: la etiqueta contractual debe pertenecer a la
    selección autenticada (lista con sha256 fijado aquí) y el documento original y sus filas se resuelven por la cadena de
    autoridad (índice de paquetes de lima1018 con su inventario fijado -> paquete -> inventario de la entrega -> sha256 del
    documento y de las filas). La entrega, el contrato y el cell_id E12 de la selección deben coincidir con lo resuelto.
    La corrida nueva se autentica por SU inventario (sha256 declarado) y debe tener un run_id propio, distinto del original.
    Identidad científica: los 15 campos de la clave E12 salvo run_id (cell_context), el contenido de frontera y de macro y la
    identidad del resumen (resultado) deben coincidir; si no, correspondencia_incorrecta.
 2. VALIDACIÓN PROPIA de cada lado (también del original, como control): esquema del CONTRATO DE LA AUTORIDAD (columnas exactas,
    tipos, nulabilidad, PK/UK, orden; paper2b.contrato_paquete.esquema con Contracts cargado desde la autoridad S5), conjunto
    exacto de tablas de la versión exigida, valores finitos (NaN/Infinity rechazados al leer), identificadores recalculados con
    las fórmulas del núcleo (CEL, FRN, CEI, MAC, NEV), relaciones documento <-> tablas (resumen techo/confrontación = filas),
    C_2 confrontación = C_2 techo, G = C_2 - K_comp_1, certificado del techo, alcanzabilidad y testigos laterales, inversiones
    (ids, soporte, conteos de hijas, objetivos), raíces R2 sobre la trayectoria de su sección y dentro de su encierro, conteos
    por sección, R1 (componentes, cruces, aristas entre vértices existentes del mismo componente) y referencias de convergencia
    y de evidencia que resuelven. Cualquier defecto -> rechazo CONTROLADO con motivo (nunca una excepción hacia fuera).
 3. COMPARACIÓN. (a) DIAGNÓSTICO EXACTO: tras sustituir los identificadores emparejados (que dependen de run_id) por fichas,
    cada tabla se compara fila a fila por su PK del contrato y campo a campo; también el documento. No es aceptación.
    (b) COMPARACIÓN CIENTÍFICA: cada campo distinto necesita una regla ACTIVA que lo cubra y que se cumpla; si no, discrepancia.
    Solo se excluyen del ámbito científico (y se listan en el diagnóstico) los campos de diagnóstico del núcleo
    (contrato_paquete.DIAGNOSTICO) y los metadatos operativos del documento (OPERATIVOS).
Originales v2: se comparan solo las tablas y filas respaldadas en origen; las tablas hijas v3 y la fila C2 de convergencia que
trae la corrida nueva son EVIDENCIA NUEVA, que debe superar la validación propia de la corrida nueva y nunca se atribuye al
original. Cualquier otra tabla o fila adicional es discrepancia.
Dictamen por unidad: aceptada | discrepancia | corrida_nueva_invalida | correspondencia_incorrecta | no_comparable.
"""
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

A = Path(__file__).resolve().parents[2]       # instalación candidata (herramientas/b/ -> raíz de la instalación)
import importlib.util as _ilu                   # rem41: datos y condiciones de DR-1 v2 (regla PROPUESTA, desactivada salvo sellado)
_sp = _ilu.spec_from_file_location("regla_dr1_comparador", A / "herramientas/b/regla_dr1.py")
RD1 = _ilu.module_from_spec(_sp)
_sp.loader.exec_module(RD1)
T = None                                      # raíz de las fuentes históricas: raiz_fuentes del despliegue (configurar)
DESPLIEGUE = None
CLAVES_DESPLIEGUE_S6 = ("raiz_proyecto", "raiz_fuentes", "encargo", "procedencia", "politica", "recibo", "autor", "s6_package", "ancla", "d7_dir",
                        "d7_tree", "run_class", "etiqueta")
TOL_CONVERGE = 1e-7          # tol_converge del techo de celda (vigente)
TOL_REL = 1e-12              # redondeo relativo de la relación cerrada G = C_2 - K_comp_1 (validar_detallado)
SELECCIONES = {"R2": ("datos/paso4/lista_R2_testigos.json", "519ec91924cad7ce8b8cf29c407894926c912c9cb9196de3c626514303ae066f"),
               "R3": ("datos/paso4/lista_R3_candidata_B_NA.json", "7f8fed89a8d678fc18ec629b1e9326c8c776d03c566533f7b4a2a2c2a94853b2")}
AUTORIDAD = ("pv12_consumidor_cierre_paso4_3_7_2026-10-12_lima1018", "e1538d3a59de50cf2231b9b39e232de0634ecfbcae0c99bae19c5304b2547d5e",
             "demo/integracion/paquetes_finales_lima1018")
IDENT = ("design_v", "country_id", "instrument_j", "availability_case_id", "omega_id", "eta_w_block", "policy_variant_id", "regime_id",
         "requirement_basis", "xi", "layer", "bound_variant", "external_cell_id", "national_state_sha256", "expected_macro_key_sha256")
OPERATIVOS = ("suite", "trabajador", "inicio_utc", "fin_utc", "pared_s", "cpu_s", "cache_delta", "manifiesto_sha256",
              "identidad_productor_sha256", "run_class", "version_trabajador", "filas")
RUTAS = ("NO_ROOT_CERTIFIED_COVERAGE", "NO_ROOT_CERTIFIED_FISCAL_LOWER_BOUND")
VALOR_INV = {"capture_required": "C_2_required", "gain_required": "delta_y_required", "lambda_required": "lambda_pi_required",
             "phi_partial": "phi_critical_partial", "phi_total": "phi_critical_total", "external_factor": "external_factor_required"}
VALIDADOR_PRODUCTIVO = ("herramientas/s3/validadores/paquete_seleccion.py",
                        "a70cf9042e93458d2df49fb1ac7b1ceb5a27b1e6697575cf0ce532b8e4924f35")     # validador INSTALADO (rem40: vínculo único vinculo_paso4); antes 9c01fca0… (s6r39) y fb039b73… (PV12, rem13)
PENDIENTES_PRODUCTIVOS = (
    "valor del modelo en el punto del supremo (contrato_paquete.verificar_techo con valor_en del modelo de la corrida)",
    "inversiones recalculables, sus convergencias, hijas e inversion_targets derivados (contrato_paquete.verificar_inversiones con el Run)",
    "geometría R1/R2 con f del modelo (contrato_paquete.verificar_geometria)",
    "identidad, contexto, frontera y macro derivados de la selección y la autoridad (paquete_seleccion.verificar_celda, verificar_macro)",
    "resumen canónico del documento (contrato_paquete.comprobar_resumen)")
SIN_MODELO = "SIN_MODELO_EN_ESTA_CAPA"
GENERADOR_REGISTRO = "herramientas/b/registro_productivo.py"     # paso 4 (S6): generador de la ruta
# rem42: validador productivo FIJADO POR SELECCIÓN. R2: el de paquetes (VALIDADOR_PRODUCTIVO). R3: el validador R3 instalado
# (validador_r3.py: comprobaciones históricas de los lotes R3 con el contexto S6) y el histórico que reutiliza, ambos por sha256.
VALIDADOR_R3 = ("herramientas/b/validador_r3.py", "d2a5cbb6be9146434fa5455cfd47647e67e470411ebb975f12a4a8dce5a04125")
VALIDADOR_R3_HISTORICO = ("validar_detallado_lima1533.py", "871b1d7f2923c2aa7ca2dbe9dfaf3b9eeb36debad02ee3c40fceee10bb840c2c")
VALIDADORES = {"R2": VALIDADOR_PRODUCTIVO, "R3": VALIDADOR_R3}
# paso 4 (S6): los ORIGINALES se validan con SU contrato (CA2-4, el del antecedente S5 de la cadena S6) y SU D7 (árbol S5 vigente al
# producirlos, autenticado como producto del antecedente S5); la corrida NUEVA, con el contrato y el D7 de la autoridad viva (G-NA-1, D7 bajo S6)
D7_ORIGINALES = "10a0bd5bb8ea48d54d1bd0916b072afcf8cd5a4eed9c5ec16a90a728f021b739"
IDRE = re.compile(r"(?:CEL|FRN|CEI|MAC|NEV):[0-9a-f]+|BRUN-[0-9a-f]+")

# Catálogo de reglas de equivalencia. «vigente»: deriva de una tolerancia o garantía ya vigente y se aplica siempre;
# «propuesta»: solo se activa si la correspondencia la cita con el sha256 EXACTO de su texto (sellado previo).
REGLAS = {
    "A-C2": {"estado": "vigente", "campos": [("capture_ceiling_result", "C_2"), ("confrontation_result", "C_2"), ("doc", "resultado.techo.C_2")],
             "texto": "C_2 puede diferir solo si ambos techos son complete con 0 <= numerical_error <= tol_converge (1e-7) y los encierros "
                      "[C_2 - err, C_2 + err] de ambas corridas se intersecan (dos certificados válidos del mismo supremo)."},
    "A-C2-ERR": {"estado": "vigente", "campos": [("capture_ceiling_result", "numerical_error"), ("doc", "resultado.techo.numerical_error")],
                 "texto": "numerical_error puede diferir solo si se cumple A-C2 (ambas cotas certificadas <= tol_converge)."},
    "A-G": {"estado": "vigente", "campos": [("confrontation_result", "G"), ("doc", "resultado.confrontacion.G")],
            "texto": "G puede diferir solo si K_comp_1 es idéntico, se cumple A-C2 y |G_o - G_n| <= err_o + err_n (G = C_2 - K_comp_1)."},
    "R-RUTA": {"estado": "propuesta", "campos": [("inversion_result", "reason_code")],
               "texto": "En phi_total, NO_ROOT_CERTIFIED_COVERAGE y NO_ROOT_CERTIFIED_FISCAL_LOWER_BOUND son equivalentes si "
                        "computation_status, result_status y no_solution son idénticos (dos certificados de inexistencia de raíz)."},
    "R-NA-GNA1": {"estado": "propuesta", "campos": [("convergence_result", "status"), ("convergence_result", "method_id"), ("numerical_evidence", "method_id"),
                                                     ("numerical_evidence", "definition")],
                  "texto": "DR-2 (rem40; propuesta, desactivada salvo sellado): solo en unidades NA (original CA2-4 por su autoridad, nueva G-NA-1), "
                           "la fila de convergence_result con quantity_id G:<cell_id> puede diferir SOLO en status (incomplete -> not_applicable) "
                           "y method_id (certified_bound_C2_closed_form_K1 -> instrument_unavailable_authenticated), y la fila de "
                           "numerical_evidence que cita SOLO en method_id y definition, si y solo si: en ambas corridas la confrontación y el "
                           "techo son not_applicable con reason_code INSTRUMENT_NOT_AVAILABLE e instrument_available=false (misma causa de no "
                           "disponibilidad); en ambas filas G coverage_complete=false, verdict_changes=0, value_before, value_after, "
                           "change_bound y topologías nulos y tolerance idéntica; la evidencia es kind=convergence, status=limitation, "
                           "error_bound nulo y result_table/record_pk idénticos; todo lo demás (tablas, filas, documento) idéntico sin otra regla. "
                           "No cubre unidades numéricas ni filas G con valores; no cambia ninguna tolerancia."},
    "R-SUCESION-S6": {"estado": "propuesta", "campos": RD1.CAMPOS_REGLA, "texto": RD1.TEXTO},
    "R-R2-ENCIERRO": {"estado": "propuesta", "campos": [("r2_roots", "parameter_low"), ("r2_roots", "parameter_high")],
                      "texto": "Los extremos del encierro de una raíz R2 pueden diferir si ambos encierros se intersecan y el tipo de raíz "
                               "es idéntico; las coordenadas de la raíz, el residuo y los demás campos NO quedan cubiertos."}}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_regla(rid):
    return sha(REGLAS[rid]["texto"].encode("utf-8"))


class Rechazo(Exception):
    pass


def _nan(x):
    raise Rechazo("valor no finito en JSON: %s" % x)


def leer_bytes(b):
    """JSON estricto: NaN/Infinity rechazados al leer."""
    return json.loads(b, parse_constant=_nan)


def es_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def finito(x):
    return es_num(x) and math.isfinite(x)


# ================================================================================================ autoridad
_CACHE = {}


def nucleo():
    """Módulos del núcleo CANDIDATO y Contracts de la AUTORIDAD S5 (Contracts.load autentica su raíz)."""
    if "C" not in _CACHE:
        d = DESPLIEGUE
        if d is None:
            raise Rechazo("despliegue S6 no configurado (--despliegue)")
        root = Path(d["raiz_proyecto"])
        for p in (str(root), str(A / "src")):
            if p in sys.path:
                sys.path.remove(p)
            sys.path.insert(0, p)
        from herramientas.bloque2 import autoridad as AU
        from herramientas.s3.validadores.core import Contracts
        from paper2b import contrato_paquete as CP
        from paper2b import inversion as INV
        from paper2b import keys as K
        from paper2b.numeric import canon_dec
        from paper2b import convergencia as CV
        from paper2b import run as RUN
        from paper2b.d7view import D7View
        from herramientas.b import ejecutar_b as EB
        from herramientas.bloque2 import familias as FAM
        a = AU.from_s6(root, d["politica"], d["recibo"], d["autor"], lanzamiento_sha256=d["ancla"])
        if a.kind != "S6" or a.fictitious or a.package_sha256 != d["s6_package"]:
            raise Rechazo("autoridad S6 no verificada")
        for f in ("b_official_run_authorized", "freeze_run_authorized", "official_export_authorized"):
            if a.scope.get(f) is not False:
                raise Rechazo("bandera oficial activa en la autoridad: %s" % f)
        C = Contracts.load(root / a.contract_root, a.contract_sha256)
        if not d["d7_dir"].startswith("salidas_s6/"):
            raise Rechazo("D7 fuera de la zona salidas_s6")
        d7_dir = root / d["d7_dir"] / "versions" / d["d7_tree"]
        d7info = FAM.verify_version(d7_dir, "D7", expected_tree=d["d7_tree"])
        if d7info["manifest"]["authority_package_sha256"] != d["s6_package"]:
            raise Rechazo("D7 no está bajo la autoridad S6")
        cfg = RUN.RunConfig()
        if float(cfg.sup.tol_converge) != TOL_CONVERGE:
            raise Rechazo("tol_converge de la configuración distinto del vigente")
        from herramientas.congelamiento import s6_publicador as S6P
        from herramientas.s6.validadores import s6_compat as S6C
        ante = S6P.s5_antecedent(root)
        C_hist = Contracts.load(root / ante["contract_root"], S6C.CONTRATOS["CA2-4"]["sha256"])
        d7h_dir = root / "fase2_datos/d7_calibracion/versions" / D7_ORIGINALES
        d7h = FAM.verify_version(d7h_dir, "D7", expected_tree=D7_ORIGINALES)
        if d7h["manifest"]["authority_package_sha256"] != ante["package_sha256"]:
            raise Rechazo("D7 de los originales no pertenece al antecedente S5 de la cadena S6")
        _CACHE.update(C_hist=C_hist, d7_hist=D7View.load(C_hist, d7h_dir), originales={"contract_sha256": S6C.CONTRATOS["CA2-4"]["sha256"],
                      "contract_root": ante["contract_root"], "d7_tree": D7_ORIGINALES, "s5_package": ante["package_sha256"]})
        _CACHE.update(CV=CV, RUN=RUN, d7=D7View.load(C, d7_dir), TOL=dict(EB.TOLERANCES), tol_root=float(EB.TOLERANCES["T_root_residual"]),
                      xtol=float(cfg.endogenous_xtol), certificado=bool(RUN.provider_for(cfg).certified), tolc=float(cfg.sup.tol_converge))
        _CACHE.update(C=C, CP=CP, INV=INV, K=K, dec=canon_dec,
                      autoridad={"s6_package": a.package_sha256, "ancla": d["ancla"], "d7_tree": d["d7_tree"], "contract_root": a.contract_root,
                                 "contract_sha256": a.contract_sha256})
    return _CACHE


def configurar(ruta):
    """Despliegue S6 explícito (claves exactas); fija la raíz de las fuentes históricas y vacía la caché del núcleo."""
    global DESPLIEGUE, T
    d = json.loads(Path(ruta).read_bytes())
    if not isinstance(d, dict) or set(d) != set(CLAVES_DESPLIEGUE_S6) or "NO OFICIAL" not in str(d.get("etiqueta")):
        raise Rechazo("despliegue S6 con esquema distinto o etiqueta oficial")
    DESPLIEGUE, T = d, Path(d["raiz_fuentes"])
    _CACHE.clear()
    return d


def _inv(ent, h):
    raw = (T / ent / "audit/entrega.json").read_bytes()
    if sha(raw) != h:
        raise Rechazo("inventario de %s distinto del fijado" % ent)
    return {r: (v["sha256"] if isinstance(v, dict) else v) for r, v in json.loads(raw)["files"].items()}


def seleccion(nombre):
    if nombre not in SELECCIONES:
        raise Rechazo("selección desconocida: %r" % (nombre,))
    rel, h = SELECCIONES[nombre]
    raw = (A / rel).read_bytes()
    if sha(raw) != h:
        raise Rechazo("selección %s alterada (sha256 %s)" % (nombre, sha(raw)))
    us = json.loads(raw)["unidades"]
    out = {}
    for u in us:
        k = u.get("cell_id_contractual") or u["unidad"]      # R3: la unidad (la convención A/B de cell_id no está adoptada)
        if k in out:
            raise Rechazo("selección con identidad contractual duplicada: %s" % k)
        out[k] = u
    return out


def paquetes():
    if "paq" not in _CACHE:
        ent, h, carpeta = AUTORIDAD
        invp = _inv(ent, h)
        raw = (T / ent / carpeta / "paquetes_indice.json").read_bytes()
        if invp.get(carpeta + "/paquetes_indice.json") != sha(raw):
            raise Rechazo("índice de paquetes no autenticado")
        por, invs = {}, {}
        for _, m in json.loads(raw)["paquetes"].items():
            b = (T / ent / carpeta / m["archivo"]).read_bytes()
            if invp.get(carpeta + "/" + m["archivo"]) != sha(b):
                raise Rechazo("paquete no autenticado: %s" % m["archivo"])
            p = json.loads(b)
            for u in p["unidades"]:
                if u["unidad"] in por:
                    raise Rechazo("unidad en dos paquetes: %s" % u["unidad"])
                por[u["unidad"]] = (p, u)
        _CACHE["paq"], _CACHE["invs"] = por, invs
    return _CACHE["paq"], _CACHE["invs"]


def original_autenticado(sel):
    """Documento y filas del ORIGINAL por la cadena de autoridad (nunca rutas dadas por la correspondencia)."""
    por, invs = paquetes()
    if sel["unidad"] not in por:
        raise Rechazo("unidad de la selección sin paquete de autoridad: %s" % sel["unidad"])
    p, u = por[sel["unidad"]]
    if p["entrega"] not in invs:
        invs[p["entrega"]] = _inv(p["entrega"], p["autoridad"]["sha256"])
    iv = invs[p["entrega"]]
    n = u["unidad"].replace(":", "_")
    rd = "%s/%s.json" % (p["carpeta_resultados"], n)
    db = (T / p["entrega"] / rd).read_bytes()
    if not (iv.get(rd) == sha(db) == u["documento_sha256"]):
        raise Rechazo("documento original no autenticado: %s" % rd)
    doc = leer_bytes(db)
    rf = "%s/%s" % (p["carpeta_resultados"], ((doc.get("filas") or {}).get("archivo") if isinstance(doc.get("filas"), dict) else None) or n + "_filas.json")
    fb = (T / p["entrega"] / rf).read_bytes() if (T / p["entrega"] / rf).exists() else None
    if fb is not None and not (iv.get(rf) == sha(fb) == u.get("filas_sha256")):
        raise Rechazo("filas originales no autenticadas: %s" % rf)
    if sel.get("entrega_original") and sel["entrega_original"] != p["entrega"]:
        raise Rechazo("la selección cita otra entrega (%s) que la autoridad (%s)" % (sel["entrega_original"], p["entrega"]))
    if sel.get("contrato") and sel["contrato"] != p["contrato"]:
        raise Rechazo("contrato de la selección distinto del paquete")
    return doc, (leer_bytes(fb) if fb is not None else {}), p["contrato"], {"entrega": p["entrega"], "doc": rd, "filas": rf if fb is not None else None,
                                                                             "doc_sha256": sha(db), "filas_sha256": sha(fb) if fb is not None else None}


# ================================================================================================ validación propia
def _tablas(F):
    return {t: v for t, v in F.items() if isinstance(v, list)}


def _uno(F, t, mot):
    rows = F.get(t) or []
    if len(rows) != 1:
        mot.append("%s: se esperaba 1 fila y hay %d" % (t, len(rows)))
        return None
    return rows[0]


def _pk(C, t):
    try:
        return list(C.C["tables"][t]["primary_key"])
    except Exception:  # noqa: BLE001
        return None


def id_celda(cc, run_id=None):
    """cell_id de Run.cell: la clave usa xi BRUTO de la grilla (último campo de external_cell_id), exportado como _dec(xi)."""
    N = nucleo()
    uk = {k: cc[k] for k in ("run_id",) + IDENT}
    if run_id is not None:
        uk["run_id"] = run_id
    xi = str(cc["external_cell_id"]).rsplit(":", 1)[-1]
    if N["dec"](xi) != cc["xi"]:
        raise Rechazo("xi exportado distinto del de external_cell_id")
    uk["xi"] = xi
    return "CEL:" + N["K"].H(uk)[:44]


def validar(doc, F, contrato, numerico, lado):
    """Validación PROPIA de una unidad (documento + filas). Devuelve la lista de motivos (vacía = válida). Nunca lanza."""
    return validar_detalle(doc, F, contrato, numerico, lado)["motivos"]


def validar_detalle(doc, F, contrato, numerico, lado):
    """{"motivos", "comprobaciones", "no_aplicables", "pendientes_productivos"}. Nunca lanza."""
    info = {"comprobaciones": ["contrato de la autoridad (esquema, PK/UK, nulos, orden)", "relaciones intrínsecas e IDs por fórmula del núcleo"],
            "no_aplicables": [], "pendientes": []}
    try:
        mot = _validar(doc, F, contrato, numerico, lado, info)
    except Exception as ex:  # noqa: BLE001  (tipo o forma inesperados: rechazo controlado)
        mot = ["%s: rechazo controlado: %s: %s" % (lado, type(ex).__name__, str(ex)[:200])]
    return {"motivos": mot, "comprobaciones": info["comprobaciones"], "no_aplicables": info["no_aplicables"],
            "pendientes_productivos": list(PENDIENTES_PRODUCTIVOS) if contrato == "v3" or not mot else list(PENDIENTES_PRODUCTIVOS)}


def _sin_modelo(td, tf):
    raise Rechazo(SIN_MODELO)


def _evidencia_v3(tabs, cc, fr, ce, cf, cid, fid, ceid, info):
    """Reglas EXISTENTES del núcleo candidato sobre la evidencia v3 de UNA unidad, sin modelo (ver cabecera)."""
    N = nucleo()
    CP, CV = N["CP"], N["CV"]
    mot = []
    menu = fr["instrument_j"]
    dom = (fr.get("structural_key_payload") or {}).get("tau_domain")
    if not isinstance(dom, dict):
        return ["frontera sin tau_domain en su carga estructural"]
    barras = (float(dom["tau_d_upper"]), float(dom["tau_f_upper"]))
    # 1. techo, testigos laterales y fila C2 de convergencia (verificar_techo); el valor del modelo en el punto queda pendiente
    if ce["instrument_available"] is True:
        e = {"menu": menu, "barras": barras, "tol_converge": N["tolc"], "contrato": "v3", "certificado": N["certificado"], "valor_en": _sin_modelo, "tol_valor": 1e-12}
        inv_, inc = CP.verificar_techo(ce, tabs, e)
        for m in inv_:
            if m == "punto del supremo no evaluable por el modelo: " + SIN_MODELO:
                info["pendientes"].append("valor del modelo en el punto del supremo")
            else:
                mot.append("verificar_techo: " + m)
        mot += ["verificar_techo (incompleto): " + m for m in inc]
        info["comprobaciones"].append("contrato_paquete.verificar_techo (dominio, laterales, testigos, fila C2: valor inicial, cota superior, error, tolerancia, cobertura, estado)")
    else:
        info["no_aplicables"].append("verificar_techo: instrumento no disponible (igual que la ruta común)")
    # 2. evidencia numérica (verificar_evidencia) en TODA unidad v3, también sin confrontación completa (p. ej. NA): la ruta común
    #    solo la aplica con confrontación completa; aquí se exige además que la evidencia de una NA concuerde con su convergencia
    K1 = cf["K_comp_1"]
    vacio = N["certificado"] and finito(K1) and finito(ce["C_2"]) and finito(ce["numerical_error"]) and K1 > ce["C_2"] + ce["numerical_error"]
    a, b = CP.verificar_evidencia(tabs, cid, ceid, {"tol_root": N["tol_root"], "vacio_demostrado": vacio})
    mot += ["verificar_evidencia: " + m for m in a + b]
    info["comprobaciones"].append("contrato_paquete.verificar_evidencia (referencia, pertenencia, método, unidad, cota, estado, huérfanas, secciones)")
    if finito(K1) and cf["computation_status"] == "complete":
        # 3. convergencia INV de las búsquedas costosas, recalculada desde sus hijas (misma llamada que verificar_inversiones)
        for row in tabs["inversion_result"]:
            iid = row["inversion_id"]
            if iid not in CP.ENDOGENAS or row["result_status"] in ("not_identified", "undefined_denominator") or row.get("reason_code") == "ENDOGENOUS_NOT_RUN" \
                    or (iid == "phi_total" and menu == "d"):
                continue
            qid = "INV:%s:%s" % (cid, iid)
            roots = sorted((x for x in tabs["scalar_inversion_roots"] if x.get("inversion_id") == iid), key=lambda x: x.get("root_index", -1))
            ivs = sorted((x for x in tabs["scalar_inversion_intervals"] if x.get("inversion_id") == iid), key=lambda x: x.get("interval_index", -1))
            ras = [(x.get("value"), x.get("bracket_low"), x.get("bracket_high"), x.get("converged")) for x in roots]
            ivv = [(x.get("lower"), x.get("upper")) for x in ivs]
            cands = [CP._c({k: CV.fila_raices(qid, CV.ref("inversion_result", {"cell_id": cid, "inversion_id": iid}), raices=ras, intervalos=ivv, coverage=cov,
                                              computation_status=row["computation_status"], no_solution=row.get("no_solution") is True, dominio=(0.0, 1.0),
                                              dominio_cubierto=(0.0, 1.0) if cov == "certified" else None, tolerancia=N["xtol"],
                                              unidad="phi" if iid == "phi_total" else "share", evidence_ref=None)[k] for k in CV.COLUMNAS if k != "evidence_ref"})
                     for cov in ("certified", "not_certified")]
            conv = [x for x in tabs["convergence_result"] if x.get("quantity_id") == qid]
            if len(conv) != 1 or CP._sin_ref(conv[0]) not in cands:
                mot.append("convergencia INV de %s distinta de la recalculada desde sus hijas (convergencia.fila_raices)" % iid)
        info["comprobaciones"].append("convergencia INV de búsquedas costosas recalculada desde sus hijas (convergencia.fila_raices)")
    else:
        info["no_aplicables"].append("convergencia INV desde hijas: confrontación no completa (igual que la ruta común)")
    # 4. Checker del núcleo (ceilings, inversions, geometry, audit) con el D7 autenticado
    try:
        orig = info.get("lado") == "original"          # paso 4 (S6): contrato y D7 del lado validado
        err = CP.checker_nucleo(N["C_hist"] if orig else N["C"], N["d7_hist"] if orig else N["d7"], CP.filas_de_celda(tabs, cid, fid, "v3"), N["TOL"])
    except Exception as x:  # noqa: BLE001
        err = ["Checker no ejecutable: %s: %s" % (type(x).__name__, str(x)[:160])]
    mot += ["Checker del núcleo: " + m for m in err[:6]]
    info["comprobaciones"].append("contrato_paquete.checker_nucleo (rules.Checker: ceilings, inversions, geometry, audit)")
    # 5. hijas de inversiones inexistentes y testigos de otro techo
    for t in ("scalar_inversion_roots", "scalar_inversion_intervals", "inversion_targets"):
        if any(x.get("inversion_id") not in N["INV"].INVERSIONS for x in tabs[t]):
            mot.append("%s de inversiones inexistentes" % t)
    return mot


def _validar(doc, F, contrato, numerico, lado, info):
    N = nucleo()
    C, CP, INV, K = (N["C_hist"] if lado == "original" else N["C"]), N["CP"], N["INV"], N["K"]     # paso 4 (S6): contrato por lado
    info["lado"] = lado
    mot = []
    if not isinstance(doc, dict) or not isinstance(F, dict) or not isinstance(doc.get("resultado"), dict):
        return ["%s: documento o filas sin estructura de objeto" % lado]
    res = doc["resultado"]
    if doc.get("contrato_exportado") not in (None, contrato):
        mot.append("contrato_exportado %r distinto del exigido %r" % (doc.get("contrato_exportado"), contrato))
    if not numerico and doc.get("estado_final") != "no_aplicable":
        mot.append("unidad no numérica de la selección sin estado_final no_aplicable")
    tabs = _tablas(F)
    esperadas = set(CP.TABLAS[contrato])
    if set(tabs) != esperadas or any(not isinstance(v, list) for v in F.values()):
        mot.append("tablas distintas de las del contrato %s (faltan %s; sobran %s)" % (contrato, sorted(esperadas - set(tabs)), sorted(set(F) - esperadas)))
        return mot
    for t in sorted(tabs):
        if any(not isinstance(r, dict) for r in tabs[t]):
            mot.append("%s: fila que no es objeto" % t)
            return mot
        e = CP.esquema(C, t, tabs[t])
        if e:
            mot.append("esquema %s: %s" % (t, e))
        pk = _pk(C, t)
        if pk:
            c = Counter(json.dumps([r.get(k) for k in pk], sort_keys=True) for r in tabs[t])
            dup = [k for k, v in c.items() if v > 1]
            if dup:
                mot.append("%s: PK duplicada %s" % (t, dup[:2]))
    for r in tabs.get("inversion_result", []):
        if "_fin" in r and not isinstance(r["_fin"], dict):
            mot.append("inversion_result._fin no es objeto")
    if mot:
        return mot                    # sin esquema válido no se interpretan relaciones (rechazo controlado)
    cc, fr, mac = _uno(F, "cell_context", mot), _uno(F, "frontier_context", mot), _uno(F, "lambda_pi_envelope", mot)
    ce, cf = _uno(F, "capture_ceiling_result", mot), _uno(F, "confrontation_result", mot)
    if mot:
        return mot
    rid = cc["run_id"]
    for t, rows in tabs.items():
        for r in rows:
            if "run_id" in r and r["run_id"] != rid:
                mot.append("%s: run_id distinto del de la celda" % t)
    # identificadores recalculados con las fórmulas del núcleo (run.py: cell, frontier, macro)
    cid = id_celda(cc)
    if cc["cell_id"] != cid:
        mot.append("cell_id no corresponde a su clave E12 (fórmula del núcleo)")
    fid = "FRN:" + K.H({"r": rid, "d": fr["design_v"], "c": fr["country_id"], "j": fr["instrument_j"], "a": fr["availability_case_id"],
                        "o": fr["omega_id"], "t": fr["tau_domain_id"]})[:40]
    if fr["frontier_id"] != fid:
        mot.append("frontier_id no corresponde a su contenido (fórmula del núcleo)")
    mid = "MAC:" + K.H({"r": rid, "c": mac["country_id"], "o": mac["omega_id"], "b": mac["eta_w_block"], "m": mac["macro_key_sha256"]})[:40]
    if mac["macro_id"] != mid:
        mot.append("macro_id no corresponde a su contenido (fórmula del núcleo)")
    ceid = "CEI:" + fid[4:]
    if ce["ceiling_id"] != ceid or ce["frontier_id"] != fid:
        mot.append("ceiling_id/frontier_id del techo no derivan de la frontera")
    if (cf["cell_id"], cf["ceiling_id"], cf["macro_id"]) != (cid, ceid, mid):
        mot.append("confrontación con referencias que no son las de la celda")
    for k in ("design_v", "country_id", "instrument_j", "availability_case_id", "omega_id"):
        if fr[k] != cc[k]:
            mot.append("frontera y celda con %s distinto" % k)
    if (mac["country_id"], mac["omega_id"], mac["eta_w_block"], mac["macro_key_sha256"], mac["national_state_sha256"]) != (
            cc["country_id"], cc["omega_id"], cc["eta_w_block"], cc["expected_macro_key_sha256"], cc["national_state_sha256"]):
        mot.append("macro y celda no casan (país, ω, bloque, clave o estado nacional)")
    for t, rows in tabs.items():
        for r in rows:
            if "cell_id" in r and r["cell_id"] != cid:
                mot.append("%s: fila de otra celda" % t)
                break
    # techo, confrontación, resumen del documento
    st, err = ce["computation_status"], ce["numerical_error"]
    if st == "complete" and not (finito(err) and 0 <= err <= TOL_CONVERGE and finito(ce["C_2"])):
        mot.append("techo complete sin certificado 0 <= numerical_error <= tol_converge")
    if cf["C_2"] != ce["C_2"]:
        mot.append("C_2 de la confrontación distinto del C_2 del techo")
    if cf["sup_not_attained"] != ce["sup_not_attained"]:
        mot.append("sup_not_attained de la confrontación distinto del techo")
    if finito(cf["G"]) or finito(cf["K_comp_1"]) or finito(cf["C_2"]):
        if not (finito(cf["G"]) and finito(cf["K_comp_1"]) and finito(cf["C_2"])):
            mot.append("G, K_comp_1 y C_2 de la confrontación incompletos")
        elif abs(cf["G"] - (cf["C_2"] - cf["K_comp_1"])) > TOL_REL * max(1.0, abs(cf["G"])):
            mot.append("G distinto de C_2 - K_comp_1")
    te, co = res.get("techo"), res.get("confrontacion")
    if numerico and (te is None or co is None):
        mot.append("unidad numérica sin resumen de techo/confrontación en el documento")
    if te is not None and (not isinstance(te, dict) or any(te.get(k, "<falta>") != ce[k] for k in ("C_2", "numerical_error", "computation_status", "reason_code", "sup_not_attained")) or set(te) != {"C_2", "numerical_error", "computation_status", "reason_code", "sup_not_attained"}):
        mot.append("resumen del documento (techo) distinto de la fila capture_ceiling_result")
    if co is not None and (not isinstance(co, dict) or any(co.get(k, "<falta>") != cf[k] for k in ("G", "K_comp_1", "verdict", "computation_status", "reason_code")) or set(co) != {"G", "K_comp_1", "verdict", "computation_status", "reason_code"}):
        mot.append("resumen del documento (confrontación) distinto de la fila confrontation_result")
    if ("cell_id" in res or numerico) and res.get("cell_id") != cid or res.get("frontier_id") != fid:
        mot.append("resumen del documento con cell_id/frontier_id distintos de las filas")
    # alcanzabilidad y testigos laterales
    sw = [r for r in tabs.get("sup_witness", []) if r.get("ceiling_id") == ceid]
    if st == "complete":
        if ce["sup_not_attained"] is False:
            if ce["sup_lateral_low"] is not None or ce["sup_lateral_high"] is not None or not finito(ce["tau_d_at_sup"]) or not finito(ce["tau_f_at_sup"]):
                mot.append("supremo alcanzado: laterales deben ser nulos y punto del supremo finito")
            if contrato == "v3" and sw:
                mot.append("supremo alcanzado con testigos laterales")
        elif ce["sup_not_attained"] is True:
            lat = [x for x in (ce["sup_lateral_low"], ce["sup_lateral_high"]) if x is not None]
            if ce["tau_d_at_sup"] is not None or ce["tau_f_at_sup"] is not None or not lat or not all(finito(x) for x in lat) or max(lat) != ce["C_2"]:
                mot.append("supremo no alcanzado: punto nulo y C_2 = máx(laterales) exigidos")
            if contrato == "v3" and not sw:
                mot.append("supremo no alcanzado sin testigos laterales (v3)")
    if len(tabs.get("sup_witness", [])) != len(sw):
        mot.append("sup_witness de otro techo")
    # inversiones
    inv = tabs.get("inversion_result", [])
    ids = [r["inversion_id"] for r in inv]
    if sorted(ids) != sorted(INV.INVERSIONS) or len(set(ids)) != len(ids):
        mot.append("inversiones %s distintas de INV.INVERSIONS" % sorted(ids))
    for r in inv:
        k = r["inversion_id"]
        if r["outside_support"] != (r["result_status"] == "outside_support"):
            mot.append("inversión %s: outside_support incoherente con result_status" % k)
        v = r.get(VALOR_INV.get(k))
        if v is not None and not finito(v):
            mot.append("inversión %s: valor no finito" % k)
        if k in CP.DOMINIO_ENDOGENO and finito(v) and not (CP.DOMINIO_ENDOGENO[k][0] <= v <= CP.DOMINIO_ENDOGENO[k][1]):
            mot.append("inversión %s: valor fuera de su dominio" % k)
        if k == "capture_required" and finito(v) and v != cf["K_comp_1"]:
            mot.append("capture_required: C_2_required distinto de K_comp_1 (EQ7_9_3)")
        if r["no_solution"] and v is not None:
            mot.append("inversión %s: no_solution con valor" % k)
        if contrato == "v3" and k in CP.ENDOGENAS:
            nr = sum(1 for x in tabs["scalar_inversion_roots"] if x.get("inversion_id") == k)
            ni = sum(1 for x in tabs["scalar_inversion_intervals"] if x.get("inversion_id") == k)
            if r["n_scalar_solutions"] is not None and r["n_scalar_solutions"] != nr:
                mot.append("inversión %s: n_scalar_solutions distinto de sus raíces" % k)
            if r["n_scalar_intervals"] is not None and r["n_scalar_intervals"] != ni:
                mot.append("inversión %s: n_scalar_intervals distinto de sus intervalos" % k)
    if contrato == "v3" and sorted(r["inversion_id"] for r in tabs["inversion_targets"]) != sorted(ids):
        mot.append("inversion_targets no corresponde a las inversiones")
    comp = ((res.get("completitud") or {}).get("partes") or {})
    for r in inv:
        p = comp.get("inversion:" + r["inversion_id"])
        if isinstance(p, dict) and (p.get("estado") == "completa") != (r["computation_status"] == "complete"):
            mot.append("completitud del documento incoherente con inversion_result %s" % r["inversion_id"])
    # R2: conteos por sección y raíces sobre la trayectoria de su sección, dentro de su encierro
    secs = {r["section_id"]: r for r in tabs.get("r2_sections", [])}
    for s, r in secs.items():
        n = sum(1 for x in tabs.get("r2_roots", []) if x["section_id"] == s)
        if r["n_roots_by_section"] is not None and r["n_roots_by_section"] != n:
            mot.append("r2_sections %s: n_roots_by_section %s y %d raíces" % (s, r["n_roots_by_section"], n))
        if r["n_roots_by_section"] is None and n:
            mot.append("r2_sections %s: raíces con conteo nulo" % s)
    for x in tabs.get("r2_roots", []):
        lo, hi, td, tf, s = x["parameter_low"], x["parameter_high"], x["tau_d_root"], x["tau_f_root"], x["section_id"]
        if not all(finito(v) for v in (lo, hi, td, tf)) or lo > hi:
            mot.append("r2_roots %s/%s: encierro o coordenadas no finitos o invertidos" % (s, x["root_index"]))
            continue
        if not (finito(x["residual"]) and x["residual"] >= 0):
            mot.append("r2_roots %s/%s: residuo inválido" % (s, x["root_index"]))
        tray = {"tau_f_0": (td, tf == 0.0), "tau_d_0": (tf, td == 0.0), "paridad": (td, td == tf), "tau_d_estatutario": (tf, True)}.get(s)
        if s not in secs or tray is None:
            mot.append("r2_roots: sección %r desconocida" % s)
        elif not tray[1] or not (lo <= tray[0] <= hi):
            mot.append("r2_roots %s/%s: raíz fuera de la trayectoria de su sección o de su encierro" % (s, x["root_index"]))
    # R1
    summ = tabs.get("r1_summary", [])
    if len(summ) > 1:
        mot.append("r1_summary con más de una fila")
    elif summ:
        s0 = summ[0]
        if s0["n_components"] is not None and s0["n_components"] != len(tabs["r1_components"]):
            mot.append("r1_summary.n_components distinto de r1_components")
        if s0["n_rejected_crossings"] is not None and s0["n_rejected_crossings"] != len(tabs["r1_rejected_crossings"]):
            mot.append("r1_summary.n_rejected_crossings distinto de r1_rejected_crossings")
    comps = {r["component_id"] for r in tabs.get("r1_components", [])}
    vert = {r["vertex_id"]: r for r in tabs.get("r1_vertices", [])}
    for r in tabs.get("r1_vertices", []):
        if r["component_id"] not in comps:
            mot.append("r1_vertices: componente inexistente")
            break
        if not (finito(r["tau_d"]) and finito(r["tau_f"]) and (r["residual"] is None or finito(r["residual"]))):
            mot.append("r1_vertices: coordenadas o residuo no finitos")
            break
    for r in tabs.get("r1_edges", []):
        a, b = vert.get(r["from_vertex_id"]), vert.get(r["to_vertex_id"])
        if a is None or b is None or a["component_id"] != r["component_id"] or b["component_id"] != r["component_id"]:
            mot.append("r1_edges %s: vértices inexistentes o de otro componente" % r["edge_id"])
            break
    # convergencia y evidencia
    for r in tabs.get("convergence_result", []):
        ref = r["result_ref"]
        m = re.fullmatch(r"([a-z_0-9]+):(\{.*\})", ref or "")
        if not m:
            mot.append("convergence_result: result_ref ilegible")
            continue
        tt, pk = m.group(1), json.loads(m.group(2))
        if not any(all(x.get(k) == v for k, v in pk.items()) for x in tabs.get(tt, [])):
            mot.append("convergence_result %s: result_ref no resuelve" % r["quantity_id"])
        if r["quantity_id"] == "C2:" + ceid and r["change_bound"] != ce["numerical_error"]:
            mot.append("fila C2 de convergencia con change_bound distinto del numerical_error del techo")
    if contrato == "v3":
        evs = {}
        for e in tabs["numerical_evidence"]:
            if e["evidence_ref"] != CP.ref_evidencia(e):
                mot.append("numerical_evidence: evidence_ref no es el hash de su contenido")
                break
            evs[e["evidence_ref"]] = e
        for r in tabs["convergence_result"]:
            if r["evidence_ref"] not in evs:
                mot.append("convergence_result %s: evidence_ref no resuelve en numerical_evidence" % r["quantity_id"])
        if not any(r["quantity_id"] == "C2:" + ceid for r in tabs["convergence_result"]) and st == "complete":
            mot.append("v3 sin fila C2 de convergencia del techo")
        if not mot:
            mot += _evidencia_v3(tabs, cc, fr, ce, cf, cid, fid, ceid, info)
    else:
        info["no_aplicables"].append("evidencia v3 (hijas, numerical_evidence, fila C2): no exportada en el contrato v2; garantía v2 limitada")
    return mot


# ================================================================================================ emparejamiento y normalización
def mapa_ids(F, lado):
    """Fichas canónicas para los identificadores que dependen de run_id (ya validados por fórmula)."""
    m = {}
    cc, fr, mac = F["cell_context"][0], F["frontier_context"][0], F["lambda_pi_envelope"][0]
    m[cc["run_id"]], m[cc["cell_id"]], m[fr["frontier_id"]], m["CEI:" + fr["frontier_id"][4:]], m[mac["macro_id"]] = "<RUN>", "<CEL>", "<FRN>", "<CEI>", "<MAC>"
    for r in F.get("convergence_result", []):
        q = normalizar(r["quantity_id"], m)
        if r["evidence_ref"] in m and m[r["evidence_ref"]] != "<NEV|%s>" % q:
            raise Rechazo("%s: evidence_ref compartida por cantidades distintas" % lado)
        m[r["evidence_ref"]] = "<NEV|%s>" % q
    for e in F.get("numerical_evidence", []):
        if e["evidence_ref"] not in m:
            m[e["evidence_ref"]] = "<NEV|%s|%s|%s|%s>" % (e["result_table"], json.dumps(normalizar(e["record_pk"], m), sort_keys=True), e["kind"], e["method_id"])
    return m


def normalizar(x, mapa):
    if isinstance(x, dict):
        return {k: normalizar(v, mapa) for k, v in x.items()}
    if isinstance(x, list):
        return [normalizar(v, mapa) for v in x]
    if isinstance(x, str):
        return IDRE.sub(lambda mm: mapa.get(mm.group(0), mm.group(0)), x)
    return x


def _ruta_campos(a, b, pref=""):
    """Rutas de los campos distintos entre dos valores (recursivo en objetos)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += _ruta_campos(a.get(k, "<ausente>"), b.get(k, "<ausente>"), pref + ("." if pref else "") + k)
        return out
    if type(a) is not type(b) or a != b:
        return [pref]
    return []


# ================================================================================================ reglas
def _ctx_reglas(Fo, Fn):
    ce_o, ce_n = Fo["capture_ceiling_result"][0], Fn["capture_ceiling_result"][0]
    eo, en = ce_o["numerical_error"], ce_n["numerical_error"]
    c2ok = (ce_o["computation_status"] == ce_n["computation_status"] == "complete" and finito(eo) and finito(en) and 0 <= eo <= TOL_CONVERGE
            and 0 <= en <= TOL_CONVERGE and finito(ce_o["C_2"]) and finito(ce_n["C_2"])
            and ce_o["C_2"] - eo <= ce_n["C_2"] + en and ce_n["C_2"] - en <= ce_o["C_2"] + eo)
    cf_o, cf_n = Fo["confrontation_result"][0], Fn["confrontation_result"][0]
    gok = (c2ok and cf_o["K_comp_1"] == cf_n["K_comp_1"] and finito(cf_o["G"]) and finito(cf_n["G"]) and abs(cf_o["G"] - cf_n["G"]) <= eo + en)
    na = all(r.get("computation_status") == "not_applicable" and r.get("reason_code") == "INSTRUMENT_NOT_AVAILABLE" for r in (cf_o, cf_n, ce_o, ce_n))         and ce_o.get("instrument_available") is False and ce_n.get("instrument_available") is False
    return {"A-C2": c2ok, "A-C2-ERR": c2ok, "A-G": gok, "_NA_MISMA_CAUSA": na}


def regla_para(tabla, campo, ro, rn, ctx, activas):
    """(id de regla que cubre y se cumple) o None. Solo reglas ACTIVAS; nunca cubre un campo que no figure en la regla."""
    for rid in activas:
        if (tabla, campo) not in REGLAS[rid]["campos"]:
            continue
        if rid in ctx:
            return rid if ctx[rid] else None
        if rid == "R-RUTA":
            if (ro.get("inversion_id") == rn.get("inversion_id") == "phi_total" and {ro.get("reason_code"), rn.get("reason_code")} <= set(RUTAS)
                    and all(ro.get(k) == rn.get(k) for k in ("computation_status", "result_status", "no_solution"))):
                return rid
            return None
        if rid == "R-SUCESION-S6":                   # DR-1 v2: solo si la sucesión técnica de ESTA unidad cumple sus condiciones
            if not (ctx.get("_DR1") or {}).get("ok"):
                return None
            if tabla == "numerical_evidence":
                return rid if campo == "definition" and RD1.definicion_equivalente(ro.get("definition"), rn.get("definition")) else None
            return rid
        if rid == "R-NA-GNA1":
            if not ctx.get("_NA_MISMA_CAUSA"):
                return None
            if tabla == "convergence_result":
                nulos = ("value_before", "value_after", "change_bound", "topology_before", "topology_after")
                ok = (str(ro.get("quantity_id", "")).startswith("G:") and ro.get("status") == "incomplete" and rn.get("status") == "not_applicable"
                      and ro.get("method_id") == "certified_bound_C2_closed_form_K1" and rn.get("method_id") == "instrument_unavailable_authenticated"
                      and all(ro.get(k) is None and rn.get(k) is None for k in nulos) and ro.get("coverage_complete") is False
                      and rn.get("coverage_complete") is False and ro.get("verdict_changes") == rn.get("verdict_changes") == 0
                      and ro.get("tolerance") == rn.get("tolerance"))
                return rid if ok else None
            if tabla == "numerical_evidence":
                ok = (all(r.get("kind") == "convergence" and r.get("status") == "limitation" and r.get("error_bound") is None for r in (ro, rn))
                      and ro.get("result_table") == rn.get("result_table") == "confrontation_result" and ro.get("record_pk") == rn.get("record_pk")
                      and ro.get("method_id") == "certified_bound_C2_closed_form_K1" and rn.get("method_id") == "instrument_unavailable_authenticated")
                return rid if ok else None
            return None
        if rid == "R-R2-ENCIERRO":
            if (ro.get("root_type") == rn.get("root_type") and all(finito(ro.get(k)) and finito(rn.get(k)) for k in ("parameter_low", "parameter_high"))
                    and ro["parameter_low"] <= rn["parameter_high"] and rn["parameter_low"] <= ro["parameter_high"]):
                return rid
            return None
    return None


# ================================================================================================ comparación de una unidad
def comparar_tablas(Fo, Fn, mo, mn, contrato_o, ctx, activas, C):
    exacto, cientifico, cubiertos, nuevas = {}, [], [], {"tablas": [], "filas": {}}
    to, tn = _tablas(Fo), _tablas(Fn)
    for t in sorted(set(to) | set(tn)):
        if t not in tn:
            cientifico.append("%s: tabla del original ausente en la nueva" % t)
            exacto[t] = ["tabla ausente en la nueva"]
            continue
        if t not in to:
            if contrato_o == "v2" and t in nucleo()["CP"].HIJAS:
                nuevas["tablas"].append(t)
            else:
                cientifico.append("%s: tabla adicional en la nueva" % t)
            exacto[t] = ["tabla solo en la nueva"]
            continue
        pk = _pk(C, t)
        def clave(r, m):
            return json.dumps(normalizar([r.get(k) for k in pk] if pk else r, m), sort_keys=True)
        ao, an = {}, {}
        for rows, m, dest in ((to[t], mo, ao), (tn[t], mn, an)):
            for r in rows:
                k = clave(r, m)
                if k in dest:
                    raise Rechazo("%s: PK duplicada tras normalizar" % t)      # nunca se colapsan duplicados
                dest[k] = normalizar(r, m)
        difs = []
        for k in sorted(set(ao) - set(an)):
            difs.append("fila solo en el original %s" % k[:120])
            cientifico.append("%s: fila del original ausente en la nueva %s" % (t, k[:120]))
        for k in sorted(set(an) - set(ao)):
            difs.append("fila solo en la nueva %s" % k[:120])
            r = an[k]
            if contrato_o == "v2" and t == "convergence_result" and str(r.get("quantity_id", "")).startswith("C2:"):
                nuevas["filas"].setdefault(t, []).append(r.get("quantity_id"))
            else:
                cientifico.append("%s: fila adicional en la nueva %s" % (t, k[:120]))
        for k in sorted(set(ao) & set(an)):
            ro, rn = ao[k], an[k]
            for campo in _ruta_campos(ro, rn):
                difs.append("%s %s" % (k[:80], campo))
                base = campo.split(".")[0]
                rid = regla_para(t, base, ro, rn, ctx, activas)
                if rid:
                    cubiertos.append({"tabla": t, "fila": k[:120], "campo": campo, "regla": rid})
                else:
                    cientifico.append("%s.%s distinto sin regla que lo cubra (fila %s)" % (t, campo, k[:100]))
        if difs:
            exacto[t] = difs[:50]
    return exacto, cientifico, cubiertos, nuevas


def comparar_doc(do, dn, mo, mn, contrato_o, ctx, activas, CP):
    exacto, cientifico, cubiertos, operativos = [], [], [], []
    for k in sorted(set(do) | set(dn)):
        if k in OPERATIVOS:
            if do.get(k) != dn.get(k):
                operativos.append(k)
            continue
        if k == "contrato_exportado" and contrato_o == "v2":
            continue          # el contrato de la corrida nueva lo fija su propia validación (v3)
        if k == "resultado":
            ro, rn = normalizar(do.get(k), mo), normalizar(dn.get(k), mn)
            for campo in _ruta_campos({c: v for c, v in (ro or {}).items() if c not in CP.DIAGNOSTICO},
                                      {c: v for c, v in (rn or {}).items() if c not in CP.DIAGNOSTICO}):
                exacto.append("resultado." + campo)
                rid = regla_para("doc", "resultado." + campo, {}, {}, ctx, activas)
                if rid:
                    cubiertos.append({"tabla": "doc", "campo": "resultado." + campo, "regla": rid})
                else:
                    cientifico.append("documento: resultado.%s distinto sin regla que lo cubra" % campo)
            for c in CP.DIAGNOSTICO:
                if (ro or {}).get(c) != (rn or {}).get(c):
                    operativos.append("resultado." + c)
            continue
        if normalizar(do.get(k), mo) != normalizar(dn.get(k), mn):
            exacto.append(k)
            cientifico.append("documento: %s distinto" % k)
    return exacto, cientifico, cubiertos, operativos


def comparar_unidad(sel, nuevo_raiz, inv_nuevo, run_id_nuevo, u, activas, registro=None):
    N = nucleo()
    C, CP = N["C"], N["CP"]
    # 1. original por la autoridad
    try:
        do, Fo, contrato_o, fuente = original_autenticado(sel)
    except (Rechazo, OSError, ValueError, KeyError) as ex:
        return {"dictamen": "no_comparable", "motivos": ["original: %s" % ex]}
    numerico = bool(sel.get("numerico", True))
    vo = validar(do, Fo, contrato_o, numerico, "original")
    if vo:
        return {"dictamen": "no_comparable", "motivos": ["el ORIGINAL autenticado no supera la validación propia: %s" % vo[:4]], "fuente_original": fuente}
    vo_det = validar_detalle(do, Fo, contrato_o, numerico, "original")
    if Fo["cell_context"][0]["cell_id"] != sel.get("cell_id_e12"):
        return {"dictamen": "no_comparable", "motivos": ["cell_id E12 de la selección distinto del original autenticado"], "fuente_original": fuente}
    # 2. nueva: autenticada por su inventario y con identidad de corrida propia
    try:
        nd, nf = (u.get("nuevo") or {}).get("doc"), (u.get("nuevo") or {}).get("filas")
        if not isinstance(nd, str) or not isinstance(nf, str):
            raise Rechazo("rutas de la corrida nueva ausentes")
        db, fb = (nuevo_raiz / nd).read_bytes(), (nuevo_raiz / nf).read_bytes()
        if inv_nuevo.get(nd) != sha(db) or inv_nuevo.get(nf) != sha(fb):
            raise Rechazo("documento o filas de la corrida nueva no autenticados por su inventario")
        dn, Fn = leer_bytes(db), leer_bytes(fb)
    except (Rechazo, OSError, ValueError) as ex:
        return {"dictamen": "corrida_nueva_invalida", "motivos": ["nueva: %s" % ex], "fuente_original": fuente}
    return comparar_cargados(sel, do, Fo, contrato_o, fuente, dn, Fn, run_id_nuevo, activas, registro=registro, bytes_nuevos=(sha(db), sha(fb)), vo_det=vo_det)


def estado_productivo(sel, registro, bytes_nuevos, numerico):
    """('verificada' | 'pendiente' | 'invalida', motivo): registro productivo LIGADO a los bytes nuevos de la unidad."""
    if registro is None or bytes_nuevos is None:
        return "pendiente", "sin registro de validación productiva ligado a los bytes nuevos"
    ent = (registro.get("unidades") or {}).get(str(sel["unidad"]))
    if not isinstance(ent, dict):
        return "pendiente", "el registro productivo no contiene esta unidad"
    if (ent.get("documento_sha256"), ent.get("filas_sha256")) != tuple(bytes_nuevos):
        return "invalida", "registro productivo ligado a OTROS bytes (sha256 de documento o filas distintos)"
    esperado = "completa_validada" if numerico else "no_aplicable_validada"
    if ent.get("estado") != esperado:
        return "invalida", "la validación productiva declara %r (se exige %r)" % (ent.get("estado"), esperado)
    return "verificada", None


def comparar_cargados(sel, do, Fo, contrato_o, fuente, dn, Fn, run_id_nuevo, activas, registro=None, bytes_nuevos=None, vo_det=None):
    """Validación propia de la nueva + identidad + comparación, con el original ya autenticado y validado."""
    N = nucleo()
    C, CP = N["C"], N["CP"]
    numerico = bool(sel.get("numerico", True))
    contrato_n = "v3"
    vn_det = validar_detalle(dn, Fn, contrato_n, numerico, "nueva")
    vo_det = vo_det or validar_detalle(do, Fo, contrato_o, numerico, "original")
    prod, prod_mot = estado_productivo(sel, registro, bytes_nuevos, numerico)
    validacion = {"original": {"estado": "valida" if not vo_det["motivos"] else "invalida", "contrato": contrato_o,
                               "garantia": "v3 (con evidencia exportada)" if contrato_o == "v3" else "v2 limitada (sin hijas ni fila C2 exportadas; no se le exige)",
                               "comprobaciones": vo_det["comprobaciones"], "no_aplicables": vo_det["no_aplicables"]},
                  "nueva": {"comun": "valida" if not vn_det["motivos"] else "invalida", "contrato": contrato_n, "comprobaciones": vn_det["comprobaciones"],
                            "no_aplicables": vn_det["no_aplicables"], "productiva": prod, "productiva_motivo": prod_mot,
                            "pendiente_de_validacion_productiva": [] if prod == "verificada" else list(PENDIENTES_PRODUCTIVOS)}}
    if vn_det["motivos"]:
        return {"dictamen": "corrida_nueva_invalida", "motivos": vn_det["motivos"][:12], "fuente_original": fuente, "validacion": validacion}
    if prod == "invalida":
        return {"dictamen": "corrida_nueva_invalida", "motivos": [prod_mot], "fuente_original": fuente, "validacion": validacion}
    out = {"fuente_original": fuente, "contrato_original": contrato_o, "validacion": validacion, "numerico": numerico}
    cco, ccn = Fo["cell_context"][0], Fn["cell_context"][0]
    if ccn["run_id"] != run_id_nuevo:
        return dict(out, dictamen="correspondencia_incorrecta", motivos=["run_id de la unidad nueva distinto del declarado para la corrida nueva"])
    if ccn["run_id"] == cco["run_id"]:
        return dict(out, dictamen="correspondencia_incorrecta", motivos=["la «corrida nueva» tiene el run_id del original: no es una corrida nueva"])
    # identidad científica
    malos = [k for k in IDENT if cco[k] != ccn[k]]
    fo, fn = Fo["frontier_context"][0], Fn["frontier_context"][0]
    malos += ["frontera." + k for k in fo if k not in ("frontier_id", "run_id") and fo[k] != fn.get(k)]
    ma, mb = Fo["lambda_pi_envelope"][0], Fn["lambda_pi_envelope"][0]
    malos += ["macro." + k for k in ("country_id", "omega_id", "eta_w_block", "macro_key_sha256", "national_state_sha256") if ma[k] != mb[k]]
    for k in ("extreme_id", "claim_id_hoja", "indice_contexto", "set_id", "omega_id", "pais", "diseno", "instrumento", "caso", "clave_estructural", "celda_externa", "estado_nacional", "macro"):
        if do["resultado"].get(k) != dn["resultado"].get(k):
            malos.append("resultado." + k)
    if do.get("id") != dn.get("id") or str(do.get("id")) != str(sel.get("unidad")):
        malos.append("id de la unidad")
    dr1 = RD1.condiciones(Fo, Fn, do, dn, N["K"]) if "R-SUCESION-S6" in activas else {"ok": False, "motivos": ["no sellada"]}
    if dr1["ok"]:                                   # DR-1 v2 (sellada): la identidad técnica S5->S6 de las cargas, por procedencia
        out["sucesion_tecnica_dr1"] = {"identidad_cubierta": sorted(set(malos) & RD1.IDENT_CUBIERTA)}
        malos = [m for m in malos if m not in RD1.IDENT_CUBIERTA]
    elif "R-SUCESION-S6" in activas:
        out["sucesion_tecnica_dr1"] = {"no_aplica": dr1["motivos"][:6]}
    if malos:
        return dict(out, dictamen="correspondencia_incorrecta", motivos=["identidad científica distinta: %s" % malos[:8]])
    try:
        mo, mn = mapa_ids(Fo, "original"), mapa_ids(Fn, "nueva")
        ctx = _ctx_reglas(Fo, Fn)
        ctx["_DR1"] = dr1
        ex_t, ci_t, cu_t, nuevas = comparar_tablas(Fo, Fn, mo, mn, contrato_o, ctx, activas, C)
        ex_d, ci_d, cu_d, op = comparar_doc(do, dn, mo, mn, contrato_o, ctx, activas, CP)
    except (Rechazo, KeyError, TypeError, ValueError) as ex:
        return dict(out, dictamen="no_comparable", motivos=["comparación: %s: %s" % (type(ex).__name__, ex)])
    diag = dict(ex_t)
    if ex_d:
        diag["doc"] = ex_d
    ci = ci_t + ci_d
    out.update(diagnostico_exacto=diag, exacto_igual=not diag, reglas_aplicadas=cu_t + cu_d, operativos_distintos=op,
               evidencia_nueva_no_atribuible_al_original=dict(nuevas, validacion_comun="valida", validacion_productiva=prod) if (nuevas["tablas"] or nuevas["filas"]) else nuevas,
               comparacion={"dictamen": "aceptada" if not ci else "discrepancia", "motivos": ci[:20]})
    if ci:
        out["dictamen"], out["motivos"] = "discrepancia", ci[:20]
    elif prod == "verificada":
        out["dictamen"], out["motivos"] = "aceptada", []
    else:
        out["dictamen"], out["motivos"] = "pendiente_validacion_productiva", ["comparación aceptada y validación común válida; falta la validación productiva: %s" % prod_mot]
    return out


def comparar(cor):
    """Entrada principal. Nunca lanza: cualquier defecto produce un rechazo controlado."""
    try:
        return _comparar(cor)
    except Exception as ex:  # noqa: BLE001
        return {"aceptado_global": False, "error_controlado": "%s: %s" % (type(ex).__name__, str(ex)[:300]), "unidades": {}, "conteo": {}, "global": {}}


def _comparar(cor):
    if not isinstance(cor, dict) or not isinstance(cor.get("unidades"), list):
        raise Rechazo("correspondencia sin lista de unidades")
    sel = seleccion(cor.get("seleccion"))
    activas = [r for r, v in REGLAS.items() if v["estado"] == "vigente"]
    selladas_malas = []
    for s in cor.get("reglas_selladas") or []:
        if isinstance(s, dict) and s.get("id") in REGLAS and REGLAS[s["id"]]["estado"] == "propuesta" and s.get("sha256") == sha_regla(s["id"]):
            activas.append(s["id"])
        else:
            selladas_malas.append(s)
    cn = cor.get("corrida_nueva") or {}
    raiz = Path(str(cn.get("raiz", "")))
    inv_raw = (raiz / "audit/entrega.json").read_bytes()
    if sha(inv_raw) != cn.get("inventario_sha256"):
        raise Rechazo("inventario de la corrida nueva distinto del declarado")
    inv_n = {r: (v["sha256"] if isinstance(v, dict) else v) for r, v in json.loads(inv_raw)["files"].items()}
    registro, reg_mot = None, None
    vp = cor.get("validacion_productiva")
    if vp is not None:
        try:
            rel = vp["archivo"]
            rb = (raiz / rel).read_bytes()
            if inv_n.get(rel) != sha(rb):
                raise Rechazo("registro productivo no autenticado por el inventario de la corrida nueva")
            reg = leer_bytes(rb)
            v_ = reg.get("validador") or {}
            vf = VALIDADORES.get(cor.get("seleccion"))
            if vf is None or (v_.get("archivo"), v_.get("sha256")) != vf or sha((A / vf[0]).read_bytes()) != vf[1]:
                raise Rechazo("registro productivo de un validador distinto del fijado")
            if vf is VALIDADOR_R3 and ((v_.get("historico") or {}).get("sha256") != VALIDADOR_R3_HISTORICO[1]
                                       or sha((A / "herramientas/b" / VALIDADOR_R3_HISTORICO[0]).read_bytes()) != VALIDADOR_R3_HISTORICO[1]):
                raise Rechazo("registro productivo R3 con un validador histórico distinto del fijado")
            g_ = reg.get("generado_por") or {}           # paso 4 (S6): el registro debe venir de la RUTA (generador instalado) con su dictamen íntegro
            if (g_.get("modulo") != GENERADOR_REGISTRO or g_.get("sha256") != sha((A / GENERADOR_REGISTRO).read_bytes())
                    or g_.get("dictamen_sha256") != sha(json.dumps(reg.get("verificacion"), sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8"))):
                raise Rechazo("registro productivo no generado por la ruta (registro_productivo.py instalado) o con dictamen alterado")
            if (any(isinstance(e_, dict) and e_.get("estado") in ("completa_validada", "no_aplicable_validada") for e_ in (reg.get("unidades") or {}).values())
                    and (reg.get("verificacion") or {}).get("cumple") is not True):
                raise Rechazo("registro productivo incoherente: unidades validadas con un dictamen del validador que no cumple")
            if not isinstance(reg.get("unidades"), dict):
                raise Rechazo("registro productivo sin unidades")
            registro = reg
        except (Rechazo, OSError, ValueError, KeyError, TypeError) as ex:
            reg_mot = "registro productivo rechazado: %s" % ex
    alc = cor.get("alcance") or {"tipo": "completa"}
    if alc.get("tipo") == "completa":
        esperadas = set(sel)
    elif alc.get("tipo") == "parcial" and isinstance(alc.get("contractuales"), list) and alc["contractuales"]:
        esperadas = set(alc["contractuales"])
        if len(esperadas) != len(alc["contractuales"]):
            raise Rechazo("alcance parcial con contractuales repetidos")
    else:
        raise Rechazo("alcance inválido")
    vistos = Counter(u.get("contractual") for u in cor["unidades"] if isinstance(u, dict))
    glob = {"seleccion": cor.get("seleccion"), "alcance": alc.get("tipo"), "fuera_de_la_seleccion": sorted(str(k) for k in (esperadas | set(vistos)) - set(sel)),
            "omisiones": sorted(esperadas & set(sel) - set(vistos)), "extras": sorted(str(k) for k in set(vistos) - esperadas),
            "duplicados_contractuales": sorted(str(k) for k, v in vistos.items() if v > 1), "reglas_activas": activas, "reglas_selladas_rechazadas": selladas_malas,
            "validacion_productiva": {"registro": vp.get("archivo") if isinstance(vp, dict) else None, "aceptado": registro is not None, "motivo_rechazo": reg_mot,
                                      "validador_fijado": dict(zip(("archivo", "sha256"), VALIDADORES.get(cor.get("seleccion")) or (None, None)))},
            "autoridad": {"seleccion_sha256": SELECCIONES[cor["seleccion"]][1], "paquetes": AUTORIDAD[:2], "contratos": nucleo()["autoridad"],
                          "corrida_nueva_inventario_sha256": cn.get("inventario_sha256")}}
    res, e12n = {}, Counter()
    for u in cor["unidades"]:
        k = u.get("contractual") if isinstance(u, dict) else None
        if not isinstance(k, str) or k not in sel:
            res[str(k)] = {"dictamen": "correspondencia_incorrecta", "motivos": ["identidad contractual que no pertenece a la selección autenticada %s" % cor.get("seleccion")]}
            continue
        if vistos[k] > 1:
            res[k] = {"dictamen": "correspondencia_incorrecta", "motivos": ["identidad contractual duplicada en la correspondencia"]}
            continue
        if k not in esperadas:
            res[k] = {"dictamen": "correspondencia_incorrecta", "motivos": ["unidad fuera del alcance declarado"]}
            continue
        try:
            r = comparar_unidad(sel[k], raiz, inv_n, cn.get("run_id"), u, activas, registro=registro)
        except Exception as ex:  # noqa: BLE001  (rechazo controlado por unidad)
            r = {"dictamen": "no_comparable", "motivos": ["error controlado: %s: %s" % (type(ex).__name__, str(ex)[:200])]}
        res[k] = r
        e12n[str((u.get("nuevo") or {}).get("doc"))] += 1
    glob["documentos_nuevos_repetidos"] = sorted(str(k) for k, v in e12n.items() if v > 1)
    for u in cor["unidades"]:              # dos unidades con el MISMO documento nuevo: ninguna se acepta
        if isinstance(u, dict) and str((u.get("nuevo") or {}).get("doc")) in glob["documentos_nuevos_repetidos"] and u.get("contractual") in res:
            res[u["contractual"]] = {"dictamen": "correspondencia_incorrecta", "motivos": ["documento nuevo asignado a más de una unidad"]}
    ok = (not glob["fuera_de_la_seleccion"] and not glob["omisiones"] and not glob["extras"] and not glob["duplicados_contractuales"]
          and not glob["documentos_nuevos_repetidos"] and not selladas_malas and reg_mot is None and res and all(v["dictamen"] == "aceptada" for v in res.values()))
    return {"global": glob, "unidades": res, "aceptado_global": bool(ok), "alcance_completo": alc.get("tipo") == "completa",
            "nota_alcance": None if alc.get("tipo") == "completa" else "alcance PARCIAL declarado: no es la comparación de la selección completa",
            "conteo": dict(Counter(v["dictamen"] for v in res.values())),
            "comparador_sha256": sha(Path(__file__).read_bytes()), "reglas": {k: dict(v, sha256=sha_regla(k)) for k, v in REGLAS.items()}}


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--despliegue" in a:
        i = a.index("--despliegue")
        configurar(a[i + 1])
        del a[i:i + 2]
    out = comparar(json.loads(Path(a[0]).read_bytes()))
    Path(a[1]).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"aceptado_global": out["aceptado_global"], "conteo": out.get("conteo"), "error": out.get("error_controlado")}, ensure_ascii=False))
